#!/usr/bin/env python3

import argparse
import csv
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_API_BASE = "https://api.openai.com/v1"
SCORE_COLUMNS = [
    "recommendation_fidelity",
    "evidence_strength_and_uncertainty_fidelity",
    "preference_sensitivity",
    "action_safety",
    "communication_clarity",
]
TEXT_COLUMNS = [
    "observed_failures",
    "evaluator_notes",
    "overall_comment",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Populate annotation_sheet.csv using an OpenAI judge model."
    )
    parser.add_argument("--run-dir", required=True, help="Run directory containing annotation_sheet.csv.")
    parser.add_argument("--model", required=True, help="OpenAI judge model name, for example gpt-5-mini.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="OpenAI API base URL.")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY", help="API key environment variable.")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of rows to judge.")
    parser.add_argument(
        "--example-id",
        action="append",
        default=[],
        help="Optional example_id to judge. Repeat the flag to target multiple rows.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite already scored rows.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without making API calls.")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Log request errors and continue with the next row instead of exiting immediately.",
    )
    parser.add_argument("--sleep-seconds", type=float, default=0.0, help="Optional delay between requests.")
    parser.add_argument("--timeout-seconds", type=int, default=120, help="Network timeout per request.")
    parser.add_argument(
        "--max-response-chars",
        type=int,
        default=500,
        help="Truncate response_text before judging to reduce timeout risk. Set 0 to disable.",
    )
    return parser.parse_args()


def load_csv_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_output_text(payload):
    if isinstance(payload.get("output_text"), str) and payload.get("output_text").strip():
        return payload["output_text"].strip()

    chunks = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content_item in item.get("content", []):
            if content_item.get("type") in ("output_text", "text"):
                text_value = content_item.get("text", "")
                if isinstance(text_value, dict):
                    text_value = text_value.get("value", "")
                if text_value:
                    chunks.append(str(text_value))
    return "\n".join(chunks).strip()


def call_openai(api_base, api_key, model, messages, timeout_seconds):
    payload = {
        "model": model,
        "input": messages,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "annotation_result",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "recommendation_fidelity": {"type": "integer", "enum": [0, 1, 2]},
                        "evidence_strength_and_uncertainty_fidelity": {"type": "integer", "enum": [0, 1, 2]},
                        "preference_sensitivity": {"type": "integer", "enum": [0, 1, 2]},
                        "action_safety": {"type": "integer", "enum": [0, 1, 2]},
                        "communication_clarity": {"type": "integer", "enum": [0, 1, 2]},
                        "observed_failures": {"type": "string"},
                        "evaluator_notes": {"type": "string"},
                        "overall_comment": {"type": "string"}
                    },
                    "required": [
                        "recommendation_fidelity",
                        "evidence_strength_and_uncertainty_fidelity",
                        "preference_sensitivity",
                        "action_safety",
                        "communication_clarity",
                        "observed_failures",
                        "evaluator_notes",
                        "overall_comment"
                    ]
                }
            }
        }
    }
    request = urllib.request.Request(
        url=api_base.rstrip("/") + "/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = response.read().decode("utf-8")
    parsed = json.loads(body)
    output_text = extract_output_text(parsed)
    if not output_text:
        raise ValueError("OpenAI response did not contain output text.")
    return json.loads(output_text)


def truncate_text(text, max_chars):
    if max_chars <= 0:
        return text
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[TRUNCATED FOR JUDGE]"


def compact_text(text, max_chars):
    compact = " ".join(text.split())
    return truncate_text(compact, max_chars)


def build_user_message(row, max_response_chars):
    fields = [
        ("source_topic", row.get("source_topic", "")),
        ("population", row.get("population", "")),
        ("grade", row.get("grade", "")),
        ("task_family", row.get("task_family", "")),
        ("user_prompt", compact_text(row.get("user_prompt", ""), 300)),
        ("expected_posture", compact_text(row.get("expected_posture", ""), 120)),
        ("required_points", compact_text(row.get("required_points", ""), 280)),
        ("forbidden_moves", compact_text(row.get("forbidden_moves", ""), 220)),
        ("response_text", compact_text(row.get("response_text", ""), max_response_chars)),
    ]
    return "\n".join(f"{name}: {value}" for name, value in fields)


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    run_dir = Path(args.run_dir).resolve()
    annotation_path = run_dir / "annotation_sheet.csv"
    judge_prompt_path = project_root / "prompts" / "judge_prompt.md"

    if not annotation_path.exists():
        raise SystemExit(f"Missing annotation_sheet.csv: {annotation_path}")
    if not judge_prompt_path.exists():
        raise SystemExit(f"Missing judge prompt: {judge_prompt_path}")

    with open(judge_prompt_path, encoding="utf-8") as handle:
        system_prompt = handle.read().strip()

    rows = load_csv_rows(annotation_path)
    todo = []
    target_ids = set(args.example_id)
    for row in rows:
        if target_ids and row.get("example_id", "") not in target_ids:
            continue
        already_scored = bool(row.get("recommendation_fidelity", "").strip())
        if already_scored and not args.overwrite:
            continue
        if not row.get("response_text", "").strip():
            continue
        todo.append(row)

    if args.limit > 0:
        todo = todo[: args.limit]

    if args.dry_run:
        print(f"Dry run: {len(todo)} rows would be judged with model {args.model}")
        return

    api_key = os.environ.get(args.api_key_env, "")
    if not api_key:
        raise SystemExit(
            f"Environment variable {args.api_key_env} is not set. "
            "Set it first or use --dry-run."
        )

    for index, row in enumerate(todo, start=1):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_message(row, args.max_response_chars)},
        ]
        try:
            judged = call_openai(
                api_base=args.api_base,
                api_key=api_key,
                model=args.model,
                messages=messages,
                timeout_seconds=args.timeout_seconds,
            )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if args.continue_on_error:
                print(
                    f"HTTP error for {row['example_id']}: {exc.code} {detail}",
                    file=sys.stderr,
                    flush=True,
                )
                continue
            raise SystemExit(f"HTTP error for {row['example_id']}: {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            if args.continue_on_error:
                print(f"Network error for {row['example_id']}: {exc}", file=sys.stderr, flush=True)
                continue
            raise SystemExit(f"Network error for {row['example_id']}: {exc}") from exc
        except (socket.timeout, TimeoutError) as exc:
            if args.continue_on_error:
                print(f"Timeout for {row['example_id']}: {exc}", file=sys.stderr, flush=True)
                continue
            raise SystemExit(f"Timeout for {row['example_id']}: {exc}") from exc

        for column in SCORE_COLUMNS + TEXT_COLUMNS:
            row[column] = str(judged.get(column, ""))

        fieldnames = rows[0].keys()
        write_csv_rows(annotation_path, rows, fieldnames)
        print(f"Judged {index}/{len(todo)}: {row['example_id']}", flush=True)

        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    print(f"Wrote judged annotations to {annotation_path}", flush=True)


if __name__ == "__main__":
    main()
