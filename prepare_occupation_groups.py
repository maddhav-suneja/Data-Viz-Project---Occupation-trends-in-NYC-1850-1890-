from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"


def parse_args():
    parser = argparse.ArgumentParser(description="Create grouped occupation outputs from geocoded point data.")
    parser.add_argument("--input", default=str(DATA_DIR / "geocoded_master_all_years.csv"))
    parser.add_argument("--output", default=str(DATA_DIR / "occupation_grouped.csv"))
    parser.add_argument("--summary", default=str(DATA_DIR / "occupation_group_summary.csv"))
    return parser.parse_args()


def normalize_occupation(value: str | None) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).lower()
    text = text.replace("& co", "")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_occupation(value: str | None) -> str:
    text = normalize_occupation(value)
    if not text:
        return "Other / Unknown"

    if any(term in text for term in ["merchant", "dealer", "broker", "grocer", "importer", "trader", "owner", "bookseller"]):
        return "Business / Owner"
    if any(term in text for term in ["tailor", "carpenter", "printer", "hairdresser", "jeweler", "bookbinder", "mason", "smith", "butcher", "baker"]):
        return "Skilled Trades"
    if any(term in text for term in ["lawyer", "physician", "doctor", "teacher", "editor", "publisher", "architect"]):
        return "Professional"
    if any(term in text for term in ["laborer", "porter", "watchman", "driver", "loader", "worker"]):
        return "Labor"
    if any(term in text for term in ["servant", "cook", "washerwoman", "domestic", "waiter", "maid"]):
        return "Domestic / Service"
    if any(term in text for term in ["clerk", "bookkeeper", "cashier", "secretary", "accountant"]):
        return "Clerical / Administrative"
    if any(term in text for term in ["captain", "sailor", "seaman", "pilot", "ship", "stevedore"]):
        return "Transport / Maritime"
    if any(term in text for term in ["police", "president", "alderman", "public"]):
        return "Public / Civic"
    return "Other / Unknown"


def main():
    args = parse_args()
    input_path = Path(args.input)
    df = pd.read_csv(input_path)

    year_col = "year" if "year" in df.columns else "directory_year"
    df["occupation_group"] = df["occupation"].apply(classify_occupation)
    df.to_csv(args.output, index=False)

    summary = (
        df.groupby([year_col, "occupation_group"])
        .size()
        .reset_index(name="count")
        .rename(columns={year_col: "year"})
        .sort_values(["year", "count"], ascending=[True, False])
    )
    summary.to_csv(args.summary, index=False)

    print(f"Wrote grouped data: {args.output}")
    print(f"Wrote summary: {args.summary}")


if __name__ == "__main__":
    main()
