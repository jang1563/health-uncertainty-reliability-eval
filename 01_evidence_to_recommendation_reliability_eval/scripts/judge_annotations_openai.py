#!/usr/bin/env python3

import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from e2r_metrics import SCORE_COLUMNS, load_json, parse_score, read_csv_rows, split_failures, write_csv_rows, write_json


DEFAULT_API_BASE = "https://api.openai.com/v1"
TEXT_COLUMNS = [
    "observed_failures",
    "evaluator_notes",
    "overall_comment",
]
REQUIRED_OUTPUT_TEXT_COLUMNS = [
    "observed_failures",
    "evaluator_notes",
]
REQUIRED_INPUT_COLUMNS = [
    "grade",
    "task_family",
    "user_prompt",
    "expected_posture",
    "required_points",
    "forbidden_moves",
    "response_text",
]
SUPPORTED_REQUEST_APIS = ("auto", "responses", "chat_completions")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Populate an annotation or adjudication CSV using an OpenAI-compatible judge model."
    )
    location_group = parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument("--run-dir", help="Run directory containing annotation_sheet.csv.")
    location_group.add_argument("--input-csv", help="CSV to score in-place or copy to --output-csv.")
    parser.add_argument("--output-csv", help="Optional output CSV path. Defaults to the input CSV.")
    parser.add_argument("--metadata-path", help="Path to write judge metadata JSON.")
    parser.add_argument("--model", required=True, help="Judge model name, for example gpt-5-mini.")
    parser.add_argument("--judge-role", default="primary", help="Label written into judge metadata.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="OpenAI-compatible API base URL.")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY", help="API key environment variable.")
    parser.add_argument(
        "--request-api",
        choices=SUPPORTED_REQUEST_APIS,
        default="auto",
        help="Transport surface to use. `auto` picks chat-completions for Anthropic compatibility and responses elsewhere.",
    )
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
        "--fallback-max-response-chars",
        type=int,
        default=500,
        help="Fallback truncation length if the full-response attempt fails. Set 0 to disable fallback.",
    )
    parser.add_argument(
        "--max-response-chars",
        type=int,
        default=None,
        help="Deprecated alias for --fallback-max-response-chars.",
    )
    return parser.parse_args()


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


def extract_chat_completion_text(payload):
    choices = payload.get("choices", [])
    if not choices:
        raise ValueError("Chat completion response did not contain choices.")
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in ("text", "output_text"):
                text_value = item.get("text", "")
                if isinstance(text_value, dict):
                    text_value = text_value.get("value", "")
                if text_value:
                    chunks.append(str(text_value))
        return "\n".join(chunks).strip()
    return str(content).strip()


def strip_json_fences(text):
    candidate = (text or "").strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    return candidate


def parse_judge_json(text):
    candidate = strip_json_fences(text)
    if not candidate:
        raise ValueError("Judge response did not contain text.")
    return json.loads(candidate)


def determine_request_api(api_base, request_api):
    if request_api != "auto":
        return request_api
    if "anthropic.com" in api_base:
        return "chat_completions"
    return "responses"


def request_api_candidates(api_base, request_api):
    primary = determine_request_api(api_base, request_api)
    if request_api != "auto":
        return [primary]
    alternate = "chat_completions" if primary == "responses" else "responses"
    return [primary, alternate]


def build_system_prompt(system_prompt, request_api):
    if request_api == "chat_completions":
        return (
            system_prompt
            + "\n\nReturn only a single JSON object with exactly these keys: "
            + ", ".join(SCORE_COLUMNS + TEXT_COLUMNS)
            + ". Use integers 0, 1, or 2 for the five score fields. "
            "Use plain strings for observed_failures, evaluator_notes, and overall_comment. "
            "Do not wrap the JSON in Markdown fences."
        )
    return system_prompt


def call_responses_api(api_base, api_key, model, messages, timeout_seconds):
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
                        "overall_comment": {"type": "string"},
                    },
                    "required": SCORE_COLUMNS + TEXT_COLUMNS,
                },
            }
        },
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
        raise ValueError("Judge response did not contain output text.")
    return json.loads(output_text)


