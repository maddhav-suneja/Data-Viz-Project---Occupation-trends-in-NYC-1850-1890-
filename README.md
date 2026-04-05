# Occupation Trends in Early New York, 1850-1854

An interactive geospatial data-science project built with Streamlit from the **New York City Directories Extracted Persons Entries, 1850-1890** dataset.

This repository contains my submission for the **NYU Data Services urban data visualization contest**. The project turns noisy historical directory records into a cleaned, geocoded, and interpretable dashboard that explores how occupations appeared across Manhattan in the early 1850s.

## Overview

This project asks a simple question:

**What did the geography of work look like in early New York?**

Using a cleaned and geocoded subset of directory entries from **1850-1854**, the dashboard allows viewers to move year by year and compare:

- individual directory entries plotted as geocoded points
- grouped occupation composition for the selected year
- neighborhood-level occupational dominance across Manhattan

The result is both a contest submission and a portfolio-style data-science project centered on historical data cleaning, geospatial analysis, and interactive storytelling.

## Highlights

- Cleaned and normalized historical address and occupation data from a noisy 19th-century source
- Geocoded address records with the **Google Maps Geocoding API**
- Cached repeated queries to reduce redundant API calls
- Engineered occupation groups from inconsistent raw text
- Built an interactive Streamlit dashboard with coordinated temporal and spatial views
- Designed the final interface around readability, historical atmosphere, and methodological transparency

## Dataset

Primary dataset:

- **New York City Directories Extracted Persons Entries, 1850-1890**

This is one of the official eligible datasets provided for the NYU Data Services contest. The full source spans forty years, but this project focuses on **1850-1854** so the final product could prioritize geocoding quality, interpretability, and polished presentation.

## Additional Sources

Supporting sources used in the analysis:

- **Google Maps Geocoding API** for converting cleaned historical addresses into coordinates
- **Manhattan Neighborhood Tabulation Area (NTA) polygons** for neighborhood-level spatial aggregation in the choropleth

These sources support interpretation of the contest dataset; the historical directory records remain the primary object of analysis.

## Data Science Workflow

The project followed an end-to-end workflow:

1. Parse and flatten historical directory records
2. Clean and normalize person, occupation, and location fields
3. Filter out vague or non-geocodable addresses
4. Remove exact person-address-year duplicates
5. Geocode cleaned address queries
6. Cache repeated address lookups
7. Join coordinates back to person-level records
8. Engineer occupation groups from noisy raw strings
9. Aggregate records for charts and choropleth layers
10. Build and refine the interactive Streamlit application

## Data Cleaning

Historical city-directory data required significant preprocessing before it could be used analytically.

### Address Cleaning

Address preparation included:

- flattening nested corrected location fields
- standardizing punctuation and whitespace
- expanding common abbreviations where possible
- normalizing street-type tokens
- preserving confidence-related location fields
- rejecting incomplete, vague, or non-geocodable addresses
- preparing cleaned geocoding query strings

Key challenges in the raw data:

- OCR noise
- inconsistent spelling
- abbreviations
- incomplete address strings
- repeated addresses across many records
- historically shifted or obsolete place references

### Duplicate Handling

Duplicates were handled at the analytical-record level by removing exact person-address-year repeats after normalization. This preserved historically meaningful repeated addresses while filtering obvious duplication artifacts.

### Occupation Cleaning and Grouping

Raw occupation values were too inconsistent to use directly, so they were normalized and grouped through a layered text-processing workflow:

- lowercase and punctuation normalization
- abbreviation cleanup
- manual synonym mapping
- rule-based classification
- iterative refinement using frequent unresolved terms

Final occupation groups:

- Business / Owner
- Skilled Trades
- Professional
- Labor
- Domestic / Service
- Clerical / Administrative
- Transport / Maritime
- Public / Civic
- Other / Unknown

This grouping layer powers both the occupation composition chart and the neighborhood choropleth.

## Geocoding Strategy

Geocoding was performed using the **Google Maps Geocoding API** after historical addresses were cleaned and normalized.

### Why Google Maps API

The final project needed a geocoder that was:

- reliable under deadline conditions
- practical for batch processing
- more stable than public, rate-limited alternatives

### Geocoding Workflow

