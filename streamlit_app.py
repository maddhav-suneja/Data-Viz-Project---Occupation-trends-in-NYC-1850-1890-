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
GROUP_HEX = {
    "Business / Owner": "#8D4B32",
    "Skilled Trades": "#B17749",
    "Professional": "#5B6F97",
    "Labor": "#708C56",
    "Domestic / Service": "#7D5F8C",
    "Clerical / Administrative": "#5A7D6E",
    "Transport / Maritime": "#C7A15A",
    "Public / Civic": "#8D6B5A",
    "Other / Unknown": "#8A8176",
}
YEAR_THEME = {
    1850: {"accent": "#8D4B32", "accent_rgb": [141, 75, 50], "soft": "rgba(141, 75, 50, 0.14)"},
    1851: {"accent": "#A0622D", "accent_rgb": [160, 98, 45], "soft": "rgba(160, 98, 45, 0.14)"},
    1852: {"accent": "#7A8450", "accent_rgb": [122, 132, 80], "soft": "rgba(122, 132, 80, 0.14)"},
    1853: {"accent": "#5E7496", "accent_rgb": [94, 116, 150], "soft": "rgba(94, 116, 150, 0.14)"},
    1854: {"accent": "#7C3F46", "accent_rgb": [124, 63, 70], "soft": "rgba(124, 63, 70, 0.14)"},
}


