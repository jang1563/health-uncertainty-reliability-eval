#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Initialize a new run directory for a real model run.")
    parser.add_argument("--run-name", required=True, help="Name of the run directory to create.")
    parser.add_argument("--runs-root", required=True, help="Root runs directory.")
    parser.add_argument(
        "--model-template",
        default="pending_real_model",
        help="Default model_name to place in outputs.csv.",
    )
    parser.add_argument(
        "--examples",
        default="data/examples.csv",
        help="Examples CSV to seed the run with. Relative paths are resolved from project root.",
    )
    parser.add_argument(
        "--prompt-pack",
        default="data/pilot_prompt_pack.jsonl",
        help="Prompt pack JSONL to record in manifest.json. Relative paths are resolved from project root.",
    )
    return parser.parse_args()


def write_csv(path, rows, fieldnames):
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


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    runs_root = Path(args.runs_root)
    run_dir = runs_root / args.run_name
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    run_dir.mkdir(parents=True, exist_ok=False)
    examples_path = resolve_project_path(project_root, args.examples)
    prompt_pack_path = resolve_project_path(project_root, args.prompt_pack)

    if not examples_path.exists():
        raise SystemExit(f"Examples CSV not found: {examples_path}")
    if not prompt_pack_path.exists():
        raise SystemExit(f"Prompt pack JSONL not found: {prompt_pack_path}")

    manifest_template_path = project_root / "runs" / "run_manifest_template.json"
    with open(manifest_template_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["run_name"] = args.run_name
    manifest["examples_source"] = display_path(examples_path, project_root)
    manifest["prompt_pack_source"] = display_path(prompt_pack_path, project_root)

    with open(run_dir / "manifest.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    with open(examples_path, newline="", encoding="utf-8") as handle:
        examples = list(csv.DictReader(handle))

    output_rows = [
        {"example_id": row["example_id"], "model_name": args.model_template, "response_text": ""}
        for row in examples
    ]
    write_csv(run_dir / "outputs.csv", output_rows, ["example_id", "model_name", "response_text"])

    notes = [
        f"# {args.run_name}",
        "",
        "- status: `initialized`",
        "- next_step: fill `outputs.csv` with real model responses",
        f"- examples_source: `{display_path(examples_path, project_root)}`",
        f"- prompt_pack_source: `{display_path(prompt_pack_path, project_root)}`",
        "- after that: run `build_annotation_sheet.py`, annotate, then run `summarize_annotations.py`",
    ]
    (run_dir / "notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")

    print(f"Initialized run directory at {run_dir}")


if __name__ == "__main__":
    main()
