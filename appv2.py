import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import plotly.graph_objects as go

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

    overall_df = overall_values[reason_cols].reset_index()
    overall_df.columns = ["Reason", "Percent"]
    overall_df = overall_df.sort_values("Percent", ascending=False)

    # --------------------------------------------------
    # Ranked List (numbered + subtle color pills)
    # --------------------------------------------------
    st.markdown("### Ranked Drivers")

    top_k = min(25, len(overall_df))  # show top 25 by default
    for rank, (_, row) in enumerate(overall_df.head(top_k).iterrows(), start=1):
        pct = float(row["Percent"])
        # editorial grayscale emphasis
        chip_bg = "#111111" if pct >= 50 else "#3a3a3a" if pct >= 25 else "#6b6b6b"
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:10px; margin:6px 0;">
              <div style="min-width:30px; font-weight:600;">{rank}.</div>
              <div style="flex:1; font-weight:500;">{row['Reason']}</div>
              <div style="padding:2px 10px; border-radius:999px; background:{chip_bg}; color:#fff; font-weight:600;">
                {pct:.0f}%
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------
    # Overall Distribution (horizontal bar)
    # --------------------------------------------------
    st.markdown("### Overall Distribution")

    fig = px.bar(
        overall_df,
        x="Percent",
        y="Reason",
        orientation="h"
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Percent of Companies (%)",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # FRONTLINE HEADCOUNT COMPARISON (DUMBBELL)
    # --------------------------------------------------
    st.markdown("### Drivers of Increase or Decrease in Frontline Headcount in 2025 ")

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

    # Sort by absolute gap so big differences stand out
    frontline_data["Gap"] = (frontline_data["Increase"] - frontline_data["Decrease"]).abs()
    frontline_data = frontline_data.sort_values("Gap", ascending=True)

    fig_db = go.Figure()

# Connector lines
    for _, r in frontline_data.iterrows():
        fig_db.add_trace(go.Scatter(
            x=[r["Decrease"], r["Increase"]],
            y=[r["Reason"], r["Reason"]],
            mode="lines",
            line=dict(color="#B0B0B0", width=3),  # neutral gray
            showlegend=False,
            hoverinfo="skip"
        ))

# Decrease points (outside the loop)
    fig_db.add_trace(go.Scatter(
        x=frontline_data["Decrease"],
        y=frontline_data["Reason"],
        mode="markers+text",
        text=[f"{v:.0f}%" for v in frontline_data["Decrease"]],
        textposition="middle left",
        marker=dict(
            size=11,
            color="#E10600"   # bright executive red
        ),
        textfont=dict(color="#E10600"),
        name="Decrease in Frontline Headcount",
        hovertemplate="%{y}<br>Decrease: %{x}%<extra></extra>"
    ))

# Increase points (outside the loop)
    fig_db.add_trace(go.Scatter(
        x=frontline_data["Increase"],
        y=frontline_data["Reason"],
        mode="markers+text",
        text=[f"{v:.0f}%" for v in frontline_data["Increase"]],
        textposition="middle right",
        marker=dict(
            size=11,
            color="#00A651"   # strong green
        ),
        textfont=dict(color="#00A651"),
        name="Increase in Frontline Headcount",
        hovertemplate="%{y}<br>Increase: %{x}%<extra></extra>"
    ))

    fig_db.update_layout(
        xaxis_title="Percent of Companies (%)",
        yaxis_title="",
        height=max(520, 30 * len(frontline_data)),
        margin=dict(l=20, r=20, t=10, b=10),
        legend_title="",
    )

    st.plotly_chart(fig_db, use_container_width=True)

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

    st.header("Insights")

    insight_scope = st.selectbox(
        "View insights for:",
        ["Overall (All Companies)"] + sorted(df_working["Category"].unique()),
        key="insight_scope"
    )

    overall_series = overall_values[reason_cols].astype(float)

