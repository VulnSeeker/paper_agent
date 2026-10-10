import streamlit as st
from agent import run

st.set_page_config(page_title="PaperPilot", page_icon="📄", layout="wide")

st.markdown("""
<style>
    .main-title {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .paper-card {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 1.2rem; margin: 1rem 0;
    }
    .post-block {
        background: #ffffff; border-left: 4px solid #6366f1;
        padding: 1rem 1.2rem; border-radius: 6px; margin: 0.5rem 0;
        font-family: monospace; font-size: 0.85rem;
        white-space: pre-wrap;
    }
    .platform-header {
        font-weight: 700; color: #6366f1;
        text-transform: uppercase; letter-spacing: 1px;
        font-size: 0.75rem; margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">PaperPilot</h1>', unsafe_allow_html=True)
st.markdown("*Turn any research paper into a LinkedIn post, a Twitter thread, a Medium article, and a Bluesky drop — in one click.*")

col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Topic or search query", placeholder="e.g. Roman Urdu fake news")
with col2:
    n = st.selectbox("Papers", [1, 2, 3, 5], index=1)

if st.button("🚀 Generate", use_container_width=True, type="primary"):
    if not topic.strip():
        st.warning("Enter a topic.")
    else:
        with st.spinner(f"Searching papers, reading them, writing posts..."):
            results = run(topic.strip(), n)

        if not results:
            st.error("No papers found. Try a different topic.")
        else:
            for i, r in enumerate(results, 1):
                paper = r["paper"]
                summary = r["summary"]

                st.markdown(f"## {i}. {paper['title']}")
                st.caption(f"{', '.join(paper.get('authors', [])[:4])} · {paper.get('published', '')} · [{paper['source']}]")
                st.markdown(f"[Read the paper]({paper['url']})")

                with st.expander("Paper summary", expanded=True):
                    st.markdown(f"**In one line:** {summary['one_line']}")
                    st.markdown(f"**Problem:** {summary['problem']}")
                    st.markdown(f"**Method:** {summary['method']}")
                    st.markdown(f"**Result:** {summary['result']}")
                    st.markdown(f"**Why it matters:** {summary['why_it_matters']}")
                    st.markdown(f"**Limitations:** {summary['limitations']}")
                    st.markdown("**Keywords:** " + ", ".join(summary.get("keywords", [])))

                st.markdown('<div class="platform-header">LinkedIn</div>', unsafe_allow_html=True)
                st.code(r["linkedin"], language=None)

                st.markdown('<div class="platform-header">Twitter / X thread</div>', unsafe_allow_html=True)
                for j, tweet in enumerate(r["twitter"], 1):
                    st.code(f"Tweet {j}/{len(r['twitter'])}\n\n{tweet}", language=None)

                st.markdown('<div class="platform-header">Medium</div>', unsafe_allow_html=True)
                st.code(r["medium"], language=None)

                st.markdown('<div class="platform-header">Bluesky</div>', unsafe_allow_html=True)
                for j, bpost in enumerate(r["bluesky"], 1):
                    st.code(f"Post {j}\n\n{bpost}", language=None)

                st.markdown("---")
