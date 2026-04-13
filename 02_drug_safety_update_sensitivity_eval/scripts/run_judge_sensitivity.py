#!/usr/bin/env python3
"""CLI wrapper for judge-sensitivity validation."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from eval.judge_sensitivity import main


if __name__ == "__main__":
    raise SystemExit(main())
