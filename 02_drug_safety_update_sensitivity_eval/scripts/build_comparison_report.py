#!/usr/bin/env python3
"""CLI wrapper for cross-model comparison reporting."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from eval.comparison_report import main


if __name__ == "__main__":
    raise SystemExit(main())
