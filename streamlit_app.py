from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
APP_POINTS_PATH = DATA_DIR / "app_points_1850_1854.csv"
OCC_SUMMARY_PATH = DATA_DIR / "occupation_group_summary_1850_1854.csv"
SONG_DIR = PROJECT_DIR / "Song"
YEAR_RANGE = list(range(1850, 1855))
NTA_GEOJSON_PATH = DATA_DIR / "manhattan_nta.geojson"
GROUP_COLORS = {
    "Business / Owner": [185, 68, 68, 170],
    "Skilled Trades": [209, 124, 84, 170],
    "Other / Unknown": [140, 140, 140, 150],
    "Professional": [77, 111, 165, 170],
    "Labor": [123, 158, 99, 170],
    "Domestic / Service": [156, 107, 153, 170],
    "Clerical / Administrative": [77, 140, 138, 170],
    "Transport / Maritime": [208, 168, 92, 170],
    "Public / Civic": [109, 89, 122, 170],
}


st.set_page_config(
    page_title="NYC Directory Map, 1850-1854",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top, rgba(129, 92, 52, 0.08), transparent 34%),
            linear-gradient(180deg, #f4ecd8 0%, #efe4cc 45%, #e6d7ba 100%);
        color: #2f2418;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
        color: #3a2819;
        letter-spacing: 0.01em;
    }
    p, label, div[data-testid="stMarkdownContainer"] {
        font-family: "Baskerville", "Times New Roman", Georgia, serif;
    }
    div[data-testid="stSlider"] {
        background: rgba(110, 79, 46, 0.08);
        border: 1px solid rgba(110, 79, 46, 0.18);
        padding: 0.7rem 1rem 0.4rem 1rem;
        border-radius: 14px;
    }
    div[data-testid="stPlotlyChart"],
    div[data-testid="stDeckGlJsonChart"] {
        background: rgba(255, 252, 244, 0.55);
        border: 1px solid rgba(95, 67, 37, 0.14);
        border-radius: 18px;
        padding: 0.35rem;
        box-shadow: 0 10px 30px rgba(74, 52, 29, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def song_file_for_year(year: int):
    path = SONG_DIR / f"{year}.mp3"
    return path if path.exists() else None


@st.cache_data
def load_app_points():
    if not APP_POINTS_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(APP_POINTS_PATH)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["person_name"] = df["person_name"].fillna("Unknown")
    df["occupation"] = df["occupation"].fillna("Unknown")
    df["occupation_group"] = df["occupation_group"].fillna("Other / Unknown")
    return df


@st.cache_data
def load_occupation_summary():
    if not OCC_SUMMARY_PATH.exists():
        return pd.DataFrame(columns=["year", "occupation_group", "count"])

    df = pd.read_csv(OCC_SUMMARY_PATH)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


@st.cache_data
def load_grouped_points():
    return load_app_points()


@st.cache_data
def load_manhattan_ntas():
    if not NTA_GEOJSON_PATH.exists():
        return []

    import json

    data = json.loads(NTA_GEOJSON_PATH.read_text(encoding="utf-8"))
    return data.get("features", [])


def build_map_layer(df):
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_radius=16,
        radius_min_pixels=1,
        radius_max_pixels=2,
        get_fill_color=[142, 68, 45, 95],
        pickable=True,
    )


def point_in_ring(lon, lat, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        intersects = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def point_in_feature(lon, lat, geometry):
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        if not coords:
            return False
        if not point_in_ring(lon, lat, coords[0]):
            return False
        for hole in coords[1:]:
            if point_in_ring(lon, lat, hole):
                return False
        return True

    if geom_type == "MultiPolygon":
        for polygon in coords:
            if not polygon:
                continue
            if not point_in_ring(lon, lat, polygon[0]):
                continue
            in_hole = any(point_in_ring(lon, lat, hole) for hole in polygon[1:])
            if not in_hole:
                return True
    return False


def geometry_bbox(geometry):
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates", [])
    points = []

    if geom_type == "Polygon":
        for ring in coords:
            points.extend(ring)
    elif geom_type == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                points.extend(ring)

    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    return min(xs), min(ys), max(xs), max(ys)


def build_zone_geojson(points_df, nta_features, selected_year):
    year_points = points_df[points_df["year"] == selected_year].copy()
    if year_points.empty:
        return {"type": "FeatureCollection", "features": []}

    zone_features = []
    for feature in nta_features:
        geometry = feature["geometry"]
        lon_min, lat_min, lon_max, lat_max = geometry_bbox(geometry)
        candidate_points = year_points[
            year_points["latitude"].between(lat_min, lat_max)
            & year_points["longitude"].between(lon_min, lon_max)
        ]
        if candidate_points.empty:
            continue

        mask = candidate_points.apply(
            lambda row: point_in_feature(row["longitude"], row["latitude"], geometry),
            axis=1,
        )
        zone_df = candidate_points[mask].copy()
        if zone_df.empty:
            continue

        counts = zone_df["occupation_group"].value_counts()
        total = int(counts.sum())
        dominant_group = counts.index[0]
        dominant_count = int(counts.iloc[0])
        dominant_share = dominant_count / total
        top_three = counts.head(3)
        tooltip_lines = "<br/>".join(
            f"{group}: {count / total:.1%}" for group, count in top_three.items()
        )

        zone_features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "zone_name": feature["properties"].get("NTAName", "Unknown"),
                    "dominant_group": dominant_group,
                    "dominant_share_pct": f"{dominant_share:.1%}",
                    "total_points": total,
                    "fill_color": GROUP_COLORS.get(dominant_group, [140, 140, 140, 150]),
                    "tooltip_html": (
                        f"<b>{feature['properties'].get('NTAName', 'Unknown')}</b><br/>"
                        f"Dominant: {dominant_group} ({dominant_share:.1%})<br/>"
                        f"Points: {total:,}<br/>{tooltip_lines}"
                    ),
                },
            }
        )

    return {"type": "FeatureCollection", "features": zone_features}