def call_chat_completions(api_base, api_key, model, messages, timeout_seconds):
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1200,
        "temperature": 0,
    }
    request = urllib.request.Request(
        url=api_base.rstrip("/") + "/chat/completions",
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
    output_text = extract_chat_completion_text(parsed)
    return parse_judge_json(output_text)


def call_openai(api_base, api_key, model, messages, timeout_seconds, request_api):
    last_error = None
    for candidate in request_api_candidates(api_base, request_api):
        try:
            if candidate == "responses":
                return (
                    call_responses_api(
                        api_base=api_base,
                        api_key=api_key,
                        model=model,
                        messages=messages,
                        timeout_seconds=timeout_seconds,
                    ),
                    candidate,
                )
            if candidate == "chat_completions":
                return (
                    call_chat_completions(
                        api_base=api_base,
                        api_key=api_key,
                        model=model,
                        messages=messages,
                        timeout_seconds=timeout_seconds,
                    ),
                    candidate,
                )
            raise ValueError(f"Unsupported request_api: {candidate}")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if request_api == "auto" and exc.code in {404, 405}:
                continue
            raise
    if last_error is not None:
        raise last_error
    raise ValueError("No request API candidates were available.")


def truncate_text(text, max_chars):
    if max_chars <= 0:
        return text
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[TRUNCATED FOR JUDGE]"


def compact_text(text, max_chars):
    compact = " ".join((text or "").split())
    return truncate_text(compact, max_chars)


def build_user_message(row, response_max_chars=0):
    fields = [
        ("source_topic", row.get("source_topic", "")),
        ("population", row.get("population", "")),
        ("grade", row.get("grade", "")),
        ("task_family", row.get("task_family", "")),
        ("user_prompt", compact_text(row.get("user_prompt", ""), 300)),
        ("expected_posture", compact_text(row.get("expected_posture", ""), 160)),
        ("required_points", compact_text(row.get("required_points", ""), 600)),
        ("forbidden_moves", compact_text(row.get("forbidden_moves", ""), 320)),
        ("response_text", compact_text(row.get("response_text", ""), response_max_chars)),
    ]
    return "\n".join(f"{name}: {value}" for name, value in fields)


def row_identifier(row):
    return row.get("adjudication_id") or row.get("example_id") or "<unknown>"


def row_is_fully_scored(row):
    try:
        return all(parse_score(row.get(column, "")) is not None for column in SCORE_COLUMNS)
    except ValueError:
        return False


def row_matches_target_ids(row, target_ids):
    if not target_ids:
        return True
    return row.get("example_id", "") in target_ids or row.get("adjudication_id", "") in target_ids


def validate_judged_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Judge response must be a JSON object.")

    validated = {}
    missing = []
    for column in SCORE_COLUMNS:
        if column not in payload:
            missing.append(column)
            continue
        validated[column] = parse_score(payload.get(column))
    for column in TEXT_COLUMNS:
        if column not in payload:
            missing.append(column)
            continue
        value = payload.get(column)
        validated[column] = "" if value is None else str(value)

    if missing:
        raise ValueError("Judge response is missing required keys: " + ", ".join(missing))
    return validated


def validate_input_rows(rows):
    if not rows:
        raise SystemExit("Input CSV has no rows.")
    header = set(rows[0].keys())
    missing = [column for column in REQUIRED_INPUT_COLUMNS if column not in header]
    if missing:
        raise SystemExit(f"Input CSV is missing required columns: {', '.join(missing)}")
    score_missing = [column for column in SCORE_COLUMNS + REQUIRED_OUTPUT_TEXT_COLUMNS if column not in header]
    if score_missing:
        raise SystemExit(
            "Input CSV must already contain scoring columns: " + ", ".join(score_missing)
        )


def resolve_paths(args):
    project_root = Path(__file__).resolve().parent.parent
    if args.run_dir:
        run_dir = Path(args.run_dir).resolve()
        input_csv = run_dir / "annotation_sheet.csv"
        output_csv = Path(args.output_csv).resolve() if args.output_csv else input_csv
        metadata_path = (
            Path(args.metadata_path).resolve()
            if args.metadata_path
            else run_dir / "judge_metadata.json"
        )
    else:
        run_dir = None
        input_csv = Path(args.input_csv).resolve()
        output_csv = Path(args.output_csv).resolve() if args.output_csv else input_csv
        metadata_path = (
            Path(args.metadata_path).resolve()
            if args.metadata_path
            else input_csv.with_name(input_csv.stem + "_judge_metadata.json")
        )
    judge_prompt_path = project_root / "prompts" / "judge_prompt.md"
    if not input_csv.exists():
        raise SystemExit(f"Missing input CSV: {input_csv}")
    if not judge_prompt_path.exists():
        raise SystemExit(f"Missing judge prompt: {judge_prompt_path}")
    return project_root, run_dir, input_csv, output_csv, metadata_path, judge_prompt_path


def load_system_prompt(judge_prompt_path):
    with open(judge_prompt_path, encoding="utf-8") as handle:
        return handle.read().strip()


def select_rows_to_judge(rows, example_ids=None, overwrite=False, limit=0):
    target_ids = set(example_ids or [])
    todo = []
    for row in rows:
        if not row_matches_target_ids(row, target_ids):
            continue
        already_scored = row_is_fully_scored(row)
        if already_scored and not overwrite:
            continue
        if not str(row.get("response_text", "")).strip():
            continue
        todo.append(row)

    if limit > 0:
        todo = todo[:limit]
    return todo


def judge_row(
    row,
    system_prompt,
    api_base,
    api_key,
    model,
    timeout_seconds,
    fallback_max_response_chars,
    request_api="auto",
):
    response_text = row.get("response_text", "")
    compact_response = " ".join(str(response_text or "").split())
    metadata = {
        "row_id": row_identifier(row),
        "example_id": row.get("example_id", ""),
        "adjudication_id": row.get("adjudication_id", ""),
        "input_response_chars": len(response_text),
        "input_response_chars_compact": len(compact_response),
        "attempts": [],
        "status": "pending",
        "request_api": determine_request_api(api_base, request_api),
    }

    attempts = [
        ("full_response", 0),
    ]
    if fallback_max_response_chars and len(compact_response) > fallback_max_response_chars:
        attempts.append(("fallback_truncated", fallback_max_response_chars))

    last_error = None
    for request_mode, max_chars in attempts:
        message = build_user_message(row, response_max_chars=max_chars)
        prompt_request_api = (
            "chat_completions"
            if request_api == "auto"
            else determine_request_api(api_base, request_api)
        )
        metadata["attempts"].append(
            {
                "request_mode": request_mode,
                "response_chars_used": len(compact_text(response_text, max_chars)),
                "truncated": max_chars > 0 and len(compact_response) > max_chars,
            }
        )
        try:
            judged, used_request_api = call_openai(
                api_base=api_base,
                api_key=api_key,
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": build_system_prompt(system_prompt, prompt_request_api),
                    },
                    {"role": "user", "content": message},
                ],
                timeout_seconds=timeout_seconds,
                request_api=request_api,
            )
            judged = validate_judged_payload(judged)
            metadata["status"] = "scored" if request_mode == "full_response" else "fallback_truncated"
            metadata["request_mode"] = request_mode
            metadata["input_truncated"] = request_mode != "full_response"
            metadata["request_api"] = used_request_api
            return judged, metadata
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError, ValueError) as exc:
            last_error = exc
            metadata["attempts"][-1]["error"] = str(exc)

    metadata["status"] = "failed"
    metadata["request_mode"] = attempts[-1][0]
    metadata["input_truncated"] = metadata["request_mode"] != "full_response"
    raise last_error


