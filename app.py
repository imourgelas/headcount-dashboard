import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Headcount Change Reasons Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    h1 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    h2, h3 {
        color: #34495e;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('companies_data_clean.csv')
    return df

df = load_data()

# Get list of reasons (all columns except Category and Subcategory)
reasons = [col for col in df.columns if col not in ['Category', 'Subcategory']]

# Title and description
st.title("📊 Headcount Change Reasons Analysis Dashboard")
st.markdown("""
This dashboard analyzes the factors driving headcount changes across different company characteristics.
Explore how various reasons impact workforce decisions by company revenue, size, and industry.
""")

st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Category selection
selected_category = st.sidebar.selectbox(
    "Select Category",
    options=df['Category'].unique(),
    index=0
)

# Filter data by category
category_df = df[df['Category'] == selected_category].copy()

# Subcategory multi-select
available_subcategories = category_df['Subcategory'].unique().tolist()
selected_subcategories = st.sidebar.multiselect(
    f"Select {selected_category} Groups",
    options=available_subcategories,
    default=available_subcategories
)

# Filter by selected subcategories
if selected_subcategories:
    filtered_df = category_df[category_df['Subcategory'].isin(selected_subcategories)]
else:
    filtered_df = category_df

# Reason selection for detailed analysis
selected_reason = st.sidebar.selectbox(
    "Focus on Specific Reason",
    options=reasons,
    index=0
)

# Top N reasons to show
top_n = st.sidebar.slider(
    "Number of Top Reasons to Display",
    min_value=3,
    max_value=10,
    value=5
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 About")
st.sidebar.info("""
**Data Source:** Survey of 1,030 companies analyzing factors 
influencing headcount changes across various business characteristics.
""")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Detailed Analysis", "📊 Comparative View", "💡 Insights"])

with tab1:
    st.header(f"Overview: {selected_category}")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Groups Analyzed",
            len(filtered_df)
        )
    
    with col2:
        # Find the most common reason overall
        avg_percentages = filtered_df[reasons].mean()
        top_reason = avg_percentages.idxmax()
        st.metric(
            "Most Common Reason",
            f"{avg_percentages.max():.1f}%",
            delta=top_reason[:30] + "..." if len(top_reason) > 30 else top_reason
        )
    
    with col3:
        # Calculate diversity of reasons (number of reasons with >20% average)
        significant_reasons = (avg_percentages > 20).sum()
        st.metric(
            "Significant Factors",
            significant_reasons,
            delta="(>20% avg response)"
        )
    
    st.markdown("---")
    
    # Top reasons bar chart
    st.subheader(f"Top {top_n} Reasons by Average Impact")
    
    avg_by_reason = filtered_df[reasons].mean().sort_values(ascending=False).head(top_n)
    
    fig_top = px.bar(
        x=avg_by_reason.values,
        y=avg_by_reason.index,
        orientation='h',
        labels={'x': 'Average Response Rate (%)', 'y': 'Reason'},
        color=avg_by_reason.values,
        color_continuous_scale='RdYlGn',
        title=f"Top {top_n} Headcount Change Reasons"
    )
    fig_top.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Heatmap of all reasons across subcategories
    st.subheader(f"Heatmap: All Reasons by {selected_category}")
    
    # Prepare data for heatmap
    heatmap_data = filtered_df.set_index('Subcategory')[reasons]
    
    fig_heatmap = px.imshow(
        heatmap_data.T,
        labels=dict(x=selected_category, y="Reason", color="Response Rate (%)"),
        x=heatmap_data.index,
        y=heatmap_data.columns,
        color_continuous_scale='RdYlGn',
        aspect='auto'
    )
    fig_heatmap.update_layout(
        height=600,
        xaxis_tickangle=-45
    )
    fig_heatmap.update_xaxes(side="bottom")
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab2:
    st.header(f"Detailed Analysis: {selected_reason[:50]}")
    
    # Get data for selected reason
    reason_data = filtered_df[['Subcategory', selected_reason]].sort_values(
        by=selected_reason,
        ascending=False
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart for selected reason
        fig_reason = px.bar(
            reason_data,
            x='Subcategory',
            y=selected_reason,
            title=f"Response Rate by {selected_category}",
            labels={'Subcategory': selected_category, selected_reason: 'Response Rate (%)'},
            color=selected_reason,
            color_continuous_scale='Viridis'
        )
        fig_reason.update_layout(
            height=400,
            xaxis_tickangle=-45,
            showlegend=False
        )
        st.plotly_chart(fig_reason, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Statistics")
        st.metric("Highest", f"{reason_data[selected_reason].max():.1f}%",
                 delta=reason_data.iloc[0]['Subcategory'])
        st.metric("Lowest", f"{reason_data[selected_reason].min():.1f}%",
                 delta=reason_data.iloc[-1]['Subcategory'])
        st.metric("Average", f"{reason_data[selected_reason].mean():.1f}%")
        st.metric("Std Dev", f"{reason_data[selected_reason].std():.1f}%")
    
    # Distribution plot
    st.subheader("Distribution of Response Rates")
    fig_dist = px.histogram(
        reason_data,
        x=selected_reason,
        nbins=20,
        title="Distribution of Response Rates",
        labels={selected_reason: 'Response Rate (%)'},
        color_discrete_sequence=['#3498db']
    )
    fig_dist.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Data table
    st.subheader("Detailed Data")
    st.dataframe(
        reason_data.style.background_gradient(subset=[selected_reason], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.header("Comparative Analysis")
    
    # Compare multiple subcategories
    st.subheader(f"Compare Across {selected_category} Groups")
    
    if len(selected_subcategories) >= 2:
        # Select reasons to compare
        reasons_to_compare = st.multiselect(
            "Select reasons to compare",
            options=reasons,
            default=reasons[:5]
        )
        
        if reasons_to_compare:
            # Create grouped bar chart
            comparison_data = filtered_df[['Subcategory'] + reasons_to_compare].melt(
                id_vars=['Subcategory'],
                var_name='Reason',
                value_name='Response Rate (%)'
            )
            
            fig_compare = px.bar(
                comparison_data,
                x='Subcategory',
                y='Response Rate (%)',
                color='Reason',
                barmode='group',
                title="Side-by-Side Comparison"
            )
            fig_compare.update_layout(
                height=500,
                xaxis_tickangle=-45,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            st.plotly_chart(fig_compare, use_container_width=True)
            
            # Radar chart comparison
            st.subheader("Radar Chart Comparison")
            
            selected_for_radar = st.multiselect(
                "Select groups for radar comparison",
                options=selected_subcategories,
                default=selected_subcategories[:min(4, len(selected_subcategories))]
            )
            
            if len(selected_for_radar) >= 2:
                radar_df = filtered_df[filtered_df['Subcategory'].isin(selected_for_radar)]
                
                fig_radar = go.Figure()
                
                for _, row in radar_df.iterrows():
                    values = [row[r] for r in reasons_to_compare]
                    values.append(values[0])  # Close the radar
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=reasons_to_compare + [reasons_to_compare[0]],
                        fill='toself',
                        name=row['Subcategory']
                    ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    height=500
                )
                st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Please select at least 2 subcategories from the sidebar to enable comparison.")
    
    # Correlation analysis
    st.subheader("Reason Correlation Analysis")
    st.markdown("How do different reasons correlate with each other?")
    
    # Calculate correlation matrix
    corr_matrix = filtered_df[reasons].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1
    )
    fig_corr.update_layout(
        height=700,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with tab4:
    st.header("💡 Key Insights & Trends")
    
    # Calculate insights
    avg_percentages = filtered_df[reasons].mean().sort_values(ascending=False)
    top_3_reasons = avg_percentages.head(3)
    bottom_3_reasons = avg_percentages.tail(3)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Most Impactful Factors")
        for i, (reason, pct) in enumerate(top_3_reasons.items(), 1):
            st.markdown(f"**{i}. {reason}**")
            st.progress(int(pct))
            st.caption(f"Average response rate: {pct:.1f}%")
            st.markdown("")
    
    with col2:
        st.subheader("❄️ Least Impactful Factors")
        for i, (reason, pct) in enumerate(bottom_3_reasons.items(), 1):
            st.markdown(f"**{i}. {reason}**")
            st.progress(int(pct))
            st.caption(f"Average response rate: {pct:.1f}%")
            st.markdown("")
    
    st.markdown("---")
    
    # Find interesting patterns
    st.subheader("🔍 Notable Patterns")
    
    # Highest variance - most divisive reason
    variances = filtered_df[reasons].std().sort_values(ascending=False)
    most_divisive = variances.head(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Most Divisive Factor")
        st.info(f"""
        **{most_divisive.index[0]}**
        
        This factor shows the highest variation across different {selected_category.lower()} groups 
        (std dev: {most_divisive.values[0]:.1f}%), suggesting it impacts companies differently 
        depending on their characteristics.
        """)
    
    with col2:
        # Most consistent reason
        least_divisive = variances.tail(1)
        st.markdown("### Most Consistent Factor")
        st.success(f"""
        **{least_divisive.index[0]}**
        
        This factor shows the least variation across different {selected_category.lower()} groups 
        (std dev: {least_divisive.values[0]:.1f}%), indicating a relatively uniform impact 
        across all company types.
        """)
    
    # Category-specific insights
    st.subheader(f"📈 {selected_category}-Specific Insights")
    
    if selected_category == "Rev Growth":
        st.markdown("""
        - **Growing companies** likely face different headcount pressures than declining ones
        - Look for patterns in expansion-related vs. cost-cutting reasons
        - High-growth companies may cite budget increases and market expansion more frequently
        """)
    elif selected_category == "Company Rev":
        st.markdown("""
        - **Company size by revenue** often correlates with sophistication in workforce planning
        - Smaller companies may be more reactive to market conditions
        - Larger companies may have more structured hiring/reduction processes
        """)
    elif selected_category == "Employee Size":
        st.markdown("""
        - **Headcount size** influences organizational complexity and hiring capabilities
        - Smaller companies may struggle more with talent availability
        - Larger organizations may face more restructuring and efficiency pressures
        """)
    elif selected_category == "Industry":
        st.markdown("""
        - **Industry dynamics** heavily influence workforce decisions
        - Tech and finance may show different patterns than retail or manufacturing
        - Regulatory and market-specific factors play crucial roles
        """)
    
    # Download section
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download filtered data
        csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data (CSV)",
            data=csv_filtered,
            file_name=f"{selected_category.lower().replace(' ', '_')}_data.csv",
            mime="text/csv"
        )
    
    with col2:
        # Download summary statistics
        summary = filtered_df[reasons].describe().T
        csv_summary = summary.to_csv().encode('utf-8')
        st.download_button(
            label="Download Summary Statistics (CSV)",
            data=csv_summary,
            file_name=f"{selected_category.lower().replace(' ', '_')}_summary.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 2rem 0;'>
    <p>Headcount Change Reasons Dashboard | Data from 1,030 companies</p>
    <p style='font-size: 0.9rem;'>Built with Streamlit • Powered by Plotly</p>
</div>
""", unsafe_allow_html=True)
