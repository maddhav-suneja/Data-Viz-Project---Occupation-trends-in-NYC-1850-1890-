# Occupation Trends in Early New York, 1850-1854

This project is an interactive Streamlit dashboard built for NYU Data Services' 2026 urban data visualization contest. It uses the **New York City Directories Extracted Persons Entries, 1850-1890** dataset to explore how work, occupation, and neighborhood patterns appeared in early New York through a focused slice of the data from **1850 to 1854**.

The dashboard combines spatial mapping, occupational composition, neighborhood comparison, and historical atmosphere into a single interface. A year slider lets the viewer move across 1850-1854 and see how the mapped entries and occupational structure change over time.

## Project Overview

This project asks a simple question: **what did the geography of work look like in early New York?**

Using geocoded person-entry records from historical city directories, the dashboard shows:

- an interactive point map where each point represents one geocoded directory entry
- an occupation diversity chart for the selected year
- a Manhattan neighborhood choropleth showing which occupation group is most prominent in each area
- a year-specific historical audio track to enrich the viewing experience

Rather than attempting to cover the entire 1850-1890 span in one rushed prototype, this submission focuses on **1850-1854** so that the visualization, cleaning, and documentation could be made more interpretable and polished for the contest.

## Dataset

Primary contest dataset:

- **New York City Directories Extracted Persons Entries, 1850-1890**

This is one of the eligible datasets listed in the NYU urban data visualization contest prompt and serves as the substantive core of the project.

## Additional Data Sources

To support the geographic visualization, this project also uses:

- **Manhattan Neighborhood Tabulation Area (NTA) boundaries**, based on NYC neighborhood polygon data used to build the choropleth layer

These neighborhood boundaries were used only to spatially summarize the contest dataset. The directory dataset remains the primary analytical source.

## What the Dashboard Shows

### 1. Interactive Map

The main map plots individual geocoded directory entries for the selected year. Hovering over a point reveals:

- person name
- occupation

This view is intentionally person-level rather than aggregated, so the viewer can see the raw spatial footprint of the records.

### 2. Occupation Diversity Chart

The pie chart summarizes the occupational composition of the selected year using grouped occupation categories rather than raw occupation strings.

### 3. Neighborhood Occupation Choropleth

The choropleth assigns geocoded records to Manhattan neighborhood polygons and colors each neighborhood by its dominant occupation group for the selected year. Hover text provides additional ratio detail.

### 4. Historical Audio Layer

The dashboard includes year-specific music files to add historical texture and support the rubric category on information enrichment. These audio files are presentation elements rather than analytical inputs.

## Methods

### Data Cleaning

The original historical directory data required substantial cleaning before it could be mapped or grouped meaningfully.

The cleaning process included:

- flattening nested location records
- normalizing person names and address strings
- preserving location confidence information from the corrected entry structure
- identifying and removing exact person-address-year duplicates
- filtering vague or non-geocodable addresses
- creating geocoding-ready address queries

Historical data issues included:

- OCR noise
- inconsistent abbreviations
- spelling variation
- incomplete or ambiguous addresses
- repeated addresses across many records

### Geocoding

Addresses were geocoded after cleaning and normalization. Repeated cleaned addresses were cached so the same location did not need to be geocoded repeatedly.

For the final working app, the project uses the saved geocoded results for the years 1850-1854 only.

### Occupation Grouping

Raw occupation labels were too inconsistent to compare directly, so they were normalized and grouped into broader analytical categories. This included:

- text normalization
- abbreviation cleanup
- synonym handling
- rule-based grouping
- refinement of high-frequency unresolved terms

The final grouped categories include:

- Business / Owner
- Skilled Trades
- Professional
- Labor
- Domestic / Service
- Clerical / Administrative
- Transport / Maritime
- Public / Civic
- Other / Unknown

This grouping step was essential for both the occupation chart and the neighborhood choropleth.

## Tools and Software Used

- Python
- Pandas
- Streamlit
- Plotly
- Pydeck

## Generative AI Use and Credit

Generative AI was used as a coding and workflow assistant during this project.

Specifically, OpenAI Codex assisted with:

- drafting and refining the data cleaning scripts
- helping normalize historical address and occupation fields
- structuring the geocoding workflow and cache logic
- helping build and debug the Streamlit dashboard
- refining layout, styling, and visualization presentation
- helping draft project documentation

All analytical decisions, project framing, visualization direction, and final submission choices were directed and reviewed by the student author.

### AI-Assisted Data Cleaning Credit

Credit is due to **OpenAI Codex** for assisting with the data cleaning workflow, especially:

- address normalization logic
- duplicate handling logic
- geocoding pipeline structure
- occupation grouping workflow

The final project reflects human judgment in selecting the years, choosing the visual framing, evaluating map behavior, refining the design, and deciding what to include in the final dashboard.

## Reproducibility Notes

This repository contains the lightweight files needed to run the final dashboard version:

- `streamlit_app.py`
- `requirements.txt`
- `data/app_points_1850_1854.csv`
- `data/occupation_group_summary_1850_1854.csv`
- `data/manhattan_nta.geojson`
- `Song/1850.mp3` through `Song/1854.mp3`

To run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Limitations

- Historical addresses do not always correspond neatly to modern geographies.
- Some occupations remain ambiguous and are grouped into `Other / Unknown`.
- The project uses a focused 1850-1854 slice of the broader 1850-1890 dataset.
- The neighborhood summary is based on modern boundary polygons applied to historical geocoded points.
- The music files are used for atmosphere and do not constitute historical analysis.

## Why This Submission Fits the Contest

This project is designed to align with the judging rubric by emphasizing:

- **ease of interpretation** through a clear slider-driven interface
- **information enrichment** through sound and spatial context
- **elegance and efficiency** through a focused, uncluttered dashboard
- **originality and impact** by turning a historical directory dataset into an interactive urban labor map
- **quality of documentation** through transparent methods, sources, and process notes

## Author Note

This dashboard was built as an effort to make an NYU-created historical urban dataset more accessible, legible, and engaging for a contemporary audience. It treats the city directory not just as a list of names and occupations, but as a record of how work was distributed across space in early New York.
