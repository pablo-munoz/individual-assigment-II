import streamlit as st
import pandas as pd
import altair as alt

# Content Strategy page
st.title("Social Media Trends Dashboard - Content Strategy")
st.markdown("This page explores which content formats and topics drive engagement, offering guidance on ideal content.")

# Load data
import os
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "Viral_Social_Media_Trends.csv"))


# Sidebar: filter by platform or content type
platforms = df["Platform"].unique().tolist()
content_types = df["Content_Type"].unique().tolist()
selected_platforms = st.sidebar.multiselect("Select Platform(s)", platforms, default=platforms)
selected_content = st.sidebar.multiselect("Select Content Type(s)", content_types, default=content_types)

# Filter data
data = df[df["Platform"].isin(selected_platforms) & df["Content_Type"].isin(selected_content)]

st.write(f"Analyzing content for platforms: {', '.join(selected_platforms)} and content types: {', '.join(selected_content)}.")

# Bar chart: average engagement by content type (likes, shares, comments)
mean_content = data.groupby("Content_Type")[["Likes", "Shares", "Comments"]].mean().reset_index()
content_long = mean_content.melt(id_vars="Content_Type", var_name="Metric", value_name="Average")
content_chart = alt.Chart(content_long).mark_bar().encode(
    column=alt.Column("Metric", header=alt.Header(title="Metric")),
    x=alt.X("Content_Type:N", title="Content Type"),
    y=alt.Y("Average:Q", title="Average"),
    color=alt.Color("Content_Type:N", legend=None)
).properties(width=150, height=300)
st.subheader("Average Engagement by Content Type")
st.altair_chart(content_chart, use_container_width=True)

# Distribution of content types (counts)
type_counts = data["Content_Type"].value_counts().reset_index()
type_counts.columns = ["Content_Type", "Count"]
donut = alt.Chart(type_counts).mark_arc(innerRadius=50).encode(
    theta=alt.Theta("Count:Q", title=""),
    color=alt.Color("Content_Type:N", legend=alt.Legend(title="Content Type")),
    tooltip=["Content_Type","Count"]
).properties(width=300, height=300, title="Posts by Content Type (Donut)")
st.subheader("Distribution of Content Types")
st.altair_chart(donut, use_container_width=True)

# Heatmap: average views by region and content type
heatmap_data = data.groupby(["Region","Content_Type"])["Views"].mean().reset_index()
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X("Region:N", title="Region"),
    y=alt.Y("Content_Type:N", title="Content Type"),
    color=alt.Color("Views:Q", title="Avg Views")
).properties(width=400, height=300)
st.subheader("Average Views by Region and Content Type")
st.altair_chart(heatmap, use_container_width=True)

# Top hashtags overall
top_hashtags = df["Hashtag"].value_counts().nlargest(5).reset_index()
top_hashtags.columns = ["Hashtag", "Count"]
hashtag_chart = alt.Chart(top_hashtags).mark_bar().encode(
    x=alt.X("Hashtag:N", title="Hashtag"),
    y=alt.Y("Count:Q", title="Usage Count"),
    color=alt.Color("Hashtag:N", legend=None)
).properties(width=400, height=300)
st.subheader("Top Hashtags Overall")
st.altair_chart(hashtag_chart, use_container_width=True)

# Strategy guidance text
st.markdown(
    "<h5 style='color:#6c6c6c'>Video content — such as reels or shorts — tends to perform best in terms of views and shares.</h5>",
    unsafe_allow_html=True
)




st.info("🕒 Timing Tip: Posting in the afternoon or early evening — especially around 4–7pm — often results in higher engagement, particularly on TikTok.")

# Scatter plot: likes vs comments by content type
avg_content_eng = data.groupby("Content_Type")[["Likes","Comments"]].mean().reset_index()
st.subheader("Likes Distribution by Content Type")
box = alt.Chart(data).mark_boxplot().encode(
    x=alt.X("Content_Type:N", title="Content Type"),
    y=alt.Y("Likes:Q", title="Likes"),
    color=alt.Color("Content_Type:N", legend=None),
    tooltip=["Content_Type","Likes"]
).properties(width=600, height=350)

st.altair_chart(box, use_container_width=True)
st.markdown("*Note:* Use hashtags relevant to trending topics to improve discoverability.")
