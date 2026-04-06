from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
CACHE_PATH = DATA_DIR / "geocode_cache.csv"


def parse_args():
    parser = argparse.ArgumentParser(description="Geocode geocode_ready CSVs with Google Maps API.")
    parser.add_argument("--base-dir", default=str(PROJECT_DIR))
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on uncached queries")
    parser.add_argument("--sleep", type=float, default=0.03)
    return parser.parse_args()


def load_cache(cache_path: Path) -> pd.DataFrame:
    if cache_path.exists():
        return pd.read_csv(cache_path)
    return pd.DataFrame(columns=["geocode_query", "latitude", "longitude", "geocoder_match", "status"])


def save_cache(cache_df: pd.DataFrame, cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_df.to_csv(cache_path, index=False)


def google_geocode(query: str, api_key: str):
    params = urllib.parse.urlencode({"address": query, "key": api_key})
    url = f"https://maps.googleapis.com/maps/api/geocode/json?{params}"
    with urllib.request.urlopen(url, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    status = payload.get("status")
    if status != "OK" or not payload.get("results"):
        return {
            "geocode_query": query,
            "latitude": None,
            "longitude": None,
            "geocoder_match": None,
            "status": status or "UNKNOWN",
        }
    result = payload["results"][0]
    location = result["geometry"]["location"]
    return {
        "geocode_query": query,
        "latitude": location["lat"],
        "longitude": location["lng"],
        "geocoder_match": result.get("formatted_address"),
        "status": status,
    }


def collect_ready_rows(base_dir: Path, year: int | None) -> pd.DataFrame:
    rows = []
    pattern = f"{year}_output/*_geocode_ready.csv" if year else "*_output/*_geocode_ready.csv"
    for path in sorted(base_dir.glob(pattern)):
        df = pd.read_csv(path)
        df["source_ready_file"] = path.name
        rows.append(df)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def main():
    args = parse_args()
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not set.")

    base_dir = Path(args.base_dir)
    ready_df = collect_ready_rows(base_dir, args.year)
    if ready_df.empty:
        print("No geocode_ready rows found.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache_df = load_cache(CACHE_PATH)
    cached_queries = set(cache_df["geocode_query"].dropna().astype(str))

    queries = ready_df["geocode_query"].dropna().drop_duplicates().tolist()
    uncached = [query for query in queries if query not in cached_queries]
    if args.limit is not None:
        uncached = uncached[: args.limit]

    new_rows = []
    for index, query in enumerate(uncached, start=1):
        result = google_geocode(query, api_key)
        new_rows.append(result)
        if index % 25 == 0:
            cache_df = pd.concat([cache_df, pd.DataFrame(new_rows)], ignore_index=True)
            save_cache(cache_df.drop_duplicates(subset=["geocode_query"], keep="last"), CACHE_PATH)
            new_rows = []
        time.sleep(args.sleep)

    if new_rows:
        cache_df = pd.concat([cache_df, pd.DataFrame(new_rows)], ignore_index=True)

    cache_df = cache_df.drop_duplicates(subset=["geocode_query"], keep="last")
    save_cache(cache_df, CACHE_PATH)

    merged = ready_df.merge(cache_df, on="geocode_query", how="left")
    merged["has_coordinates"] = merged["latitude"].notna() & merged["longitude"].notna()

    scope = f"{args.year}" if args.year else "all_years"
    (DATA_DIR / f"all_geocode_ready_{scope}.csv").write_text(merged.to_csv(index=False), encoding="utf-8")
    (DATA_DIR / f"geocoded_master_{scope}.csv").write_text(merged.to_csv(index=False), encoding="utf-8")

    points_cols = [col for col in ["person_name", "occupation", "directory_year", "latitude", "longitude", "has_coordinates"] if col in merged.columns]
    points = merged[points_cols].copy()
    if "directory_year" in points.columns:
        points = points.rename(columns={"directory_year": "year"})
    (DATA_DIR / f"geocoded_points_{scope}.csv").write_text(points.to_csv(index=False), encoding="utf-8")

    print(f"Processed {len(queries)} unique queries; cache size is now {len(cache_df)}.")
    print(f"Cache: {CACHE_PATH}")


if __name__ == "__main__":
    main()