def judge_csv(
    *,
    input_csv,
    output_csv,
    metadata_path,
    judge_prompt_path,
    run_dir,
    model,
    judge_role,
    api_base,
    api_key_env,
    example_ids=None,
    limit=0,
    overwrite=False,
    dry_run=False,
    continue_on_error=False,
    sleep_seconds=0.0,
    timeout_seconds=120,
    fallback_max_response_chars=500,
    request_api="auto",
):
    rows = read_csv_rows(input_csv)
    validate_input_rows(rows)
    system_prompt = load_system_prompt(judge_prompt_path)
    todo = select_rows_to_judge(
        rows,
        example_ids=example_ids,
        overwrite=overwrite,
        limit=limit,
    )

    if dry_run:
        print(f"Dry run: {len(todo)} rows would be judged with model {model}")
        print(f"Input CSV: {input_csv}")
        print(f"Output CSV: {output_csv}")
        print(f"Metadata path: {metadata_path}")
        return {
            "input_csv": str(input_csv),
            "output_csv": str(output_csv),
            "run_dir": str(run_dir) if run_dir else None,
            "judge_prompt_path": str(judge_prompt_path),
            "judge_model": model,
            "judge_role": judge_role,
            "api_base": api_base,
            "api_key_env": api_key_env,
            "primary_mode": "full_response",
            "fallback_max_response_chars": fallback_max_response_chars,
            "status_counts": {},
            "rows": [],
        }

    if not todo:
        print("No rows selected for judging.", flush=True)
        return {
            "input_csv": str(input_csv),
            "output_csv": str(output_csv),
            "run_dir": str(run_dir) if run_dir else None,
            "judge_prompt_path": str(judge_prompt_path),
            "judge_model": model,
            "judge_role": judge_role,
            "api_base": api_base,
            "api_key_env": api_key_env,
            "primary_mode": "full_response",
            "fallback_max_response_chars": fallback_max_response_chars,
            "status_counts": {},
            "rows": [],
        }

    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        raise SystemExit(
            f"Environment variable {api_key_env} is not set. "
            "Set it first or use --dry-run."
        )

    output_rows = list(rows)
    for row in output_rows:
        for column in TEXT_COLUMNS:
            row.setdefault(column, "")
    by_identifier = {row_identifier(row): row for row in output_rows}
    metadata_rows = []
    status_counts = {}

    for index, row in enumerate(todo, start=1):
        row_id = row_identifier(row)
        try:
            judged, row_metadata = judge_row(
                row=row,
                system_prompt=system_prompt,
                api_base=api_base,
                api_key=api_key,
                model=model,
                timeout_seconds=timeout_seconds,
                fallback_max_response_chars=fallback_max_response_chars,
                request_api=request_api,
            )
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError, ValueError) as exc:
            if continue_on_error:
                row_metadata = {
                    "row_id": row_id,
                    "example_id": row.get("example_id", ""),
                    "adjudication_id": row.get("adjudication_id", ""),
                    "status": "failed",
                    "request_mode": "full_response",
                    "input_response_chars": len(row.get("response_text", "")),
                    "input_truncated": False,
                    "attempts": [{"request_mode": "full_response", "error": str(exc)}],
                }
                metadata_rows.append(row_metadata)
                status_counts[row_metadata["status"]] = status_counts.get(row_metadata["status"], 0) + 1
                print(f"Judge error for {row_id}: {exc}", file=sys.stderr, flush=True)
                continue
            raise SystemExit(f"Judge error for {row_id}: {exc}") from exc

        target_row = by_identifier[row_id]
        for column in SCORE_COLUMNS + TEXT_COLUMNS:
            target_row[column] = str(judged.get(column, ""))
        metadata_rows.append(row_metadata)
        status_counts[row_metadata["status"]] = status_counts.get(row_metadata["status"], 0) + 1

        fieldnames = list(output_rows[0].keys())
        write_csv_rows(output_csv, output_rows, fieldnames)
        print(f"Judged {index}/{len(todo)}: {row_id} ({row_metadata['status']})", flush=True)

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    metadata = {
        "input_csv": str(input_csv),
        "output_csv": str(output_csv),
        "run_dir": str(run_dir) if run_dir else None,
        "judge_prompt_path": str(judge_prompt_path),
        "judge_model": model,
        "judge_role": judge_role,
        "api_base": api_base,
        "api_key_env": api_key_env,
        "request_api": determine_request_api(api_base, request_api),
        "primary_mode": "full_response",
        "fallback_max_response_chars": fallback_max_response_chars,
        "status_counts": status_counts,
        "rows": metadata_rows,
    }
    write_json(metadata_path, metadata)

    print(f"Wrote judged annotations to {output_csv}", flush=True)
    print(f"Wrote judge metadata to {metadata_path}", flush=True)
    return metadata


def main():
    args = parse_args()
    if args.max_response_chars is not None:
        args.fallback_max_response_chars = args.max_response_chars

    _, run_dir, input_csv, output_csv, metadata_path, judge_prompt_path = resolve_paths(args)
    judge_csv(
        input_csv=input_csv,
        output_csv=output_csv,
        metadata_path=metadata_path,
        judge_prompt_path=judge_prompt_path,
        run_dir=run_dir,
        model=args.model,
        judge_role=args.judge_role,
        api_base=args.api_base,
        api_key_env=args.api_key_env,
        example_ids=args.example_id,
        limit=args.limit,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        continue_on_error=args.continue_on_error,
        sleep_seconds=args.sleep_seconds,
        timeout_seconds=args.timeout_seconds,
        fallback_max_response_chars=args.fallback_max_response_chars,
        request_api=args.request_api,
    )


if __name__ == "__main__":
    main()
