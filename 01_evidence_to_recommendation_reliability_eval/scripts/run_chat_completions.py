#!/usr/bin/env python3

"""Populate outputs.csv for a run using any OpenAI-compatible Chat Completions endpoint.

Tested providers: DeepSeek (https://api.deepseek.com/v1), Together
(https://api.together.xyz/v1), Groq (https://api.groq.com/openai/v1),
and OpenAI's own /chat/completions endpoint.

This is the sibling of run_openai_responses.py for providers that do not
expose the OpenAI /responses endpoint.
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Populate a run directory outputs.csv using an OpenAI-compatible Chat Completions endpoint."
    )
    parser.add_argument("--run-dir", required=True, help="Run directory containing outputs.csv and manifest.json.")
    parser.add_argument("--model", required=True, help="Model name as recognized by the provider.")
    parser.add_argument(
        "--provider",
        default="OpenAI-compatible",
        help="Provider display name recorded in manifest.json.",
    )
    parser.add_argument(
        "--prompt-pack",
        default="",
        help="Optional override for prompt pack JSONL. Defaults to the prompt_pack_source in manifest.json.",
    )
    parser.add_argument(
        "--api-base",
        required=True,
        help="Base URL for the chat-completions endpoint, e.g. https://api.deepseek.com/v1.",
    )
    parser.add_argument(
        "--api-key-env",
        required=True,
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
    parser.add_argument("--sleep-seconds", type=float, default=0.0, help="Optional delay between requests.")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="Network timeout per request.")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=0,
        help="Optional max_tokens value to send. 0 omits the field.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Optional temperature. If omitted, the provider default is used.",
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


def extract_chat_text(payload):
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("value") or ""
                if isinstance(text, str) and text:
                    chunks.append(text)
        return "\n".join(chunks).strip()
    return ""


def call_chat_completions(api_base, api_key, model, messages, timeout_seconds, max_tokens, temperature):
    payload = {
        "model": model,
        "messages": messages,
    }
    if max_tokens and max_tokens > 0:
        payload["max_tokens"] = max_tokens
    if temperature is not None:
        payload["temperature"] = temperature
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
    output_text = extract_chat_text(parsed)
    if not output_text:
        raise ValueError(f"Provider response did not contain message content: {body[:500]}")
    return output_text


def update_manifest(manifest_path, model, provider, api_base, prompt_pack_path=None, project_root=None):
    if not manifest_path.exists():
        return
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["model_name"] = model
    manifest["provider"] = provider
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
        print(f"Dry run: {len(todo)} prompts would be sent to model {args.model} via {args.api_base}")
        return

    api_key = os.environ.get(args.api_key_env, "")
    if not api_key:
        raise SystemExit(
            f"Environment variable {args.api_key_env} is not set. Set it first or use --dry-run."
        )

    update_manifest(manifest_path, args.model, args.provider, args.api_base, prompt_pack, project_root)

    completed = 0
    failed = []
    for record, row in todo:
        try:
            response_text = call_chat_completions(
                api_base=args.api_base,
                api_key=api_key,
                model=args.model,
                messages=record["messages"],
                timeout_seconds=args.timeout_seconds,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"HTTP error for {record['example_id']}: {exc.code} {detail[:300]}", file=sys.stderr)
            failed.append(record["example_id"])
            continue
        except urllib.error.URLError as exc:
            print(f"Network error for {record['example_id']}: {exc}", file=sys.stderr)
            failed.append(record["example_id"])
            continue
        except Exception as exc:
            print(f"Unexpected error for {record['example_id']}: {exc}", file=sys.stderr)
            failed.append(record["example_id"])
            continue

        row["model_name"] = args.model
        row["response_text"] = response_text
        completed += 1

        fieldnames = output_rows[0].keys() if output_rows else ["example_id", "model_name", "response_text"]
        write_csv_rows(outputs_path, output_rows, fieldnames)

        print(f"Completed {completed}/{len(todo)}: {record['example_id']}")
        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    print(f"Wrote outputs to {outputs_path}")
    if failed:
        print(f"Failed example_ids ({len(failed)}): {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