st.set_page_config(
    page_title="Occupation Trends in Early New York",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #2f2418;
        --ink-soft: #5c4938;
        --paper-line: rgba(95, 67, 37, 0.16);
        --glow: rgba(74, 52, 29, 0.08);
    }
    .stApp {
        background:
            radial-gradient(circle at top, rgba(129, 92, 52, 0.14), transparent 28%),
            linear-gradient(180deg, #f7f0df 0%, #efe4cb 44%, #e3d0ae 100%);
        color: var(--ink);
    }
    .main .block-container {
        padding-top: 0.3rem;
        padding-bottom: 1.5rem;
        max-width: 1380px;
    }
    h1, h2, h3 {
        font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
        color: #3a2819;
        letter-spacing: 0.01em;
    }
    p, label, div[data-testid="stMarkdownContainer"] {
        font-family: "Baskerville", "Times New Roman", Georgia, serif;
    }
    .slider-shell {
        margin: 0 0 -0.22rem 0;
    }
    .slider-kicker {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: var(--ink-soft);
        margin-bottom: 0.08rem;
    }
    div[data-testid="stSelectSlider"] {
        margin-top: -0.1rem;
        margin-bottom: 0.05rem;
    }
    div[data-testid="stSelectSlider"] label {
        display: none !important;
    }
    div[data-testid="stSelectSlider"] span,
    div[data-testid="stSelectSlider"] p {
        color: #2f2418 !important;
        opacity: 1 !important;
        text-shadow: none !important;
        font-size: 0.84rem !important;
    }
    div[data-testid="stSelectSlider"] [data-baseweb="slider"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    div[data-testid="stSelectSlider"] [data-baseweb="slider"] > div {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .hero {
        background:
            radial-gradient(circle at top right, rgba(141, 75, 50, 0.08), transparent 28%),
            linear-gradient(135deg, rgba(255,250,241,0.86), rgba(242,229,202,0.62));
        border: 1px solid var(--paper-line);
        border-radius: 22px;
        padding: 0.58rem 0.9rem 0.5rem 0.9rem;
        margin-bottom: 0.28rem;
        box-shadow: 0 14px 34px var(--glow);
    }
    .hero-kicker {
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 0.66rem;
        color: var(--ink-soft);
        margin-bottom: 0.18rem;
    }
    .hero-title {
        font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
        font-size: 1.8rem;
        line-height: 0.98;
        color: #362517;
        margin: 0 0 0.14rem 0;
    }
    .hero-copy {
        color: var(--ink-soft);
        font-size: 0.84rem;
        line-height: 1.22;
        max-width: 860px;
        margin: 0;
    }
    .control-card {
        background: linear-gradient(180deg, rgba(255, 249, 237, 0.72), rgba(248, 238, 214, 0.42));
        border: 1px solid rgba(110, 79, 46, 0.14);
        border-radius: 18px;
        padding: 0.42rem 0.72rem;
        margin-bottom: 0.22rem;
        box-shadow: 0 10px 24px rgba(74, 52, 29, 0.06);
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.8rem;
    }
    div[data-testid="stHorizontalBlock"] > div:has(.metric-card) {
        margin-top: -0.28rem;
    }
    .control-label {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.66rem;
        color: var(--ink-soft);
        margin-bottom: 0.18rem;
    }
    .control-copy {
        margin: 0;
        color: var(--ink);
        line-height: 1.25;
        font-size: 0.82rem;
    }
    .viz-note {
        color: var(--ink-soft);
        font-size: 0.97rem;
        line-height: 1.4;
        margin-top: -0.2rem;
        margin-bottom: 0.32rem;
    }
    .insight-band {
        background: linear-gradient(135deg, rgba(255,250,241,0.82), rgba(242,229,202,0.52));
        border: 1px solid var(--paper-line);
        border-radius: 20px;
        padding: 0.7rem 0.9rem;
        margin: 0.12rem 0 0.35rem 0;
        box-shadow: 0 12px 28px var(--glow);
    }
    .insight-label {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.64rem;
        color: var(--ink-soft);
        margin-bottom: 0.18rem;
    }
    .insight-text {
        margin: 0;
        font-size: 0.92rem;
        line-height: 1.3;
        color: var(--ink);
    }
    .metric-card {
        background: linear-gradient(180deg, rgba(255, 249, 237, 0.78), rgba(246, 236, 214, 0.5));
        border: 1px solid rgba(110, 79, 46, 0.14);
        border-radius: 18px;
        padding: 0.6rem 0.8rem;
        min-height: 78px;
        box-shadow: 0 12px 28px rgba(74, 52, 29, 0.06);
    }
    .metric-label {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.62rem;
        color: var(--ink-soft);
        margin-bottom: 0.22rem;
    }
    .metric-value {
        font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
        font-size: 1.2rem;
        line-height: 1;
        color: #362517;
        margin-bottom: 0.14rem;
    }
    .metric-copy {
        margin: 0;
        color: var(--ink-soft);
        font-size: 0.75rem;
        line-height: 1.14;
    }
    .metric-card-offset {
        margin-top: 0.38rem;
    }
    .metric-copy-tight {
        margin: 0 0 0.15rem 0;
        color: var(--ink-soft);
        font-size: 0.72rem;
        line-height: 1.1;
    }
    .leaderboard {
        margin: 0.04rem 0 0 0;
        padding-left: 1rem;
        color: var(--ink-soft);
        font-size: 0.82rem;
        line-height: 1.18;
    }
    .leaderboard li::marker {
        color: #8d6b5a;
    }
    .legend-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.35rem 0.8rem;
        margin-top: 0.18rem;
        margin-left: 0.6rem;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 0.9rem;
        color: var(--ink-soft);
        line-height: 1.2;
    }
    .legend-swatch {
        width: 0.78rem;
        height: 0.78rem;
        border-radius: 999px;
        border: 1px solid rgba(58, 40, 25, 0.18);
        flex: 0 0 auto;
    }
    div[data-testid="stDeckGlJsonChart"],
    div[data-testid="stAudio"] {
        background: rgba(255, 250, 241, 0.38);
        border: 1px solid rgba(95, 67, 37, 0.1);
        border-radius: 20px;
        padding: 0.45rem;
        box-shadow: 0 14px 30px rgba(74, 52, 29, 0.07);
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
    theme = YEAR_THEME.get(int(df["year"].iloc[0]), YEAR_THEME[1850]) if not df.empty else YEAR_THEME[1850]
    r, g, b = theme["accent_rgb"]
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_radius=16,
        radius_min_pixels=1,
        radius_max_pixels=2,
        get_fill_color=[r, g, b, 105],
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


def summarize_year(selected_year, selected_occ, zone_geojson, map_df):
    mapped_total = int(len(map_df))

    top_occ = None
    top_share = None
    if not selected_occ.empty:
        top_row = selected_occ.sort_values("count", ascending=False).iloc[0]
        top_occ = top_row["occupation_group"]
        top_share = float(top_row["count"] / selected_occ["count"].sum())

    neighborhood_leaders = []
    if zone_geojson["features"]:
        group_to_places = {}
        point_totals = {}
        for feature in zone_geojson["features"]:
            group = feature["properties"]["dominant_group"]
            zone_name = feature["properties"]["zone_name"]
            total_points = int(feature["properties"]["total_points"])
            group_to_places.setdefault(group, []).append(zone_name)
            point_totals.setdefault(group, []).append(total_points)

        neighborhood_leaders = sorted(
            (
                {
                    "group": group,
                    "count": len(places),
                    "points": sum(point_totals[group]),
                    "places": sorted(places)[:3],
                }
                for group, places in group_to_places.items()
            ),
            key=lambda item: (-item["count"], -item["points"], item["group"]),
        )[:5]

    if top_occ and neighborhood_leaders:
        insight_text = (
            f"In {selected_year}, the map suggests the strongest directory concentration in lower Manhattan. "
            f"{top_occ} is the largest occupation group overall ({top_share:.1%} of grouped entries), "
            f"and {neighborhood_leaders[0]['group']} leads the most neighborhoods on the choropleth."
        )
    elif top_occ:
        insight_text = (
            f"In {selected_year}, the map suggests a strong concentration of directory activity in lower Manhattan, "
            f"and {top_occ} is the largest occupation group overall ({top_share:.1%} of grouped entries)."
        )
    else:
        insight_text = (
            f"In {selected_year}, the strongest visible pattern is spatial concentration: "
            f"directory activity clusters in parts of lower Manhattan rather than spreading evenly across the island."
        )

    return (
        mapped_total,
        top_occ,
        top_share,
        neighborhood_leaders,
        insight_text,
    )


st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Historical Urban Directory Atlas</div>
        <div class="hero-title">Occupation Trends in Early New York, 1850-1854</div>
        <p class="hero-copy">
            This dashboard follows how geocoded directory entries were distributed across Manhattan between 1850 and 1854.
            Use the shared year control to trace individual directory points, compare the occupational makeup of each year,
            and see which neighborhoods were dominated by different kinds of work.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not APP_POINTS_PATH.exists():
    st.error("Missing app data file. Build the compact 1850-1854 points file before opening this app.")
    st.stop()

st.markdown("<div class='slider-shell'><div class='slider-kicker'>Year</div></div>", unsafe_allow_html=True)
selected_year = st.select_slider(
    "Year",
    options=YEAR_RANGE,
    value=min(YEAR_RANGE),
    label_visibility="collapsed",
)
theme = YEAR_THEME[selected_year]

song_path = song_file_for_year(selected_year)

st.markdown(
    f"""
    <style>
    .stApp [data-baseweb="slider"] div[role="slider"] {{
        background: {theme["accent"]} !important;
        border-color: {theme["accent"]} !important;
        box-shadow: 0 0 0 5px {theme["soft"]};
    }}
    .stApp [data-baseweb="slider"] > div > div {{
        background: linear-gradient(90deg, {theme["accent"]}, rgba(255,255,255,0.35)) !important;
    }}
    .hero {{
        box-shadow: 0 14px 34px {theme["soft"]};
    }}
    .hero-kicker, .control-label {{
        color: {theme["accent"]};
    }}
    .hero-title,
    .metric-value {{
        color: {theme["accent"]};
    }}
    .control-card {{
        border-color: {theme["soft"]};
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.28);
    }}
    .metric-card,
    .insight-band {{
        border-color: {theme["soft"]};
    }}
    .leaderboard strong {{
        color: {theme["accent"]};
        font-weight: 700;
    }}
    h2 {{
        color: {theme["accent"]};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([1.9, 0.85])
with top_left:
    st.markdown(
        f"""
        <div class="control-card">
            <div class="control-label">Shared Year View</div>
            <p class="control-copy">
                All views update together for <strong>{selected_year}</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with top_right:
    if song_path is not None:
        st.markdown(
            f"""
            <div class="control-card">
                <div class="control-label">Listening Layer</div>
                <p class="control-copy">Audio track for <strong>{selected_year}</strong>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
(
    mapped_total,
    top_occ,
    top_share,
    neighborhood_leaders,
    insight_text,
) = summarize_year(selected_year, selected_occ, zone_geojson, map_df)

summary_left, summary_middle, summary_right = st.columns([0.9, 1.05, 1.05], gap="medium")
with summary_left:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Mapped Entries</div>
            <div class="metric-value">{mapped_total:,}</div>
            <p class="metric-copy">Individual directory records plotted for {selected_year}.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="metric-card metric-card-offset">
            <div class="metric-label">Largest Occupation Group</div>
            <div class="metric-value">{top_occ or "N/A"}</div>
            <p class="metric-copy">{f"{top_share:.1%} of grouped entries in {selected_year}." if top_share is not None else "Grouped occupation summary unavailable."}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with summary_middle:
    leaderboard_html = (
        "<ol class='leaderboard'>"
        + "".join(
            f"<li><strong>{item['group']}</strong> leads {item['count']} neighborhoods</li>"
            for item in neighborhood_leaders
        )
        + "</ol>"
        if neighborhood_leaders
        else "<p class='metric-copy'>No neighborhood data available for this year.</p>"
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Neighborhood Dominance</div>
            <p class="metric-copy-tight">How many neighborhoods are led by each occupation group in the selected year.</p>
            {leaderboard_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
with summary_right:
    st.markdown(
        f"""
        <div class="insight-band">
            <div class="insight-label">What To Notice</div>
            <p class="insight-text">{insight_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

left, middle, right = st.columns([1.2, 0.95, 1.0], gap="medium")

with left:
    st.subheader("Directory Point Map")
    st.markdown(
        '<p class="viz-note">Each point represents one geocoded directory entry for the selected year.</p>',
        unsafe_allow_html=True,
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
    st.markdown(
        '<p class="viz-note">Grouped occupation categories summarize the overall composition of work in the selected year.</p>',
        unsafe_allow_html=True,
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
            color_discrete_map=GROUP_HEX,
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
        legend_order = [
            "Business / Owner",
            "Skilled Trades",
            "Professional",
            "Labor",
            "Domestic / Service",
            "Clerical / Administrative",
            "Transport / Maritime",
            "Public / Civic",
            "Other / Unknown",
        ]
        st.markdown(
            "<div class='legend-grid'>"
            + "".join(
                f"<div class='legend-item'><span class='legend-swatch' style='background:{GROUP_HEX[group]}'></span>{group}</div>"
                for group in legend_order
                if group in selected_occ['occupation_group'].values
            )
            + "</div>",
            unsafe_allow_html=True,
        )

with right:
    st.subheader("Neighborhood Ratios")
    st.markdown(
        '<p class="viz-note">Neighborhood polygons are colored by the occupation group with the strongest share in that area.</p>',
        unsafe_allow_html=True,
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
