"""
Social Sentinel - Streamlit Dashboard
Interactive dashboard for monitoring hooks, niches, and generating content.
"""

import json
import os

import streamlit as st

from social_sentinel.config import config
from social_sentinel.core.analyzer import AnalysisEngine
from social_sentinel.core.scraper import SocialScraper
from social_sentinel.main import SocialSentinel
from social_sentinel.storage.hook_bank import HookBank

st.set_page_config(
    page_title="Social Sentinel Dashboard",
    page_icon="🛰️",
    layout="wide",
)

st.title("🛰️ Social Sentinel")
st.caption("Automated Content Intelligence — Hook Detection, Niche Analysis & Content Generation")

# Sidebar
with st.sidebar:
    st.header("Controls")
    run_pipeline = st.button("🔄 Run Pipeline", type="primary")
    platform = st.selectbox("Generate for", ["linkedin", "twitter"])

    st.divider()
    stats = HookBank().get_stats()
    st.metric("Total Hooks", stats["total_hooks"])
    st.metric("Unique Niches", stats["unique_niches"])
    st.metric("Avg Score", f"{stats['avg_niche_score']}/10")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🏆 Hook Bank", "🔥 Trending Niches", "📝 Content Generator"])

# Tab 1: Dashboard
with tab1:
    st.header("Pipeline Overview")

    if run_pipeline:
        with st.spinner("Running Social Sentinel pipeline..."):
            sentinel = SocialSentinel()
            report = sentinel.run_pipeline(platform=platform)
            st.session_state["last_report"] = report
            st.success(f"Pipeline complete! {report['hooks_added']} new hooks added.")

    report = st.session_state.get("last_report")
    if report and report.get("status") == "success":
        col1, col2, col3 = st.columns(3)
        col1.metric("Posts Scraped", report["posts_scraped"])
        col2.metric("Hooks Added", report["hooks_added"])
        col3.metric("Total in Bank", report["stats"]["total_hooks"])

        if report.get("generated_post"):
            st.subheader("📝 Generated Post")
            st.markdown(f"```\n{report['generated_post']}\n```")
            st.download_button(
                label="📥 Download Post",
                data=report["generated_post"],
                file_name="generated_post.txt",
                mime="text/plain",
            )

# Tab 2: Hook Bank
with tab2:
    st.header("Hook Bank")

    hook_bank = HookBank()
    niche_filter = st.selectbox(
        "Filter by niche",
        ["All"] + [n["niche"] for n in hook_bank.get_trending_niches(limit=20)]
    )

    niche = None if niche_filter == "All" else niche_filter
    hooks = hook_bank.get_top_hooks(limit=50, niche=niche)

    if hooks:
        for hook in hooks:
            with st.expander(
                f"{'🔥' if hook['niche_score'] >= 8 else '⭐'} {hook['hook_text'][:100]}... "
                f"(Score: {hook['niche_score']}/10 | {hook['hook_type']})"
            ):
                st.write(f"**Full Hook:** {hook['hook_text']}")
                st.write(f"**Pattern:** {hook['hook_type']}")
                st.write(f"**Niche:** {hook['niche']}")
                st.write(f"**Platform:** {hook['platform']}")
                st.write(f"**Author:** {hook['author']}")
                st.write(f"**Emotional Trigger:** {hook.get('emotional_trigger', 'N/A')}")
                st.write(f"**Why Viral:** {hook.get('why_viral', 'N/A')}")
    else:
        st.info("No hooks in bank yet. Run the pipeline to start collecting!")

# Tab 3: Trending Niches
with tab3:
    st.header("Trending Niches")

    hook_bank = HookBank()
    niches = hook_bank.get_trending_niches(limit=10)

    if niches:
        for niche in niches:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Niche", niche["niche"])
            col2.metric("Avg Score", f"{niche['avg_score']:.1f}/10")
            col3.metric("Max Score", f"{niche['max_score']}/10")
            col4.metric("Hooks", niche["hook_count"])

        # Visual bar chart
        import pandas as pd
        df = pd.DataFrame(niches)
        st.bar_chart(df.set_index("niche")[["avg_score", "max_score"]])
    else:
        st.info("No niche data yet. Run the pipeline first!")

# Tab 4: Content Generator
with tab4:
    st.header("Content Generator")
    st.caption("Generate optimized posts based on your Hook Bank data")

    gen_platform = st.selectbox("Platform", ["linkedin", "twitter"], key="gen_platform")
    gen_niche = st.text_input("Focus niche (optional)", placeholder="e.g., AI Agents, Vibe Coding")

    if st.button("✨ Generate Post", type="primary"):
        with st.spinner("Analyzing top hooks and generating content..."):
            hook_bank = HookBank()
            hooks_data = hook_bank.get_top_hooks(limit=10)

            if not hooks_data:
                st.warning("No hooks in bank. Run the pipeline first!")
            else:
                analyzer = AnalysisEngine()
                # Convert to format expected by generate_post
                analyzed = [
                    {"post": type("obj", (object,), {"platform": h["platform"], "author": h["author"]})(),
                     "analysis": {"hook": h["hook_text"], "hook_type": h["hook_type"],
                                  "niche": h["niche"], "niche_score": h["niche_score"]}}
                    for h in hooks_data
                ]

                post = analyzer.generate_post(analyzed, platform=gen_platform)
                st.subheader("Generated Post")
                st.markdown(f"```\n{post}\n```")

                col1, col2 = st.columns(2)
                col1.download_button(
                    "📥 Download",
                    data=post,
                    file_name=f"post_{gen_platform}.txt",
                    mime="text/plain",
                )
                if col2.button("📋 Copy to Clipboard"):
                    st.code(post, language="text")

# Footer
st.divider()
st.caption("Social Sentinel v1.0 | Built for content intelligence & growth hacking")
