import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIG + CHIEF EXECUTIVE STYLE
# --------------------------------------------------

st.set_page_config(page_title="Drivers of Headcount Change in 2025", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    color: #1A1A1A;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif;
    color: #000000;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    path = Path(__file__).parent / "companies_data_clean.csv"
    return pd.read_csv(path)

df = load_data()

# --------------------------------------------------
# IDENTIFY OVERALL ROW
# --------------------------------------------------

overall_row = df[df["Category"] == "Overall"]

if overall_row.empty:
    overall_row = df[df["Subcategory"] == "Overall"]

if overall_row.empty:
    st.error("No 'Overall' row found.")
    st.stop()

overall_values = overall_row.iloc[0]

df_working = df[
    (df["Category"] != "Overall") &
    (df["Subcategory"] != "Overall")
].copy()

reason_cols = [c for c in df.columns if c not in ["Category", "Subcategory"]]

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Filters")

category = st.sidebar.selectbox(
    "Select Category",
    sorted(df_working["Category"].unique())
)

subcat_df = df_working[df_working["Category"] == category]

subcategories = subcat_df["Subcategory"].unique()

selected_subcats = st.sidebar.multiselect(
    "Select Subcategories",
    subcategories,
    default=subcategories
)

top_n = st.sidebar.slider("Top N Drivers", 5, 20, 12)

filtered = subcat_df[subcat_df["Subcategory"].isin(selected_subcats)]

# --------------------------------------------------
# LONG FORMAT
# --------------------------------------------------

long_df = filtered.melt(
    id_vars=["Category", "Subcategory"],
    value_vars=reason_cols,
    var_name="Reason",
    value_name="Percent"
)

overall_long = overall_values[reason_cols].reset_index()
overall_long.columns = ["Reason", "OverallPercent"]

long_df = long_df.merge(overall_long, on="Reason")
long_df["Delta"] = long_df["Percent"] - long_df["OverallPercent"]

# Sort by Overall %
top_reasons = (
    overall_long.sort_values("OverallPercent", ascending=False)
    .head(top_n)["Reason"]
)

long_df = long_df[long_df["Reason"].isin(top_reasons)]

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "Snapshot",
    "Subcategory Comparison",
    "Insights"
])

# --------------------------------------------------
# SNAPSHOT TAB
# --------------------------------------------------

with tab1:

    st.title("Drivers of Headcount Change in 2025")
    st.subheader(category)

    # GROUPED BAR CHART
    fig = px.bar(
        long_df,
        x="Reason",
        y="Percent",
        color="Subcategory",
        barmode="group"
    )

    fig.add_scatter(
        x=top_reasons,
        y=overall_long.set_index("Reason").loc[top_reasons]["OverallPercent"],
        mode="markers",
        marker=dict(color="black", size=8),
        name="Overall"
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title="Percent of Companies (%)",
        legend_title=""
    )

    st.plotly_chart(fig, use_container_width=True)

    # HEATMAP BY CATEGORY (RAW %)
    st.subheader("Distribution Across Subcategories")

    heatmap_data = (
        long_df.pivot(
            index="Subcategory",
            columns="Reason",
            values="Percent"
        )
    )

    fig2 = px.imshow(
        heatmap_data,
        color_continuous_scale="Blues",
        aspect="auto"
    )

    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# SUBCATEGORY COMPARISON TAB
# --------------------------------------------------

with tab2:

    st.subheader("Compare Up to Three Subcategories")

    compare_selection = st.multiselect(
        "Select up to 3 subcategories",
        selected_subcats,
        default=selected_subcats[:2]
    )

    compare_selection = compare_selection[:3]

    compare_df = long_df[long_df["Subcategory"].isin(compare_selection)]

    fig = px.bar(
        compare_df,
        x="Reason",
        y="Percent",
        color="Subcategory",
        barmode="group"
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title="Percent of Companies (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# INSIGHTS TAB
# --------------------------------------------------

with tab3:

    st.subheader("Executive Insights")

    # Most common overall driver
    top_overall = overall_long.sort_values(
        "OverallPercent",
        ascending=False
    ).iloc[0]

    # Most polarizing
    spread = (
        long_df.groupby("Reason")["Percent"]
        .agg(lambda x: x.max() - x.min())
        .sort_values(ascending=False)
    )

    most_polarizing = spread.index[0]

    # Most distinctive subcategory
    distinctiveness = (
        long_df.groupby("Subcategory")["Delta"]
        .apply(lambda x: abs(x).sum())
        .sort_values(ascending=False)
    )

    most_distinct = distinctiveness.index[0]

    paragraph = f"""
    Across the {category} category, headcount decisions in 2025 are primarily driven by 
    {top_overall['Reason']} ({top_overall['OverallPercent']:.0f}% overall). 

    Variation within the category is most pronounced around {most_polarizing}, indicating 
    meaningful divergence in how subcategories are responding to that factor. 

    Among subcategories, {most_distinct} stands out as the most distinctive relative to the overall benchmark, 
    suggesting structural or strategic differences compared with the broader company population.
    """

    st.write(paragraph)
