"""Helpers for run metadata and comparability validation."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


MANIFEST_FILENAME = "run_manifest.json"
ROW_METADATA_FIELDS = [
    "model_name",
    "judge_model",
    "dataset_item_count",
    "dataset_case_id_hash",
]


def compute_case_id_hash(case_ids):
    """Return a stable hash for a collection of case IDs."""
    normalized = "\n".join(sorted(case_ids))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_case_id_hash_from_items(items):
    """Return a stable case-id hash from benchmark items."""
    return compute_case_id_hash(item["case_id"] for item in items)


def compute_case_id_hash_from_results(results):
    """Return a stable case-id hash from result rows."""
    return compute_case_id_hash(result["case_id"] for result in results)


def build_run_manifest(
    model_name,
    judge_model,
    data_path,
    items,
    output_dir,
    report_path,
    figures_dir,
):
    """Build manifest metadata for one evaluation run."""
    case_ids = [item["case_id"] for item in items]
    return {
        "manifest_version": "drug_safety_update_eval_run_manifest_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_name": model_name,
        "judge_model": judge_model,
        "data_path": str(Path(data_path).resolve()),
        "output_dir": str(Path(output_dir).resolve()),
        "report_path": str(Path(report_path).resolve()),
        "figures_dir": str(Path(figures_dir).resolve()),
        "dataset_item_count": len(items),
        "dataset_case_id_hash": compute_case_id_hash(case_ids),
        "case_ids": case_ids,
    }


def write_run_manifest(output_dir, manifest):
    """Write a run manifest into the output directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest_path


def load_run_manifest(results_path):
    """Load the sidecar run manifest for a results file if present."""
    manifest_path = Path(results_path).resolve().parent / MANIFEST_FILENAME
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text())


def extract_row_metadata(results):
    """Extract and validate metadata that may be embedded in result rows."""
    metadata = {}
    for field in ROW_METADATA_FIELDS:
        values = {result.get(field) for result in results if field in result}
        if len(values) > 1:
            raise ValueError(f"Inconsistent row metadata for {field}: {sorted(values)}")
        metadata[field] = next(iter(values)) if values else None

    metadata["dataset_item_count_inferred"] = len(results)
    metadata["dataset_case_id_hash_inferred"] = compute_case_id_hash_from_results(results)
    metadata["case_ids"] = [result["case_id"] for result in results]
    return metadata
