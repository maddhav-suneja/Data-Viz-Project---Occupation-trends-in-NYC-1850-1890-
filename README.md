# Occupation Trends in Early New York, 1850-1854

An interactive historical data visualization built with Streamlit for NYU Data Services' 2026 urban data visualization contest.

This project uses the **New York City Directories Extracted Persons Entries, 1850-1890** dataset to explore how occupations were distributed across Manhattan in the early 1850s. Through a synchronized year slider, the dashboard lets viewers move across 1850-1854 and compare individual directory entries, occupation composition, and neighborhood-level occupational dominance.

## Live Concept

The central question behind this project is:

**What did the geography of work look like in early New York?**

Rather than treating the city directory as a static table of names and jobs, this dashboard reframes it as a spatial and social record of urban life. The result is a historical interface that shows where people appeared in the directory, what kinds of work were represented, and how occupational patterns varied across neighborhoods.

## Why This Project

This project was created in response to NYU Data Services' urban data visualization contest, which highlights datasets created by NYU researchers and invites students to interpret them through thoughtful, well-documented visual work.

The competition emphasizes:

- ease of interpretation
- information enrichment
- elegance and efficiency
- originality and impact
- quality of documentation

This dashboard was designed with those goals in mind: readable interaction design, clear narrative framing, strong visual hierarchy, transparent methodology, and a focused scope that prioritizes interpretability over excess.

## Dataset

Primary contest dataset:

- **New York City Directories Extracted Persons Entries, 1850-1890**

This is one of the official eligible datasets provided for the NYU Data Services contest. The full source spans 1850-1890; this project focuses on the years **1850-1854** to keep the analysis and interface more coherent and contest-ready.

## Additional Sources

To support the spatial analysis, this project also uses:

- **Manhattan Neighborhood Tabulation Area (NTA) boundary polygons** for the neighborhood choropleth layer

These boundaries are used only to summarize the directory records geographically. The historical directory entries remain the primary dataset and the core analytical source.

## What the Dashboard Includes

### 1. Interactive Point Map

Each point represents one geocoded directory entry for the selected year.

Hovering reveals:

- person name
- occupation

This is intentionally kept at the individual-record level so the viewer can see the raw spatial footprint of the data.

### 2. Occupation Diversity Chart

A grouped occupation chart summarizes the occupational composition of the selected year. Because the original occupation labels are messy, abbreviated, and inconsistent, the dashboard uses normalized occupation groups rather than raw strings.

### 3. Neighborhood Occupation Choropleth

The choropleth assigns records to Manhattan neighborhood polygons and colors each neighborhood by its dominant occupation group for the selected year. Hover details provide a quick neighborhood-level ratio summary.

### 4. Historical Audio Layer

The dashboard includes year-specific background audio to add historical atmosphere and support the contest's information-enrichment dimension. These tracks are used as interpretive presentation elements, not as data inputs.

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

## Methodology

### 1. Data Cleaning

The historical directory entries required significant preprocessing before they could be used for mapping and comparison.

The cleaning workflow included:

- flattening nested corrected location records
- normalizing person names
- standardizing and cleaning address text
- preserving location confidence fields
- identifying and removing exact person-address-year duplicates
- filtering vague or non-geocodable addresses
- preparing cleaned address queries for geocoding

The underlying data presented common historical-text problems:

- OCR noise
- inconsistent spelling
- abbreviations
- incomplete addresses
- repeated addresses across many records

### 2. Geocoding

After normalization, cleaned addresses were geocoded and cached so repeated addresses could reuse the same coordinates instead of being processed repeatedly.

For the final app, the repository includes a compact saved dataset containing the usable geocoded results for **1850-1854**.

### 3. Occupation Normalization and Grouping

Raw occupation text was not suitable for direct analysis. To make the data interpretable, occupations were:

- lowercased and normalized
- cleaned for punctuation and common abbreviations
- mapped through manual synonym handling
- grouped using rule-based classification
- iteratively refined by reviewing frequent unresolved terms

The final groups are:

- Business / Owner
- Skilled Trades
- Professional
- Labor
- Domestic / Service
- Clerical / Administrative
- Transport / Maritime
- Public / Civic
- Other / Unknown

This grouping layer is what powers both the occupation chart and the neighborhood choropleth.

## Tools and Technologies

- Python
- Pandas
- Streamlit
- Plotly
- Pydeck

## Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
streamlit run streamlit_app.py
```

## Design Decisions

Several design choices were made deliberately for readability and storytelling:

- The dashboard focuses on **1850-1854** instead of all forty years.
  This keeps the narrative tight and avoids turning the project into a rushed coverage exercise.
- The point map remains **individual-record based** rather than aggregated.
  This preserves the immediacy of the historical directory entries.
- Occupation colors stay **consistent across years** so category meaning is stable.
- Year-specific accent colors are used to give each year a different mood without sacrificing comparability.
- The interface uses a warm paper-and-ink palette and serif typography to evoke a historical atlas rather than a generic dashboard.

## Limitations

- Historical addresses do not always map neatly onto modern geographies.
- Some occupation labels remain ambiguous and are grouped into `Other / Unknown`.
- The neighborhood analysis applies modern polygon boundaries to historical point data.
- The current published app focuses on 1850-1854 rather than the full 1850-1890 span.
- The audio layer is interpretive and atmospheric, not analytical.

## Documentation for Contest Submission

This repository is intended to satisfy the contest's documentation expectations by describing:

- the primary dataset used
- additional geographic sources
- the processing and cleaning workflow
- the tools required to run the project
- major design decisions
- limitations and interpretive boundaries
- generative AI assistance used during development

## Generative AI Disclosure

Generative AI was used during development as a programming and workflow assistant.

OpenAI Codex assisted with:

- drafting and refining data cleaning scripts
- normalizing historical address and occupation fields
- structuring parts of the geocoding workflow and caching logic
- helping build and debug the Streamlit dashboard
- refining layout, styling, and documentation

All substantive analytical framing, project direction, interpretation, curation of the final output, and final submission decisions were made by the project author.

### Credit for AI-Assisted Data Cleaning

Credit is due to **OpenAI Codex** for assistance with the data cleaning pipeline, especially:

- address normalization logic
- duplicate handling logic
- geocoding workflow structure
- occupation grouping workflow

The final project reflects human judgment in deciding what to clean, what to keep, how to frame the story, and how to present the data responsibly.

## Portfolio Framing

Beyond the contest, this project demonstrates:

- historical data cleaning under noisy real-world conditions
- geospatial visualization design
- interactive dashboard development
- categorical feature engineering from messy text
- thoughtful documentation and methodological transparency

## Acknowledgment

This project was created as an effort to make an NYU-supported historical urban dataset more accessible, interpretable, and engaging for a wider audience. It treats the city directory not simply as a list of entries, but as a lens into how labor, business, and everyday life were distributed across early New York.
