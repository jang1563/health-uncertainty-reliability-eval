#!/usr/bin/env python3
"""
Drug Safety Update Sensitivity Eval — Evaluation Runner

Loads benchmark items, prompts a target model twice per item (before + after),
collects response pairs, then scores them using a judge model.

Usage:
    python eval/run_eval.py --model claude-sonnet-4-20250514 --judge claude-sonnet-4-20250514
    python eval/run_eval.py --model gpt-4o --judge claude-sonnet-4-20250514 --items 18  # pilot only
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from eval.scoring import score_response_pair
from eval.prompts import build_system_prompt, build_user_message
from eval.run_metadata import (
    build_run_manifest,
    compute_case_id_hash_from_items,
    write_run_manifest,
)


def load_benchmark_items(jsonl_path, max_items=None):
    """Load benchmark items from JSONL file, skipping metadata line."""
    items = []
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "_meta" in obj:
                continue
            items.append(obj)
            if max_items and len(items) >= max_items:
                break
    return items


def call_model(model_name, system_prompt, user_message, api_key=None):
    """Call a model API and return the response text.

    Supports 'anthropic' (Claude) and 'openai' (GPT) providers.
    Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables.
    """
    if model_name.startswith("claude") or model_name.startswith("anthropic"):
        return _call_anthropic(model_name, system_prompt, user_message, api_key)
    elif model_name.startswith("gpt") or model_name.startswith("o1") or model_name.startswith("o3"):
        return _call_openai(model_name, system_prompt, user_message, api_key)
    else:
        raise ValueError(f"Unknown model provider for: {model_name}. Use claude-* or gpt-* prefix.")


def _call_anthropic(model_name, system_prompt, user_message, api_key=None):
    try:
        import anthropic
    except ImportError:
        raise ImportError("pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=model_name,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _call_openai(model_name, system_prompt, user_message, api_key=None):
    try:
        import openai
    except ImportError:
        raise ImportError("pip install openai")

    client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    request_args = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    if model_name.startswith("gpt-5"):
        request_args["reasoning_effort"] = "minimal"

    try:
        response = client.chat.completions.create(
            max_tokens=2048,
            **request_args,
        )
    except openai.BadRequestError as exc:
        error_message = str(exc)
        if "max_completion_tokens" not in error_message:
            raise
        response = client.chat.completions.create(
            max_completion_tokens=2048,
            **request_args,
        )
    return _extract_openai_message_content(response.choices[0].message)


def _extract_openai_message_content(message):
    """Normalize OpenAI message content across SDK/model variants."""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return content or ""

    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
            continue
        if isinstance(block, dict):
            if block.get("type") in {"output_text", "text"} and block.get("text"):
                parts.append(block["text"])
            continue

        block_type = getattr(block, "type", None)
        text = getattr(block, "text", None)
        if block_type in {"output_text", "text"} and text:
            parts.append(text)

    return "".join(parts)


def run_eval(model_name, judge_model, items, output_dir, delay=1.0):
    """Run the full evaluation pipeline."""
    results = []
    total = len(items)
    dataset_case_id_hash = compute_case_id_hash_from_items(items)

    for i, item in enumerate(items):
        case_id = item["case_id"]
        print(f"[{i+1}/{total}] {case_id}")

        # Build prompts
        before_system = build_system_prompt(item["before_packet"])
        after_system = build_system_prompt(item["after_packet"])
        user_msg = build_user_message(item["user_question"])

        # Get model responses
        print(f"  Calling model (before)...")
        before_response = call_model(model_name, before_system, user_msg)
        time.sleep(delay)

        print(f"  Calling model (after)...")
        after_response = call_model(model_name, after_system, user_msg)
        time.sleep(delay)

        # Score the response pair
        print(f"  Scoring with judge...")
        scores = score_response_pair(
            judge_model=judge_model,
            item=item,
            before_response=before_response,
            after_response=after_response,
            call_model_fn=call_model,
        )
        time.sleep(delay)

        result = {
            "case_id": case_id,
            "drug_name": item["drug_name"],
            "section_changed": item["section_changed"],
            "update_direction": item["update_direction"],
            "severity_tier": item["severity_tier"],
            "prompt_variant": item["prompt_variant"],
            "model_name": model_name,
            "judge_model": judge_model,
            "dataset_item_count": total,
            "dataset_case_id_hash": dataset_case_id_hash,
            "before_response": before_response,
            "after_response": after_response,
            "scores": scores,
        }
        results.append(result)

        # Save incrementally
        output_path = os.path.join(output_dir, "eval_results.jsonl")
        with open(output_path, "a") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        print(f"  Scores: {scores}")

    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Drug Safety Update Sensitivity Eval Runner")
    parser.add_argument("--model", required=True, help="Target model to evaluate (e.g., claude-sonnet-4-20250514)")
    parser.add_argument("--judge", required=True, help="Judge model for scoring (e.g., claude-sonnet-4-20250514)")
    parser.add_argument("--data", default=str(PROJECT_ROOT / "data" / "benchmark_items.jsonl"), help="Path to JSONL")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "eval" / "output"), help="Output directory")
    parser.add_argument("--report-path", default=None, help="Optional explicit markdown report path")
    parser.add_argument("--figures-dir", default=None, help="Optional explicit directory for generated figures")
    parser.add_argument("--items", type=int, default=None, help="Max items to evaluate (for testing)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls in seconds")
    args = parser.parse_args(argv)

    os.makedirs(args.output, exist_ok=True)

    # Clear previous results
    output_path = os.path.join(args.output, "eval_results.jsonl")
    if os.path.exists(output_path):
        os.remove(output_path)

    items = load_benchmark_items(args.data, max_items=args.items)
    print(f"Loaded {len(items)} benchmark items")
    print(f"Target model: {args.model}")
    print(f"Judge model: {args.judge}")
    print()

    from eval.report_generator import resolve_artifact_paths
    report_path, figures_dir = resolve_artifact_paths(
        output_dir=args.output,
        report_path=args.report_path,
        figures_dir=args.figures_dir,
    )
    manifest = build_run_manifest(
        model_name=args.model,
        judge_model=args.judge,
        data_path=args.data,
        items=items,
        output_dir=args.output,
        report_path=report_path,
        figures_dir=figures_dir,
    )
    manifest_path = write_run_manifest(args.output, manifest)
    print(f"Run manifest saved to: {manifest_path}")

    results = run_eval(args.model, args.judge, items, args.output, delay=args.delay)

    print(f"\nEvaluation complete. {len(results)} items scored.")
    print(f"Results saved to: {output_path}")

    # Generate report
    from eval.report_generator import generate_report
    generate_report(results, report_path, figures_dir, model_name=args.model)
    print(f"Report saved to: {report_path}")
    print(f"Figures saved to: {figures_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
