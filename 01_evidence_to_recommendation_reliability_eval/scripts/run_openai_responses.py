#!/usr/bin/env python3

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_API_BASE = "https://api.openai.com/v1"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Populate a run directory outputs.csv using the OpenAI Responses API."
    )
    parser.add_argument("--run-dir", required=True, help="Run directory containing outputs.csv and manifest.json.")
    parser.add_argument("--model", required=True, help="OpenAI model name, for example gpt-5-mini.")
    parser.add_argument(
        "--prompt-pack",
        default="",
        help="Optional override for prompt pack JSONL. Defaults to project data/pilot_prompt_pack.jsonl.",
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help="OpenAI API base URL. Defaults to https://api.openai.com/v1.",
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable name containing the API key.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of prompts to run.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite rows that already have non-empty response_text.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print what would run without making network requests.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="Optional delay between requests.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
        help="Network timeout per request.",
    )
    return parser.parse_args()


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_csv_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def resolve_project_path(project_root, raw_path):
    path = Path(raw_path)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def display_path(path, project_root):
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


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
    return output_text


def update_manifest(manifest_path, model, api_base, prompt_pack_path=None, project_root=None):
    if not manifest_path.exists():
        return
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["model_name"] = model
    manifest["provider"] = "OpenAI"
    manifest["api_base"] = api_base
    if prompt_pack_path is not None and project_root is not None:
        manifest["prompt_pack_source"] = display_path(prompt_pack_path, project_root)
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    run_dir = Path(args.run_dir).resolve()
    outputs_path = run_dir / "outputs.csv"
    manifest_path = run_dir / "manifest.json"

    manifest = {}
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as handle:
            manifest = json.load(handle)

    if args.prompt_pack:
        prompt_pack = resolve_project_path(project_root, args.prompt_pack)
    elif manifest.get("prompt_pack_source"):
        prompt_pack = resolve_project_path(project_root, manifest["prompt_pack_source"])
    else:
        prompt_pack = project_root / "data" / "pilot_prompt_pack.jsonl"

    if not outputs_path.exists():
        raise SystemExit(f"Missing outputs.csv: {outputs_path}")
    if not prompt_pack.exists():
        raise SystemExit(f"Missing prompt pack JSONL: {prompt_pack}")

    records = load_jsonl(prompt_pack)
    output_rows = load_csv_rows(outputs_path)
    output_map = {row["example_id"]: row for row in output_rows}

    todo = []
    for record in records:
        example_id = record["example_id"]
        row = output_map.get(example_id)
        if row is None:
            continue
        has_response = bool(row.get("response_text", "").strip())
        if has_response and not args.overwrite:
            continue
        todo.append((record, row))

    if args.limit > 0:
        todo = todo[: args.limit]

    if args.dry_run:
        print(f"Dry run: {len(todo)} prompts would be sent to model {args.model}")
        return

    api_key = os.environ.get(args.api_key_env, "")
    if not api_key:
        raise SystemExit(
            f"Environment variable {args.api_key_env} is not set. "
            "Set it first or use --dry-run."
        )

    update_manifest(manifest_path, args.model, args.api_base, prompt_pack, project_root)

    completed = 0
    for record, row in todo:
        try:
            response_text = call_openai(
                api_base=args.api_base,
                api_key=api_key,
                model=args.model,
                messages=record["messages"],
                timeout_seconds=args.timeout_seconds,
            )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"HTTP error for {record['example_id']}: {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise SystemExit(f"Network error for {record['example_id']}: {exc}") from exc

        row["model_name"] = args.model
        row["response_text"] = response_text
        completed += 1

        fieldnames = output_rows[0].keys() if output_rows else ["example_id", "model_name", "response_text"]
        write_csv_rows(outputs_path, output_rows, fieldnames)

        print(f"Completed {completed}/{len(todo)}: {record['example_id']}")
        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    print(f"Wrote outputs to {outputs_path}")


if __name__ == "__main__":
    main()
