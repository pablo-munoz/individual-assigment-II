import streamlit as st
import pandas as pd
import altair as alt
from streamlit_chat import message

# Trend Overview page
st.title("Social Media Trends Dashboard - Trend Overview")
st.markdown("This page provides an overview of engagement and virality trends across social media platforms over time.")

# Load data
import os
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "Viral_Social_Media_Trends.csv"))


# Sidebar filters
platforms = df["Platform"].unique().tolist()
regions = df["Region"].unique().tolist()
selected_platforms = st.sidebar.multiselect("Select Platform(s)", platforms, default=platforms)
selected_regions = st.sidebar.multiselect("Select Region(s)", regions, default=regions)

# Filter data based on selections
data = df[df["Platform"].isin(selected_platforms) & df["Region"].isin(selected_regions)]

# Display key metrics as large text
total_posts = len(data)
avg_views = int(data["Views"].mean()) if total_posts > 0 else 0
avg_likes = int(data["Likes"].mean()) if total_posts > 0 else 0
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Posts", total_posts)
col2.metric("Average Views", f"{avg_views:,}")
col3.metric("Average Likes", f"{avg_likes:,}")

# Description text
st.write("These metrics update based on your filters. They give quick insight into the volume of posts and average engagement for the selected data.")

# Line chart: trending views over grouped posts
data_sorted = data.copy()
data_sorted["Post_Num"] = data_sorted["Post_ID"].str.extract("([0-9]+)").astype(int)
data_sorted = data_sorted.sort_values("Post_Num")
data_sorted["Bin"] = (data_sorted["Post_Num"] - 1) // 50
avg_by_bin = data_sorted.groupby(["Bin", "Platform"])["Views"].mean().reset_index()
line_chart = alt.Chart(avg_by_bin).mark_line(point=True).encode(
    x=alt.X("Bin:Q", title="Post Group (earlier to later)"),
    y=alt.Y("Views:Q", title="Average Views"),
    color=alt.Color("Platform:N", title="Platform")
).properties(width=600, height=300)
st.subheader("Views Trend by Platform")
st.altair_chart(line_chart, use_container_width=True)

# Bar chart: average engagement metrics by platform
mean_metrics = data.groupby("Platform")[["Likes", "Shares", "Comments"]].mean().reset_index()
metrics_long = mean_metrics.melt(id_vars="Platform", var_name="Metric", value_name="Average")
bar_chart = alt.Chart(metrics_long).mark_bar().encode(
    column=alt.Column("Metric", header=alt.Header(title="Metric")),
    x=alt.X("Platform:N", title="Platform"),
    y=alt.Y("Average:Q", title="Average"),
    color=alt.Color("Platform:N", legend=None)
).properties(width=150, height=300)
st.subheader("Average Engagement by Platform")
st.altair_chart(bar_chart, use_container_width=True)

# Bar chart: distribution of posts by engagement level
if total_posts > 0:
    eng_counts = data["Engagement_Level"].value_counts().reset_index()
    eng_counts.columns = ["Level", "Count"]
    eng_chart = alt.Chart(eng_counts).mark_bar().encode(
        x=alt.X("Level:N", title="Engagement Level"),
        y=alt.Y("Count:Q", title="Number of Posts"),
        color=alt.Color("Level:N", legend=None)
    ).properties(width=400, height=300)
    st.subheader("Post Engagement Level Distribution")
    st.altair_chart(eng_chart, use_container_width=True)

# Show raw data table on demand
if st.checkbox("Show raw data table"):
    st.write("Filtered dataset:")
    st.dataframe(data)

# Chatbot interactive section
st.subheader("Ask an Analytics Chatbot")
if "history" not in st.session_state:
    st.session_state.history = []
user_input = st.text_input("Ask a question about the data or marketing strategy:")
if user_input:
    q = user_input.lower()
    response = ""
    if "best platform" in q or "top platform" in q:
        best = mean_metrics.sort_values("Likes", ascending=False).iloc[0]["Platform"]
        response = f"In our dataset, {best} posts have the highest average likes."
    elif "content type" in q or "type of content" in q:
        best_type = data.groupby("Content_Type")["Views"].mean().idxmax()
        response = f"Content type '{best_type}' has the highest average views in the selected data."
    elif "views" in q:
        response = f"The average views across all posts is about {int(df['Views'].mean()):,}."
    else:
        response = "TikTok and YouTube posts tend to perform very well. Use filters to explore specific trends."
    st.session_state.history.append((user_input, response))
for user, bot in st.session_state.history:
    st.write(f"**You:** {user_input}")
    st.write(f"**Bot:** {response}")