The geocoding pipeline used the following strategy:

- geocode only cleaned candidate addresses
- cache results for repeated addresses
- reuse coordinates for recurring address strings across rows
- join cached coordinates back onto the person-level dataset

This reduced redundant calls, improved efficiency, and made the final data pipeline more reproducible.

## Visualization Strategy

The dashboard was designed around three synchronized analytical views controlled by a single year slider.

### 1. Point Map

One geocoded point is shown for each directory entry in the selected year.

Why this choice:

- it preserves the direct connection between the historical record and the spatial display
- it makes the data feel archival and human rather than overly abstracted

Hover tooltip:

- person name
- occupation

### 2. Occupation Composition Chart

This chart summarizes grouped occupational composition for the selected year.

Why this choice:

- grouped occupations create a readable summary from messy raw text
- the chart provides a compact citywide view that complements the map

### 3. Neighborhood Dominance Choropleth

The choropleth colors Manhattan neighborhoods by the occupation group with the highest share in that area for the selected year.

Why this choice:

- it shifts the analysis from individual points to neighborhood character
- it makes occupational specialization easier to read than the point map alone

### Dashboard Design Choices

- one shared year control across all views
- stable occupation colors across years
- year-specific accent themes used for atmosphere, not analytical encoding
- summary cards and interpretive text to guide the viewer
- a historical paper-and-ink visual language rather than a generic dashboard aesthetic

## Dashboard Features

The final Streamlit app includes:

- year slider for 1850-1854
- interactive Manhattan point map
- hover tooltips with name and occupation
- grouped occupation composition chart
- neighborhood dominance choropleth
- summary cards and interpretive text
- year-specific historical audio layer

## Tech Stack

- **Python**
- **Pandas**
- **Google Maps Geocoding API**
- **Streamlit**
- **Pydeck**
- **Plotly Express**

## Project Structure

```text
.
├── streamlit_app.py
├── requirements.txt
├── README.md
├── data
│   ├── app_points_1850_1854.csv
│   ├── occupation_group_summary_1850_1854.csv
│   └── manhattan_nta.geojson
└── Song
    ├── 1850.mp3
    ├── 1851.mp3
    ├── 1852.mp3
    ├── 1853.mp3
    └── 1854.mp3
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run streamlit_app.py
```

## Technical Decisions

### Focused Time Window

The source dataset covers forty years, but the final project focuses on **1850-1854**. This was a deliberate product decision:

- the time slice is still rich enough to show meaningful patterns
- the narrower scope improved geocoding completion and dashboard quality
- it allowed more time for cleaning, documentation, and visualization refinement

### Stable Occupation Encoding

Occupation colors remain fixed across years so the viewer can compare categories consistently.

### Modern Neighborhood Boundaries on Historical Data

The choropleth uses modern Manhattan neighborhood polygons to summarize historical points. This is analytically useful, but still interpretive rather than a perfect historical administrative match.

## Limitations

- Historical addresses do not always resolve cleanly to modern geographies.
- Geocoding quality depends on the legibility and modern interpretability of historical address strings.
- The project represents a geocoded subset of records rather than a complete census of residents.
- Occupation grouping involves interpretive classification.
- Modern polygon boundaries are applied to historical points.
- The published dashboard focuses on 1850-1854 rather than the full 1850-1890 span.

## Generative AI Disclosure

Generative AI was used as a coding and workflow assistant during development.

OpenAI Codex assisted with:

- drafting and refining data cleaning scripts
- address normalization logic
- duplicate-handling logic
- geocoding workflow design
- occupation grouping workflow
- Streamlit debugging and interface refinement
- README drafting and documentation support

All final analytical framing, interpretation, design choices, and submission decisions were made by the project author.

## Why This Works as a Portfolio Project

This project demonstrates:

- historical data cleaning under noisy conditions
- geospatial data preparation
- API-based geocoding with caching and reuse
- feature engineering from messy text
- interactive visualization design
- methodological transparency
- end-to-end data storytelling from raw records to deployable app

## Acknowledgment

This project was built as both a historical urban visualization and a technical exercise in transforming archival-style data into a structured, explorable analytical product. It aims to make an NYU-supported historical dataset more legible, reusable, and engaging for contemporary audiences.
