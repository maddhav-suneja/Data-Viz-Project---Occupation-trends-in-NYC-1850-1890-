from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


STREET_SUFFIXES = {
    "st": "Street",
    "street": "Street",
    "ave": "Avenue",
    "av": "Avenue",
    "avenue": "Avenue",
    "rd": "Road",
    "road": "Road",
    "ln": "Lane",
    "lane": "Lane",
    "pl": "Place",
    "place": "Place",
    "ct": "Court",
    "court": "Court",
    "sq": "Square",
    "square": "Square",
}

DIRECTIONALS = {"e": "East", "w": "West", "n": "North", "s": "South"}

BOROUGH_HINTS = {
    "brooklyn": "Brooklyn, New York, NY",
    "b'klyn": "Brooklyn, New York, NY",
    "bklyn": "Brooklyn, New York, NY",
    "new jersey": "New Jersey",
    "n. j.": "New Jersey",
    "n.j.": "New Jersey",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean one directory year NDJSON file.")
    parser.add_argument("--input", required=True, help="Path to one NDJSON input file")
    parser.add_argument("--outdir", required=True, help="Directory for outputs")
    parser.add_argument("--min-confidence", type=float, default=8.0)
    return parser.parse_args()


def clean_text(value):
    if value is None:
        return None
    value = str(value).replace("\u00a0", " ").strip()
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" ,.;")
    return value or None


def normalize_name(name):
    name = clean_text(name)
    if not name:
        return None
    replacements = {
        "Wm.": "William",
        "Chas.": "Charles",
        "Geo.": "George",
        "Jos.": "Joseph",
        "Jno.": "John",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def expand_common_abbreviations(address):
    if address is None:
        return None
    address = clean_text(address)
    if not address:
        return None

    address = (
        address.replace("B'way", "Broadway")
        .replace("b'way", "Broadway")
        .replace("B'klyn", "Brooklyn")
        .replace("N. J.", "New Jersey")
        .replace("N.J.", "New Jersey")
        .replace("N. Y.", "New York")
    )

    out = []
    for token in address.split():
        bare = re.sub(r"[.,]$", "", token)
        lower = bare.lower()
        if lower in DIRECTIONALS:
            out.append(DIRECTIONALS[lower])
        elif lower in STREET_SUFFIXES:
            out.append(STREET_SUFFIXES[lower])
        else:
            out.append(token)

    address = " ".join(out)
    address = re.sub(r"\bNo\.?\s*", "", address, flags=re.I)
    address = re.sub(r"\s+,", ",", address)
    address = re.sub(r",\s*", ", ", address)
    address = re.sub(r"\s+", " ", address).strip(" ,.;")
    return address or None


def normalize_address(address):
    address = expand_common_abbreviations(address)
    if not address:
        return None
    address = re.sub(r"\b[hvr]\b\.?$", "", address, flags=re.I).strip(" ,.;")
    return address or None


def has_house_number(address):
    return bool(address and re.search(r"\b\d+[A-Za-z]?\b", address))


def looks_too_vague(address):
    if not address:
        return True
    lower = address.lower().strip()
    if len(lower) < 5:
        return True
    if lower in {"new york", "brooklyn", "new jersey", "city"}:
        return True
    return not bool(re.search(r"[a-z]", lower))


def infer_area_suffix(address):
    lower = (address or "").lower()
    for key, suffix in BOROUGH_HINTS.items():
        if key in lower:
            return suffix
    return "Manhattan, New York, NY"


def make_geocode_query(address):
    if not address:
        return None
    return f"{address}, {infer_area_suffix(address)}"


def address_is_geocodable(address):
    if not address or looks_too_vague(address) or not has_house_number(address):
        return False
    lower = address.lower()
    strong_cues = [
        "street", "avenue", "road", "lane", "place", "court", "square",
        "broadway", "wall", "broad", "orchard", "allen", "maiden",
    ]
    return any(cue in lower for cue in strong_cues)


def load_ndjson(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def flatten_records(records, source_file: Path) -> pd.DataFrame:
    flat = []
    for rec in records:
        corrected = rec.get("corrected_entry") or {}
        locations = corrected.get("locations") or []
        subjects = corrected.get("subjects") or []
        occupations = corrected.get("occupations") or []
        person_name = normalize_name(subjects[0] if subjects else None)

        occupation_values = []
        for occ in occupations:
            if isinstance(occ, dict):
                value = occ.get("value")
            else:
                value = occ
            if value:
                occupation_values.append(str(value))
        occupation = "; ".join(occupation_values) if occupation_values else None

        if not locations:
            flat.append(
                {
                    "source_file": source_file.name,
                    "directory_year": rec.get("directory_year"),
                    "entry_uuid": rec.get("entry_uuid"),
                    "person_name": person_name,
                    "occupation": occupation,
                    "location_raw": None,
                    "location_clean": None,
                    "location_confidence": None,
                }
            )
            continue

        for loc in locations:
            raw = loc.get("value") if isinstance(loc, dict) else None
            score = loc.get("score") if isinstance(loc, dict) else None
            flat.append(
                {
                    "source_file": source_file.name,
                    "directory_year": rec.get("directory_year"),
                    "entry_uuid": rec.get("entry_uuid"),
                    "person_name": person_name,
                    "occupation": occupation,
                    "location_raw": clean_text(raw),
                    "location_clean": normalize_address(raw),
                    "location_confidence": pd.to_numeric(score, errors="coerce"),
                }
            )

    return pd.DataFrame(flat)


def add_quality_flags(df: pd.DataFrame, min_confidence: float) -> pd.DataFrame:
    df = df.copy()
    df["person_name_norm"] = (
        df["person_name"].fillna("").str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    )
    df["location_norm"] = (
        df["location_clean"].fillna("").str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    )
    df["geocode_candidate"] = df["location_clean"].apply(address_is_geocodable)
    df["confidence_ok"] = df["location_confidence"].fillna(0) >= min_confidence
    df["needs_review"] = (~df["geocode_candidate"]) | (~df["confidence_ok"])
    df["duplicate_exact"] = df.duplicated(
        subset=["directory_year", "person_name_norm", "location_norm"], keep=False
    )
    df["geocode_query"] = df["location_clean"].apply(make_geocode_query)
    return df


def main():
    args = parse_args()
    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    records = load_ndjson(input_path)
    df = flatten_records(records, input_path)
    df = add_quality_flags(df, args.min_confidence)

    all_rows_path = outdir / f"{input_path.stem}_all_rows.csv"
    review_path = outdir / f"{input_path.stem}_review.csv"
    ready_path = outdir / f"{input_path.stem}_geocode_ready.csv"
    summary_path = outdir / f"{input_path.stem}_summary.json"

    df.to_csv(all_rows_path, index=False)
    df[df["needs_review"]].to_csv(review_path, index=False)

    ready_df = (
        df[df["geocode_candidate"] & df["confidence_ok"] & df["location_clean"].notna()]
        .sort_values(by=["location_confidence"], ascending=False)
        .drop_duplicates(subset=["directory_year", "person_name_norm", "location_norm"], keep="first")
    )
    ready_df.to_csv(ready_path, index=False)

    summary = {
        "input_file": str(input_path),
        "total_flat_rows": int(len(df)),
        "geocode_candidates": int(df["geocode_candidate"].sum()),
        "confidence_ok": int(df["confidence_ok"].sum()),
        "review_rows": int(df["needs_review"].sum()),
        "ready_rows": int(len(ready_df)),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Done")
    print(f"All rows: {all_rows_path}")
    print(f"Review rows: {review_path}")
    print(f"Geocode ready: {ready_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
