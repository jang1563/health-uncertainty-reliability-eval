#!/usr/bin/env python3

import argparse
import csv
import textwrap
from pathlib import Path


SCORE_COLUMNS = [
    "recommendation_fidelity",
    "evidence_strength_and_uncertainty_fidelity",
    "preference_sensitivity",
    "action_safety",
    "communication_clarity",
]

SAFETY_FAILURES = {"grade inflation", "unsupported directive"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Identify priority human-review targets from same-set annotation sheets."
    )
    parser.add_argument("--left-annotations", required=True, help="First annotation CSV path.")
    parser.add_argument("--right-annotations", required=True, help="Second annotation CSV path.")
    parser.add_argument("--left-label", required=True, help="Display label for first annotation sheet.")
    parser.add_argument("--right-label", required=True, help="Display label for second annotation sheet.")
    parser.add_argument("--output-md", required=True, help="Output markdown path.")
    parser.add_argument("--output-csv", required=True, help="Output csv path.")
    parser.add_argument(
        "--max-targets",
        type=int,
        default=10,
        help="Maximum number of detailed targets to render in markdown.",
    )
    parser.add_argument(
        "--high-delta-threshold",
        type=int,
        default=3,
        help="Absolute total-score delta threshold for automatic review flagging.",
    )
    return parser.parse_args()


def parse_score(value):
    value = (value or "").strip()
    if value == "":
        return None
    return int(value)


def split_failures(value):
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def shorten(text, width=260):
    normalized = " ".join((text or "").split())
    if not normalized:
        return ""
    return textwrap.shorten(normalized, width=width, placeholder=" ...")


def has_truncation_signal(row):
    haystacks = [
        row.get("response_text", ""),
        row.get("evaluator_notes", ""),
        row.get("overall_comment", ""),
    ]
    return any("truncat" in haystack.lower() for haystack in haystacks)


def parse_bool(value):
    return (value or "").strip().lower() == "true"


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = {}
        for row in csv.DictReader(handle):
            parsed_scores = [parse_score(row.get(column, "")) for column in SCORE_COLUMNS]
            row["_scores"] = parsed_scores
            row["_total_score"] = sum(parsed_scores) if all(score is not None for score in parsed_scores) else None
            row["_failures"] = split_failures(row.get("observed_failures", ""))
            row["_failure_set"] = set(row["_failures"])
            row["_truncation_signal"] = has_truncation_signal(row)
            row["_preference_sensitive"] = parse_bool(row.get("preference_sensitive", ""))
            row["_uncertainty_required"] = parse_bool(row.get("uncertainty_required", ""))
            rows[row["example_id"]] = row
    return rows


def build_target(example_id, left_row, right_row, high_delta_threshold):
    left_score = left_row["_total_score"]
    right_score = right_row["_total_score"]
    score_delta = None if left_score is None or right_score is None else left_score - right_score
    abs_delta = abs(score_delta) if score_delta is not None else 0

    left_failures = left_row["_failure_set"]
    right_failures = right_row["_failure_set"]
    left_safety = bool(left_failures & SAFETY_FAILURES)
    right_safety = bool(right_failures & SAFETY_FAILURES)
    safety_critical = left_safety or right_safety
    high_score_divergence = abs_delta >= high_delta_threshold
    preference_gap = (
        left_row["grade"] == "C"
        and (("preference omission" in left_failures) != ("preference omission" in right_failures))
    )
    uncertainty_gap = left_row["_uncertainty_required"] and (
        (("missing uncertainty disclosure" in left_failures))
        != (("missing uncertainty disclosure" in right_failures))
    )
    failure_label_disagreement = left_failures != right_failures
    truncation_confound = (
        left_row["grade"] in {"C", "D", "I"}
        and (left_row["_truncation_signal"] or right_row["_truncation_signal"])
        and (abs_delta >= 2 or safety_critical or preference_gap or uncertainty_gap)
    )

    reasons = []
    if safety_critical:
        reasons.append("safety_critical")
    if high_score_divergence:
        reasons.append("high_score_divergence")
    if preference_gap:
        reasons.append("preference_gap")
    if uncertainty_gap:
        reasons.append("uncertainty_gap")
    if truncation_confound:
        reasons.append("truncation_confound")
    if failure_label_disagreement and reasons:
        reasons.append("failure_label_disagreement")

    if not reasons:
        return None

    priority = 0
    if safety_critical:
        priority += 100
    priority += abs_delta * 10
    if preference_gap:
        priority += 18
    if uncertainty_gap:
        priority += 16
    if left_row["grade"] in {"C", "D", "I"}:
        priority += 8
    if truncation_confound:
        priority += 5
    if failure_label_disagreement:
        priority += 3

    if safety_critical:
        primary_reason = "safety_critical"
    elif high_score_divergence:
        primary_reason = "high_score_divergence"
    elif preference_gap:
        primary_reason = "preference_gap"
    elif uncertainty_gap:
        primary_reason = "uncertainty_gap"
    elif truncation_confound:
        primary_reason = "truncation_confound"
    else:
        primary_reason = "failure_label_disagreement"

    return {
        "example_id": example_id,
        "grade": left_row["grade"],
        "source_topic": left_row["source_topic"],
        "population": left_row["population"],
        "task_family": left_row["task_family"],
        "expected_posture": left_row["expected_posture"],
        "primary_reason": primary_reason,
        "reasons": reasons,
        "priority": priority,
        "score_delta": score_delta,
        "abs_score_delta": abs_delta,
        "left_score": left_score,
        "right_score": right_score,
        "left_failures": left_row["_failures"],
        "right_failures": right_row["_failures"],
        "left_truncation_signal": left_row["_truncation_signal"],
        "right_truncation_signal": right_row["_truncation_signal"],
        "prompt": left_row["user_prompt"],
        "left_response_excerpt": shorten(left_row.get("response_text", "")),
        "right_response_excerpt": shorten(right_row.get("response_text", "")),
        "left_notes_excerpt": shorten(left_row.get("evaluator_notes", ""), width=320),
        "right_notes_excerpt": shorten(right_row.get("evaluator_notes", ""), width=320),
    }


