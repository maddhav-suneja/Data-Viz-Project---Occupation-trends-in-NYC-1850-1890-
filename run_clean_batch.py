from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Run clean_directory_year.py across a range of year files.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--start-year", type=int, default=1850)
    parser.add_argument("--end-year", type=int, default=1889)
    return parser.parse_args()


def main():
    args = parse_args()
    base = Path(args.input_dir)
    script = Path(__file__).resolve().parent / "clean_directory_year.py"

    for year in range(args.start_year, args.end_year + 1):
        matches = sorted(base.glob(f"{year}*.ndjson"))
        if not matches:
            print(f"Skipping {year}: no input file found")
            continue
        input_path = matches[0]
        outdir = base / f"{year}_output"
        cmd = [sys.executable, str(script), "--input", str(input_path), "--outdir", str(outdir)]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
