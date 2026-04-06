from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Run Google geocoding year by year in batches.")
    parser.add_argument("--base-dir", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--start-year", type=int, default=1850)
    parser.add_argument("--end-year", type=int, default=1889)
    parser.add_argument("--batch-size", type=int, default=250)
    return parser.parse_args()


def main():
    args = parse_args()
    if not os.environ.get("GOOGLE_MAPS_API_KEY"):
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not set.")

    script = Path(__file__).resolve().parent / "geocode_all_years.py"
    for year in range(args.start_year, args.end_year + 1):
        while True:
            cmd = [
                sys.executable,
                str(script),
                "--base-dir",
                args.base_dir,
                "--year",
                str(year),
                "--limit",
                str(args.batch_size),
            ]
            print("Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)
            # one pass per year/batch is enough; rerun manually or loop externally if desired
            break


if __name__ == "__main__":
    main()
