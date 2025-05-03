import streamlit as st
import pandas as pd
import re


def create_chatbot(df: pd.DataFrame):

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Reset button
    _, col_reset = st.columns([4, 1])
    with col_reset:
        if st.button("Reset Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    # Show history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Get user input
    user_input = st.chat_input("Ask about your social media trends…")
    if not user_input:
        return

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Generate and show response
    response = _generate_response(user_input, df)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)


def _generate_response(query: str, df: pd.DataFrame) -> str:
    q = query.lower()

    # Precompute key aggregates
    safe_views = df["Views"].replace(0, pd.NA)
    df = df.assign(Engagement_Rate=((df["Likes"] + df["Shares"] + df["Comments"]) / safe_views * 100).fillna(0))

    # Only numeric columns
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    avg_platform = df.groupby("Platform")[num_cols].mean(numeric_only=True)
    avg_content  = df.groupby("Content_Type")[num_cols].mean(numeric_only=True)
    avg_region   = df.groupby("Region")[num_cols].mean(numeric_only=True)
    top_hashtags = df["Hashtag"].value_counts()

    # Identify metrics requested
    metrics_keys = {
        "views": "Views",
        "view": "Views",
        "likes": "Likes",
        "like": "Likes",
        "shares": "Shares",
        "share": "Shares",
        "comments": "Comments",
        "comment": "Comments",
        "engagement rate": "Engagement_Rate",
        "engagement": "Engagement_Rate"
    }
    requested_metrics = []
    for key, col in metrics_keys.items():
        if key in q:
            requested_metrics.append(col)
    requested_metrics = list(dict.fromkeys(requested_metrics))

    # Identify entities
    entities = []
    if re.search(r"\bplatforms?\b", q): entities.append("platform")
    if re.search(r"\bcontent|format|type\b", q): entities.append("content")
    if re.search(r"\bregions?\b|country|location", q): entities.append("region")
    if re.search(r"\bhashtag", q): entities.append("hashtag")
    if "compare" in q or " vs " in q: entities.append("compare")
    if re.search(r"\btime\b|when\b", q): entities.append("time")
    if re.search(r"\bstrategy|tip|recommend|advice|suggest\b", q): entities.append("strategy")
    if re.search(r"\baverage|stat|overview|metrics?\b", q): entities.append("stats")

    # Greeting or help
    if re.search(r"\b(hello|hi|hey)\b", q):
        return "Hello! I can provide top platforms, content types, regions, hashtags, timing tips, or strategy advice. What would you like?"
    if "help" in q:
        return ("Ask me things like:\n"
                "- Best platform for views/likes/engagement?\n"
                "- Top content type by shares?\n"
                "- Compare TikTok vs Instagram.\n"
                "- Top hashtags.\n"
                "- Best time to post.\n"
                "- Provide strategy tips.")

    # Hashtag query
    if "hashtag" in entities:
        top5 = top_hashtags.head(5)
        return "Top hashtags: " + ", ".join([f"#{tag}" for tag in top5.index.tolist()]) + "."

    # Compare two platforms
    if "compare" in entities:
        platforms = df["Platform"].unique()
        mentioned = [p for p in platforms if p.lower() in q]
        if len(mentioned) >= 2:
            p1, p2 = mentioned[:2]
            lines = []
            for m in requested_metrics or ["Views"]:
                val1, val2 = avg_platform.at[p1, m], avg_platform.at[p2, m]
                champ = p1 if val1 > val2 else p2
                lines.append(f"{m}: {p1} {val1:.0f} vs {p2} {val2:.0f} → Top: {champ}")
            return "Comparison results:\n" + "\n".join(lines)
        return "Please specify two platforms to compare, e.g. 'Compare TikTok vs Instagram'."

    # Best/worst entities
    if requested_metrics and entities:
        metric = requested_metrics[0]
        best = True if re.search(r"\b(best|top|highest|most)\b", q) else False
        results = []
        for ent in [e for e in entities if e in ("platform","content","region")]:
            df_map = {"platform": avg_platform,
                      "content":  avg_content,
                      "region":   avg_region}[ent]
            if best:
                idx = df_map[metric].idxmax()
                val = df_map[metric].max()
                results.append(f"Top {ent}: {idx} ({val:.2f}) by {metric.lower()}")
            elif re.search(r"\b(worst|least|lowest|underperform)\b", q):
                idx = df_map[metric].idxmin()
                val = df_map[metric].min()
                results.append(f"Lowest {ent}: {idx} ({val:.2f}) by {metric.lower()}")
        if results:
            return "\n".join(results)

    # Default comparisons: top 3 if just entity
    if not requested_metrics and entities:
        ent = entities[0]
        if ent in ("platform","content","region"):
            df_map = {"platform": avg_platform,
                      "content":  avg_content,
                      "region":   avg_region}[ent]
            top3 = df_map["Views"].nlargest(3)
            lines = [f"{i+1}. {idx} ({val:.0f} avg views)" for i,(idx,val) in enumerate(top3.items())]
            return f"Top 3 {ent}s by views:\n" + "\n".join(lines)

    # Timing
    if "time" in entities:
        return "🕒 Best posting window: 4–7 PM local time, especially for video content on TikTok & Instagram."

    # Strategy advice
    if "strategy" in entities:
        bp = avg_platform["Views"].idxmax()
        bc = avg_content["Views"].idxmax()
        tags = top_hashtags.head(3).index.tolist()
        return (
            f"Strategy Tips:\n"
            f"1. Focus on {bc} content.\n"
            f"2. Prioritize {bp} platform.\n"
            f"3. Use hashtags: {', '.join(tags)}.\n"
            "4. Post around 4–7 PM.\n"
            "5. Encourage comments with CTAs."
        )

    # Overall stats
    if "stats" in entities:
        avgs = df[num_cols].mean()
        lines = [f"{c}: {avgs[c]:,.0f}" for c in ["Views","Likes","Shares","Comments"]]
        return "Overall averages:\n" + "\n".join(lines)

    # Fallback
    return ("Sorry, I didn't get that. You can ask about top platforms/content/regions, "
            "compare platforms, top hashtags, best times to post, or strategy tips.")
