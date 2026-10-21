from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from combined_momentum.config import load_config
from combined_momentum.data import download_yahoo_prices
from combined_momentum.io import write_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the configured raw prices without validating or transforming them"
    )
    parser.add_argument(
        "--config",
        default="configs/final_us_industry_project.yaml",
        help="Path to YAML configuration",
    )
    return parser.parse_args()


def main() -> None:
    config = load_config(parse_args().config)
    raw = download_yahoo_prices(config)
    output = config.path("raw_prices")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_table(raw, output)
    print(
        json.dumps(
            {
                "raw_file": str(output),
                "rows_downloaded": len(raw),
                "symbols_downloaded": int(raw["ticker"].nunique()),
                "next_step": "Group member A must run and document data validation.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
