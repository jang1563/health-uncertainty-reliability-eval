#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path


REQUIRED_COLUMNS = [
    "example_id",
    "source_topic",
    "population",
    "grade",
    "release_date",
    "task_family",
    "user_prompt",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export benchmark rows to a JSONL prompt pack for model runs."
    )
    parser.add_argument("--examples", required=True, help="Path to examples CSV.")
    parser.add_argument("--output", required=True, help="Path to output JSONL prompt pack.")
    parser.add_argument(
        "--system-prompt",
        default="",
        help="Optional path to a system prompt Markdown or text file.",
    )
    return parser.parse_args()


def read_examples(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_system_prompt(path):
    if not path:
        return ""
    with open(path, encoding="utf-8") as handle:
        return handle.read().strip()


def validate_columns(rows):
    if not rows:
        raise ValueError("examples CSV has no rows.")
    header = set(rows[0].keys())
    missing = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing:
        raise ValueError(f"examples CSV is missing required columns: {', '.join(missing)}")


def build_messages(system_prompt, user_prompt):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return messages


def main():
    args = parse_args()
    rows = read_examples(args.examples)
    validate_columns(rows)
    system_prompt = load_system_prompt(args.system_prompt)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as handle:
        for row in rows:
            record = {
                "example_id": row["example_id"],
                "messages": build_messages(system_prompt, row["user_prompt"]),
                "metadata": {
                    "source_topic": row["source_topic"],
                    "population": row["population"],
                    "grade": row["grade"],
                    "release_date": row["release_date"],
                    "task_family": row["task_family"],
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} prompt records to {output_path}")


if __name__ == "__main__":
    main()
