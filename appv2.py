import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Headcount Drivers v2", layout="wide")

# -----------------------------
# DATA LOADING
# -----------------------------
@st.cache_data
def load_data():
    path = Path(__file__).parent / "companies_data_clean.csv"
    df = pd.read_csv(path)
    return df

df = load_data()

# -----------------------------
# IDENTIFY OVERALL ROW
# -----------------------------
overall_row = df[df["Category"] == "Overall"]

if overall_row.empty:
    overall_row = df[df["Subcategory"] == "Overall"]

if overall_row.empty:
    st.error("No 'Overall' row found in dataset.")
    st.stop()

overall_values = overall_row.iloc[0]

# Remove overall from working dataset
df_working = df[
    (df["Category"] != "Overall") &
    (df["Subcategory"] != "Overall")
].copy()

reason_cols = [c for c in df.columns if c not in ["Category", "Subcategory"]]

# -----------------------------
# SIDEBAR
# -----------------------------
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

top_n = st.sidebar.slider("Top N Reasons", 5, 20, 12)

view_mode = st.sidebar.radio(
    "View Mode",
    ["Raw %", "Delta vs Overall"]
)

filtered = subcat_df[subcat_df["Subcategory"].isin(selected_subcats)]

# -----------------------------
# PREP LONG FORMAT
# -----------------------------
long_df = filtered.melt(
    id_vars=["Category", "Subcategory"],
    value_vars=reason_cols,
    var_name="Reason",
    value_name="Percent"
)

# Add Overall benchmark
overall_long = overall_values[reason_cols].reset_index()
overall_long.columns = ["Reason", "OverallPercent"]

long_df = long_df.merge(overall_long, on="Reason")

long_df["Delta"] = long_df["Percent"] - long_df["OverallPercent"]

# Sort reasons by Overall %
top_reasons = (
    overall_long.sort_values("OverallPercent", ascending=False)
    .head(top_n)["Reason"]
)

long_df = long_df[long_df["Reason"].isin(top_reasons)]

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Snapshot",
    "Benchmark vs Overall",
    "Subcategory Comparison",
    "Insights"
])

# -----------------------------
# TAB 1 - SNAPSHOT
# -----------------------------
with tab1:
    st.subheader(f"{category}: Headcount Drivers")

    y_col = "Percent" if view_mode == "Raw %" else "Delta"

    fig = px.bar(
        long_df,
        x="Reason",
        y=y_col,
        color="Subcategory",
        barmode="group"
    )

    if view_mode == "Raw %":
        fig.add_scatter(
            x=top_reasons,
            y=overall_long.set_index("Reason").loc[top_reasons]["OverallPercent"],
            mode="markers",
            marker=dict(color="black", size=8),
            name="Overall"
        )

    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title="Percent (%)" if view_mode == "Raw %" else "Delta vs Overall (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 2 - DELTA HEATMAP
# -----------------------------
with tab2:
    st.subheader("Over / Under Index vs Overall")

    heatmap_data = (
        long_df.pivot(
            index="Subcategory",
            columns="Reason",
            values="Delta"
        )
    )

    fig = px.imshow(
        heatmap_data,
        color_continuous_scale="RdBu",
        aspect="auto",
        origin="lower"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 3 - SUBCATEGORY VS SUBCATEGORY
# -----------------------------
with tab3:
    st.subheader("Compare Two Subcategories")

    col1, col2 = st.columns(2)

    with col1:
        sub_a = st.selectbox("Subcategory A", selected_subcats)

    with col2:
        sub_b = st.selectbox("Subcategory B", selected_subcats, index=1 if len(selected_subcats) > 1 else 0)

    compare_df = long_df[long_df["Subcategory"].isin([sub_a, sub_b])]

    fig = px.bar(
        compare_df,
        x="Reason",
        y="Percent",
        color="Subcategory",
        barmode="group"
    )

    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TAB 4 - INSIGHTS
# -----------------------------
with tab4:
    st.subheader("Automated Insights")

    # Most polarizing reason
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

    st.markdown(f"""
    **Most Polarizing Reason:**  
    {most_polarizing}

    **Most Distinctive Subcategory (vs Overall):**  
    {most_distinct}
    """)
