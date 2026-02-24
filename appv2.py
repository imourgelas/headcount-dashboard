import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Drivers of Headcount Change in 2025", layout="wide")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    path = Path(__file__).parent / "companies_data_clean.csv"
    return pd.read_csv(path)

df = load_data()

reason_cols = [c for c in df.columns if c not in ["Category", "Subcategory"]]

# Identify overall row
overall_row = df[df["Category"] == "Overall"]

if overall_row.empty:
    overall_row = df[df["Subcategory"] == "Overall"]

if overall_row.empty:
    st.error("No Overall row found.")
    st.stop()

overall_values = overall_row.iloc[0]

df_working = df[
    (df["Category"] != "Overall") &
    (df["Subcategory"] != "Overall")
].copy()

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab_overall, tab_category, tab_compare, tab_insights = st.tabs([
    "Overall Landscape",
    "Category Snapshot",
    "Subcategory Comparison",
    "Insights"
])

# ==================================================
# TAB 1 — OVERALL LANDSCAPE
# ==================================================

with tab_overall:

    st.title("Drivers of Headcount Change in 2025")
    st.subheader("Overall (All Companies)")

    overall_df = (
        overall_values[reason_cols]
        .reset_index()
    )

    overall_df.columns = ["Reason", "Percent"]
    overall_df = overall_df.sort_values("Percent", ascending=False)

    # Ranked List
    st.markdown("### Ranked Drivers")
    for i, row in overall_df.iterrows():
        st.write(f"**{row['Reason']}** — {row['Percent']:.0f}%")

    # Horizontal Bar Chart
    st.markdown("### Overall Distribution")

    fig = px.bar(
        overall_df,
        x="Percent",
        y="Reason",
        orientation="h"
    )

    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # FRONTLINE HEADCOUNT COMPARISON
    # --------------------------------------------------

    st.markdown("### Frontline Headcount Drivers: Increase vs Decrease")

    frontline_data = pd.DataFrame({
        "Reason": [
            "Change in company revenue",
            "Expansion into new markets or segments",
            "Launch of new products or services",
            "Budget increases allowing for headcount growth",
            "Difficulty finding qualified candidates",
            "Seasonal or cyclical hiring needs",
            "Cost-cutting initiatives to preserve margins",
            "Industry-specific change in demand",
            "Artificial intelligence reducing workforce number",
            "Rising labor costs (e.g., wages, benefits)",
            "Restructuring, mergers or acquisitions",
            "Shifting business priorities or leadership direction",
            "Economic uncertainty or market volatility",
            "Changes in government policy or regulation",
            "Delayed or canceled projects impacting workforce needs",
            "Increased availability of skilled talent",
            "Other",
            "Rising operational costs (e.g., materials, rent, logistics)",
            "Automation or digital transformation reducing manual roles"
        ],
        "Increase": [71,31,23,21,19,15,13,13,10,8,8,8,8,6,4,4,4,2,2],
        "Decrease": [59,17,14,3,17,0,52,24,31,21,28,28,21,21,14,0,14,28,24]
    })

    frontline_long = frontline_data.melt(
        id_vars="Reason",
        var_name="Direction",
        value_name="Percent"
    )

    fig2 = px.bar(
        frontline_long,
        x="Percent",
        y="Reason",
        color="Direction",
        barmode="group",
        orientation="h"
    )

    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)

# ==================================================
# TAB 2 — CATEGORY SNAPSHOT
# ==================================================

with tab_category:

    st.header("Category Snapshot")

    category = st.selectbox(
        "Select Category",
        sorted(df_working["Category"].unique())
    )

    subcat_df = df_working[df_working["Category"] == category]

    long_df = subcat_df.melt(
        id_vars=["Category", "Subcategory"],
        value_vars=reason_cols,
        var_name="Reason",
        value_name="Percent"
    )

    fig = px.bar(
        long_df,
        x="Percent",
        y="Reason",
        color="Subcategory",
        orientation="h",
        barmode="group"
    )

    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 3 — SUBCATEGORY COMPARISON
# ==================================================

with tab_compare:

    st.header("Compare Up to Three Subcategories")

    category = st.selectbox(
        "Select Category for Comparison",
        sorted(df_working["Category"].unique()),
        key="compare_cat"
    )

    subcat_df = df_working[df_working["Category"] == category]

    selected = st.multiselect(
        "Select up to 3 subcategories",
        subcat_df["Subcategory"].unique(),
        default=subcat_df["Subcategory"].unique()[:2]
    )

    selected = selected[:3]

    compare_df = subcat_df[subcat_df["Subcategory"].isin(selected)]

    long_compare = compare_df.melt(
        id_vars=["Category", "Subcategory"],
        value_vars=reason_cols,
        var_name="Reason",
        value_name="Percent"
    )

    fig = px.bar(
        long_compare,
        x="Percent",
        y="Reason",
        color="Subcategory",
        orientation="h",
        barmode="group"
    )

    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TAB 4 — INSIGHTS
# ==================================================

with tab_insights:

    st.header("Executive Summary")

    top_reason = overall_df.iloc[0]

    paragraph = (
        f"Across all companies, the dominant driver of headcount change in 2025 "
        f"is {top_reason['Reason']} ({top_reason['Percent']:.0f}%). "
        f"The data shows divergence between organizations increasing and decreasing "
        f"frontline headcount, particularly around cost pressures and restructuring. "
        f"Revenue-driven expansion continues to drive workforce growth, while "
        f"margin preservation and labor cost pressures are more closely associated "
        f"with reductions."
    )

    st.write(paragraph)