def build_zone_layer(zone_geojson):
    return pdk.Layer(
        "GeoJsonLayer",
        data=zone_geojson,
        get_fill_color="properties.fill_color",
        get_line_color=[255, 255, 255, 180],
        line_width_min_pixels=1,
        stroked=True,
        filled=True,
        pickable=True,
        opacity=0.68,
    )


st.title("Occupation Trends in Early New York, 1850-1854")
st.caption(
    "This dashboard follows how geocoded directory entries were distributed across Manhattan between 1850 and 1854. "
    "Use the year slider to trace individual directory points, compare the occupational makeup of each year, "
    "and see which neighborhoods were dominated by different kinds of work."
)

if not APP_POINTS_PATH.exists():
    st.error("Missing app data file. Build the compact 1850-1854 points file before opening this app.")
    st.stop()

selected_year = st.slider(
    "Year",
    min_value=min(YEAR_RANGE),
    max_value=max(YEAR_RANGE),
    value=min(YEAR_RANGE),
    step=1,
)

song_path = song_file_for_year(selected_year)
top_left, top_right = st.columns([1.6, 1])
with top_left:
    st.markdown(
        "This shared year control updates every view on the page so the map, occupation mix, and neighborhood ratios stay synchronized."
    )
with top_right:
    if song_path is not None:
        st.audio(str(song_path), format="audio/mp3", start_time=0)

app_points_df = load_app_points()
occupation_summary_df = load_occupation_summary()
grouped_points_df = load_grouped_points()
manhattan_nta_features = load_manhattan_ntas()
map_df = app_points_df[app_points_df["year"] == selected_year].copy()

if map_df.empty:
    st.info("No mapped points are available yet for this year.")
    st.stop()

selected_occ = occupation_summary_df[occupation_summary_df["year"] == selected_year].copy()
zone_geojson = build_zone_geojson(grouped_points_df, manhattan_nta_features, selected_year)

left, middle, right = st.columns([1.2, 0.95, 1.0], gap="medium")

with left:
    st.subheader("Directory Point Map")
    st.caption(
        "Each point is one geocoded directory entry for the selected year."
    )
    view_state = pdk.ViewState(
        latitude=float(map_df["latitude"].median()),
        longitude=float(map_df["longitude"].median()),
        zoom=10.5,
        pitch=0,
    )

    tooltip = {
        "html": "<b>{person_name}</b><br/>{occupation}",
        "style": {"backgroundColor": "#4b3521", "color": "#f8f1e3"},
    }

    st.pydeck_chart(
        pdk.Deck(
            map_style="light",
            initial_view_state=view_state,
            layers=[build_map_layer(map_df)],
            tooltip=tooltip,
        ),
        use_container_width=True,
    )

with middle:
    st.subheader("Occupation Diversity")
    st.caption(
        "Grouped occupation mix for the selected year."
    )
    if selected_occ.empty:
        st.info("Occupation summary data is not available for this year.")
    else:
        pie_fig = px.pie(
            selected_occ,
            names="occupation_group",
            values="count",
            hole=0.35,
            color="occupation_group",
            color_discrete_sequence=[
                "#8d4b32",
                "#b17749",
                "#c7a15a",
                "#708c56",
                "#5a7d6e",
                "#5b6f97",
                "#7d5f8c",
                "#8d6b5a",
                "#8a8176",
            ],
        )
        pie_fig.update_traces(
            textposition="inside",
            textinfo="percent",
            textfont_size=11,
            hovertemplate="%{label}<br>%{percent}<extra></extra>",
        )
        pie_fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#3a2819", family="Baskerville, Times New Roman, serif"),
            uniformtext_minsize=10,
            uniformtext_mode="hide",
        )
        st.plotly_chart(pie_fig, use_container_width=True, config={"displayModeBar": False})

with right:
    st.subheader("Neighborhood Ratios")
    st.caption(
        "Neighborhood polygons colored by dominant occupation group."
    )
    if not zone_geojson["features"]:
        st.info("No neighborhood ratio data is available yet for this year.")
    else:
        zone_view = pdk.ViewState(
            latitude=40.78,
            longitude=-73.975,
            zoom=10.6,
            pitch=0,
        )
        zone_tooltip = {
            "html": "{tooltip_html}",
            "style": {"backgroundColor": "#4b3521", "color": "#f8f1e3"},
        }
        st.pydeck_chart(
            pdk.Deck(
                map_style="light",
                initial_view_state=zone_view,
                layers=[build_zone_layer(zone_geojson)],
                tooltip=zone_tooltip,
            ),
            use_container_width=True,
        )
