# pages/chatbot_assistant.py

import os, sys, streamlit as st, pandas as pd

# ── Ensure project root (where chatbot.py lives) is on sys.path ──
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.chatbot import create_chatbot   # now Python will see root/chatbot.py

# ── the rest of your imports and code ──
st.set_page_config(page_title="Social Media Analytics Chatbot", layout="wide")
st.title("🤖 Social Media Analytics Chatbot")
st.markdown("""
Welcome! Ask questions about your social media performance data
and get AI-powered insights to improve your strategy.
""")

with st.expander("🔍 Example questions you can ask"):
    st.markdown("""
    - What is the best platform for views?
    - Which platform has the lowest engagement rate?
    - Which content type gets the most likes?
    - Compare TikTok vs Instagram
    - What are the top hashtags?
    - What's the best time to post content?
    - Provide strategy tips
    - Show overall average metrics
    - Top 3 platforms by views
    """)
# Load data
csv_path = os.path.join(ROOT, "Viral_Social_Media_Trends.csv")
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    df = pd.read_csv("Viral_Social_Media_Trends.csv")

# Sidebar filters (same as your other pages)
st.sidebar.header("Filters for Chatbot Context")
platforms   = df["Platform"].unique()
regions     = df["Region"].unique()
content_typ = df["Content_Type"].unique()

sel_plat = st.sidebar.multiselect("Platform(s)", platforms, default=platforms)
sel_reg  = st.sidebar.multiselect("Region(s)",   regions,   default=regions)
sel_ct   = st.sidebar.multiselect("Content Type(s)", content_typ, default=content_typ)

df_filtered = df[
    df["Platform"].isin(sel_plat) &
    df["Region"].isin(sel_reg) &
    df["Content_Type"].isin(sel_ct)
]

st.markdown("---")
create_chatbot(df_filtered)
