from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from combined_momentum.config import load_config
from combined_momentum.pipeline import VALID_STAGES, run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the combined momentum research pipeline")
    parser.add_argument(
        "--config",
        default="configs/final_us_industry_project.yaml",
        help="Path to YAML configuration",
    )
    parser.add_argument("--stage", default="all", choices=sorted(VALID_STAGES))
    parser.add_argument("--run-id", default=None, help="Existing or requested artifact run ID")
    parser.add_argument("--force-download", action="store_true", help="Replace the cached raw price file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    run_dir, summary = run_pipeline(
        config,
        stage=args.stage,
        run_id=args.run_id,
        force_download=args.force_download,
    )
    print(json.dumps({"run_dir": str(run_dir) if run_dir else None, **summary}, indent=2, default=str))


if __name__ == "__main__":
    main()

