import streamlit as st
import pandas as pd
import altair as alt

# Platform Insights page
st.title("Social Media Trends Dashboard - Platform Insights")
st.markdown("This page compares key metrics across social media platforms to support strategic prioritization.")

# Load data
import os
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "Viral_Social_Media_Trends.csv"))


# Sidebar: Select region filter to compare platforms within region(s)
regions = df["Region"].unique().tolist()
selected_regions = st.sidebar.multiselect("Select Region(s)", regions, default=regions)

# Filter data by selected regions
data = df[df["Region"].isin(selected_regions)]

# Sidebar: Choose a metric to compare
metric_options = ["Views", "Likes", "Shares", "Comments", "Engagement Rate (%)"]
selected_metric = st.sidebar.selectbox("Select Metric for Comparison", metric_options)

st.write(f"Analyzing {selected_metric.lower()} for platforms in regions: {', '.join(selected_regions)}.")

# Compute average metric by platform
if selected_metric == "Engagement Rate (%)":
    data["Engagement_Rate"] = (data["Likes"] + data["Shares"] + data["Comments"]) / data["Views"] * 100
    avg_by_platform = data.groupby("Platform")["Engagement_Rate"].mean().reset_index()
    avg_by_platform.columns = ["Platform", "Average"]
else:
    avg_by_platform = data.groupby("Platform")[[selected_metric]].mean().reset_index()
    avg_by_platform.columns = ["Platform", "Average"]

# Sort for better visual ordering
avg_by_platform = avg_by_platform.sort_values("Average", ascending=False)

overall = avg_by_platform["Average"].mean()

bars = alt.Chart(avg_by_platform).mark_bar(size=30).encode(
    y=alt.Y("Platform:N", sort="-x", title="Platform"),
    x=alt.X("Average:Q", title=f"Avg {selected_metric}"),
    color=alt.Color("Platform:N", legend=None),
    tooltip=["Platform","Average"]
)
benchmark = alt.Chart(pd.DataFrame({"y":[-1],"x":[overall]})).mark_rule(color="red").encode(
    x="x:Q"
).properties(title=f"Avg {selected_metric} by Platform (red line = overall avg)")
st.subheader(f"Platform Comparison with Benchmark")
st.altair_chart(bars + benchmark, use_container_width=True)
# Bar chart of average metric by platform
bar_chart = alt.Chart(avg_by_platform).mark_bar().encode(
    x=alt.X("Platform:N", title="Platform"),
    y=alt.Y("Average:Q", title=f"Average {selected_metric}"),
    color=alt.Color("Platform:N", legend=None)
).properties(width=400, height=400)
st.subheader(f"Average {selected_metric} by Platform")
st.altair_chart(bar_chart, use_container_width=True)

# Scatter plot: relationship between average likes and average shares by platform
avg_metrics = data.groupby("Platform")[["Likes", "Shares"]].mean().reset_index()
scatter = alt.Chart(avg_metrics).mark_circle(size=100).encode(
    x=alt.X("Likes:Q", title="Average Likes"),
    y=alt.Y("Shares:Q", title="Average Shares"),
    color=alt.Color("Platform:N", legend=None),
    tooltip=["Platform", "Likes", "Shares"]
).properties(width=400, height=350)
st.subheader("Average Likes vs. Shares by Platform")
st.altair_chart(scatter, use_container_width=True)

# Show total engagement (likes+shares+comments) by platform
data["Total_Engagement"] = data["Likes"] + data["Shares"] + data["Comments"]
total_eng = data.groupby("Platform")["Total_Engagement"].sum().reset_index()
total_eng_chart = alt.Chart(total_eng).mark_bar().encode(
    x=alt.X("Platform:N", title="Platform"),
    y=alt.Y("Total_Engagement:Q", title="Total Engagement"),
    color=alt.Color("Platform:N", legend=None)
).properties(width=400, height=300)
st.subheader("Total Engagement by Platform")
st.altair_chart(total_eng_chart, use_container_width=True)

# Show number of posts per platform (for context)
post_counts = data["Platform"].value_counts().reset_index()
post_counts.columns = ["Platform", "Count"]
count_chart = alt.Chart(post_counts).mark_bar().encode(
    x=alt.X("Platform:N", title="Platform"),
    y=alt.Y("Count:Q", title="Number of Posts"),
    color=alt.Color("Platform:N", legend=None)
).properties(width=400, height=300)
st.subheader("Number of Posts by Platform")
st.altair_chart(count_chart, use_container_width=True)