def sort_targets(targets):
    return sorted(
        targets,
        key=lambda target: (
            -target["priority"],
            -target["abs_score_delta"],
            target["example_id"],
        ),
    )


def select_priority_queue(targets, max_targets):
    sorted_targets = sort_targets(targets)
    selected = []
    selected_ids = set()

    def take(predicate, limit=None):
        taken = 0
        for target in sorted_targets:
            if target["example_id"] in selected_ids:
                continue
            if not predicate(target):
                continue
            selected.append(target)
            selected_ids.add(target["example_id"])
            taken += 1
            if limit is not None and taken >= limit:
                break

    take(lambda target: target["primary_reason"] == "safety_critical")
    take(lambda target: target["primary_reason"] == "high_score_divergence")
    take(lambda target: target["primary_reason"] == "preference_gap", limit=2)
    take(lambda target: target["primary_reason"] == "uncertainty_gap", limit=2)

    for target in sorted_targets:
        if len(selected) >= max_targets:
            break
        if target["example_id"] in selected_ids:
            continue
        selected.append(target)
        selected_ids.add(target["example_id"])

    return selected[:max_targets]


def write_csv(path, targets):
    fieldnames = [
        "example_id",
        "grade",
        "source_topic",
        "population",
        "task_family",
        "expected_posture",
        "primary_reason",
        "reasons",
        "left_score",
        "right_score",
        "score_delta_left_minus_right",
        "left_failures",
        "right_failures",
        "left_truncation_signal",
        "right_truncation_signal",
        "prompt",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for target in sort_targets(targets):
            writer.writerow(
                {
                    "example_id": target["example_id"],
                    "grade": target["grade"],
                    "source_topic": target["source_topic"],
                    "population": target["population"],
                    "task_family": target["task_family"],
                    "expected_posture": target["expected_posture"],
                    "primary_reason": target["primary_reason"],
                    "reasons": ";".join(target["reasons"]),
                    "left_score": target["left_score"],
                    "right_score": target["right_score"],
                    "score_delta_left_minus_right": target["score_delta"],
                    "left_failures": ";".join(target["left_failures"]),
                    "right_failures": ";".join(target["right_failures"]),
                    "left_truncation_signal": str(target["left_truncation_signal"]).lower(),
                    "right_truncation_signal": str(target["right_truncation_signal"]).lower(),
                    "prompt": target["prompt"],
                }
            )


def render_detail_block(lines, index, target, left_label, right_label):
    lines.extend(
        [
            f"### {index}. `{target['example_id']}`",
            "",
            f"- grade/task: `{target['grade']}` / `{target['task_family']}`",
            f"- expected_posture: `{target['expected_posture']}`",
            f"- primary_reason: `{target['primary_reason']}`",
            f"- all_reasons: `{'; '.join(target['reasons'])}`",
            f"- score_delta: `{left_label} {target['left_score']}` vs `{right_label} {target['right_score']}`",
            f"- failures: `{left_label}` = `{'; '.join(target['left_failures']) or 'none'}`, `{right_label}` = `{'; '.join(target['right_failures']) or 'none'}`",
            "",
            "**Prompt**",
            "",
            target["prompt"],
            "",
            f"**{left_label} response excerpt**",
            "",
            target["left_response_excerpt"] or "(empty)",
            "",
            f"**{right_label} response excerpt**",
            "",
            target["right_response_excerpt"] or "(empty)",
            "",
            f"**{left_label} evaluator note excerpt**",
            "",
            target["left_notes_excerpt"] or "(empty)",
            "",
            f"**{right_label} evaluator note excerpt**",
            "",
            target["right_notes_excerpt"] or "(empty)",
            "",
        ]
    )


def write_markdown(path, all_targets, selected_targets, args, compared_rows):
    safety_count = sum(1 for target in all_targets if "safety_critical" in target["reasons"])
    divergence_count = sum(1 for target in all_targets if "high_score_divergence" in target["reasons"])
    preference_gap_count = sum(1 for target in all_targets if "preference_gap" in target["reasons"])
    uncertainty_gap_count = sum(1 for target in all_targets if "uncertainty_gap" in target["reasons"])
    truncation_confound_count = sum(1 for target in all_targets if "truncation_confound" in target["reasons"])

    lines = [
        "# Annotation Sanity Check Queue",
        "",
        f"- compared_rows: `{compared_rows}`",
        f"- left_annotations: `{args.left_annotations}`",
        f"- right_annotations: `{args.right_annotations}`",
        f"- labels: `{args.left_label}` vs `{args.right_label}`",
        f"- high_delta_threshold: `{args.high_delta_threshold}`",
        "",
        "이 문서는 same-set annotation sheet 두 개를 비교해서 사람이 다시 볼 우선 review target을 뽑은 것이다.",
        "우선순위는 safety-critical failure, 큰 점수 차이, C/I omission gap, truncation-confounded disagreement를 중심으로 잡았다.",
        "",
        "## headline counts",
        "",
        f"- flagged_examples: `{len(all_targets)}`",
        f"- safety_critical: `{safety_count}`",
        f"- high_score_divergence: `{divergence_count}`",
        f"- preference_gap: `{preference_gap_count}`",
        f"- uncertainty_gap: `{uncertainty_gap_count}`",
        f"- truncation_confound: `{truncation_confound_count}`",
        "",
        "## priority queue",
        "",
        "| rank | example_id | grade | primary_reason | left_score | right_score | delta |",
        "|---|---|---|---|---:|---:|---:|",
    ]

    for index, target in enumerate(selected_targets, start=1):
        lines.append(
            f"| {index} | `{target['example_id']}` | `{target['grade']}` | "
            f"`{target['primary_reason']}` | {target['left_score']} | {target['right_score']} | {target['score_delta']} |"
        )

    lines.extend(
        [
            "",
            "## review guidance",
            "",
            "1. `I` row에서는 evidence is insufficient posture가 실제로 보존됐는지 먼저 확인한다.",
            "2. `C` row에서는 benefits/harms plus values/preferences가 둘 다 살아 있는지 본다.",
            "3. `D` row에서는 recommend-against posture가 shared decision framing으로 불필요하게 약해지지 않았는지 본다.",
            "4. evaluator note에 `truncated`가 있는 경우 visible excerpt만으로 failure label이 과하게 붙었는지 재확인한다.",
            "",
            "## detailed targets",
            "",
        ]
    )

    for index, target in enumerate(selected_targets, start=1):
        render_detail_block(lines, index, target, args.left_label, args.right_label)

    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    left_rows = read_rows(args.left_annotations)
    right_rows = read_rows(args.right_annotations)

    left_ids = set(left_rows)
    right_ids = set(right_rows)
    shared_ids = sorted(left_ids & right_ids)
    if not shared_ids:
        raise SystemExit("No overlapping example_ids between annotation sheets.")

    targets = []
    for example_id in shared_ids:
        target = build_target(
            example_id,
            left_rows[example_id],
            right_rows[example_id],
            args.high_delta_threshold,
        )
        if target:
            targets.append(target)

    if not targets:
        raise SystemExit("No review targets found from the provided heuristics.")

    selected_targets = select_priority_queue(targets, args.max_targets)

    output_md = Path(args.output_md)
    output_csv = Path(args.output_csv)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    write_csv(output_csv, targets)
    write_markdown(output_md, sort_targets(targets), selected_targets, args, len(shared_ids))

    print(f"Wrote review-target markdown to {output_md}")
    print(f"Wrote review-target csv to {output_csv}")


if __name__ == "__main__":
    main()
