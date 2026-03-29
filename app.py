"""
app.py
──────
Streamlit UI for the Healthcare RAG application.
Design: Cinematic dark-green "cave moonlight" theme from the Design Doc.
"""

import streamlit as st
from pathlib import Path
import os
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bits and RAGs on HITECH",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design System (from Design Doc) ───────────────────────────────────────────
STYLE = """
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── CSS Variables ── */
  :root {
    --bg-primary:   #09100B;
    --bg-secondary: #265131;
    --bg-tertiary:  #162D1B;
    --text-primary: #E9F4E2;
    --text-muted:   #919491;
    --text-dim:     #5F655F;
    --accent-green: #51C445;
    --teal-light:   #9AE5C8;
    --teal-mid:     #6AB597;
    --border:       rgba(106,181,151,0.25);
    --glow:         0 0 20px rgba(81,196,69,0.15);
    --glass:        rgba(38,81,49,0.35);
  }

  /* ── Reset & Base ── */
  html, body,
  .stApp,
  .stApp > div,
  [class*="css"],
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewBlockContainer"],
  [data-testid="stVerticalBlock"],
  [data-testid="stMain"],
  [data-testid="stMainBlockContainer"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg-primary); }
  ::-webkit-scrollbar-thumb { background: var(--bg-secondary); border-radius: 3px; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: var(--bg-tertiary) !important;
    border-right: 1px solid var(--border);
  }
  [data-testid="stSidebar"] * { color: var(--text-primary) !important; }
  [data-testid="stSidebar"] .stTextInput input {
    background: rgba(9,16,11,0.8) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
  }
  [data-testid="stSidebar"] .stTextInput input:focus {
    border-color: var(--accent-green) !important;
    box-shadow: var(--glow) !important;
  }

  /* ── Main chat area ── */
  .main-wrapper {
    max-width: 860px;
    margin: 0 auto;
    padding: 2rem 1.5rem 120px;
    min-height: 100dvh;
  }

  /* ── App title ── */
  .app-header {
    text-align: center;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }
  .app-header h1 {
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 0 0 0.4rem;
  }
  .app-header h1 span { color: var(--accent-green); }
  .app-header p {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin: 0;
  }

  /* ── Chat bubbles ── */
  .chat-container { display: flex; flex-direction: column; gap: 1.4rem; }

  .msg-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    animation: fadeSlideIn 0.3s ease;
  }
  .msg-row.user { flex-direction: row-reverse; }

  @keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .avatar {
    width: 36px; height: 36px; flex-shrink: 0;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
  }
  .avatar.ai  { background: linear-gradient(135deg, var(--bg-secondary), var(--teal-mid)); border: 1px solid var(--teal-mid); }
  .avatar.usr { background: linear-gradient(135deg, #1a3320, var(--bg-secondary)); border: 1px solid var(--border); }

  .bubble {
    max-width: 78%;
    padding: 0.9rem 1.1rem;
    border-radius: 14px;
    font-size: 0.93rem;
    line-height: 1.65;
    position: relative;
  }
  .bubble.user {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-top-right-radius: 4px;
    color: var(--text-primary);
  }
  .bubble.ai {
    background: rgba(38,81,49,0.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(154,229,200,0.18);
    border-top-left-radius: 4px;
    color: var(--text-primary);
  }
  .bubble.ai strong { color: var(--teal-light); }

  /* ── Citation cards ── */
  .citations-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0.9rem 0 0.5rem 0.5rem;
  }
  .citations-grid {
    display: flex; flex-wrap: wrap; gap: 0.7rem;
    margin-left: 0.5rem;
  }
  .citation-card {
    background: var(--glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border);
    border-left: 3px solid var(--teal-mid);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    max-width: 320px;
    transition: border-color 0.2s, transform 0.2s;
    cursor: default;
  }
  .citation-card:hover {
    border-left-color: var(--accent-green);
    transform: translateY(-2px);
    box-shadow: var(--glow);
  }
  .citation-meta {
    font-size: 0.68rem;
    color: var(--teal-light);
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 0.35rem;
    display: flex; justify-content: space-between;
  }
  .citation-text {
    font-size: 0.77rem;
    color: var(--text-muted);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  /* ── Input bar (anchored bottom) ── */
  .input-bar-wrapper {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(to top, var(--bg-primary) 80%, transparent);
    padding: 1rem 1.5rem 1.4rem;
    z-index: 100;
  }
  .input-bar-inner {
    max-width: 860px; margin: 0 auto;
    display: flex; gap: 0.6rem; align-items: flex-end;
  }
  .stTextArea textarea {
    background: rgba(22,45,27,0.9) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.93rem !important;
    resize: none !important;
    min-height: 52px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
  }
  .stTextArea textarea:focus {
    border-color: var(--accent-green) !important;
    box-shadow: var(--glow) !important;
    outline: none !important;
  }
  .stTextArea textarea::placeholder { color: var(--text-dim) !important; }

  /* ── Submit button ── */
  .stButton > button {
    background: var(--accent-green) !important;
    color: #09100B !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.65rem 1.4rem !important;
    height: 52px !important;
    cursor: pointer !important;
    transition: filter 0.2s, transform 0.15s !important;
    white-space: nowrap !important;
  }
  .stButton > button:hover {
    filter: brightness(1.15) !important;
    transform: translateY(-1px) !important;
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* ── Processing indicator ── */
  .thinking-row {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.5rem 0.2rem;
  }
  .thinking-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent-green);
    animation: pulse 1s infinite ease-in-out;
  }
  .thinking-dot:nth-child(2) { animation-delay: 0.2s; }
  .thinking-dot:nth-child(3) { animation-delay: 0.4s; }
  @keyframes pulse {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40%           { transform: scale(1);   opacity: 1; }
  }
  .thinking-text { font-size: 0.82rem; color: var(--text-muted); }

  /* ── Welcome card ── */
  .welcome-card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 2rem auto;
    max-width: 600px;
  }
  .welcome-card .icon { font-size: 2.8rem; margin-bottom: 0.8rem; }
  .welcome-card h2 { font-size: 1.2rem; font-weight: 600; margin: 0 0 0.6rem; }
  .welcome-card p { font-size: 0.87rem; color: var(--text-muted); margin: 0 0 1.2rem; }
  .sample-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
  .chip {
    background: rgba(81,196,69,0.1);
    border: 1px solid rgba(81,196,69,0.35);
    border-radius: 20px;
    padding: 0.35rem 0.9rem;
    font-size: 0.78rem;
    color: var(--teal-light);
    cursor: pointer;
    transition: background 0.2s;
  }
  .chip:hover { background: rgba(81,196,69,0.2); }

  /* ── Status badges ── */
  .status-badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    font-size: 0.72rem; font-family: 'JetBrains Mono', monospace;
    padding: 0.2rem 0.6rem; border-radius: 20px;
  }
  .status-badge.ok  { background: rgba(81,196,69,0.12); color: var(--accent-green); border: 1px solid rgba(81,196,69,0.3); }
  .status-badge.err { background: rgba(220,50,50,0.12);  color: #f87171;             border: 1px solid rgba(220,50,50,0.3); }

  /* ── Sidebar sections ── */
  .sidebar-section {
    margin-bottom: 1.4rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
  }
  .sidebar-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted) !important;
    margin-bottom: 0.5rem;
  }

  /* ── Mobile ── */
  @media (max-width: 640px) {
    .main-wrapper { padding: 1rem 0.8rem 130px; }
    .bubble { max-width: 92%; font-size: 0.88rem; }
    .app-header h1 { font-size: 1.3rem; }
    .citation-card { max-width: 100%; }
  }
</style>
"""

# ── Inject CSS ─────────────────────────────────────────────────────────────────
st.markdown(STYLE, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {role, content, sources}
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "chain_ready" not in st.session_state:
    st.session_state.chain_ready = False
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GROQ_API_KEY", "")
if "index_built" not in st.session_state:
    st.session_state.index_built = (Path("faiss_index")).exists()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ RAG Assistant")
    st.markdown("<div class='sidebar-label'>Document</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.82rem;color:#9AE5C8;padding:0.4rem 0;'>"
        "📄 HITECH Act (Public Law 111-5)<br>"
        "<span style='color:#5F655F;font-size:0.72rem;'>Subtitles D — Privacy & Security</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("<div class='sidebar-label'>Groq API Key</div>", unsafe_allow_html=True)
    if st.session_state.api_key:
        st.markdown(
            "<span class='status-badge ok'>● API Key Set</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='status-badge err'>○ No API Key — set GROQ_API_KEY in .env</span>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("<div class='sidebar-label'>Model</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.8rem;color:#9AE5C8;'>🤖 llama-3.3-70b-versatile (Groq)</div>"
        "<div style='font-size:0.72rem;color:#5F655F;margin-top:0.2rem;'>Embeddings: all-MiniLM-L6-v2</div>"
        "<div style='font-size:0.72rem;color:#5F655F;'>Vector Store: FAISS</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    if st.session_state.index_built:
        st.markdown(
            "<span class='status-badge ok'>● Vector Index Ready</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='status-badge err'>○ Index not built yet</span>",
            unsafe_allow_html=True,
        )
        st.caption("Index builds automatically on first query.")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Load/cache rag chain ───────────────────────────────────────────────────────
def get_chain():
    if not st.session_state.chain_ready and st.session_state.api_key:
        with st.spinner("🔧 Building RAG pipeline…"):
            try:
                from rag_pipeline import build_rag_chain
                st.session_state.rag_chain = build_rag_chain(
                    api_key=st.session_state.api_key
                )
                st.session_state.chain_ready = True
                st.session_state.index_built = True
            except Exception as e:
                st.error(f"Failed to build pipeline: {e}")
    return st.session_state.rag_chain


# ── Main layout ────────────────────────────────────────────────────────────────
main_col, _ = st.columns([1, 0.001])

with main_col:
    st.markdown("<div class='main-wrapper'>", unsafe_allow_html=True)

    # Header
    st.markdown(
        """
        <div class='app-header'>
          <h1>Bits and <span>RAGs</span> on HITECH</h1>
          <p>Ask questions about breach notification, PHR security, and healthcare privacy law.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Chat history
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    if not st.session_state.messages:
        # Welcome card
        st.markdown(
            """
            <div class='welcome-card'>
              <div class='icon'>⚖️</div>
              <h2>Ask the HITECH Act</h2>
              <p>This assistant is grounded in <strong>Public Law 111-5, Division A, Title XIII</strong>.<br>
              All answers are retrieved directly from the document.</p>
              <div class='sample-chips'>
                <span class='chip'>What is a PHR breach?</span>
                <span class='chip'>FTC breach notification role</span>
                <span class='chip'>Vendor obligations after breach</span>
                <span class='chip'>PHR identifiable health info</span>
                <span class='chip'>Third-party service provider duties</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            sources = msg.get("sources", [])

            if role == "user":
                safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                st.markdown(
                    f"<div class='msg-row user'>"
                    f"<div class='avatar usr'>🧑</div>"
                    f"<div class='bubble user'>{safe_content}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(
                    f"<div class='msg-row ai'>"
                    f"<div class='avatar ai'>⚖️</div>"
                    f"<div class='bubble ai'>{safe_content}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                # Citation cards
                if sources:
                    st.markdown(
                        "<div class='citations-label'>📎 Retrieved Sections</div>",
                        unsafe_allow_html=True,
                    )
                    cards_html = "<div class='citations-grid'>"
                    for s in sources:
                        sim_pct = int(s["similarity"] * 100)
                        bar_w = max(sim_pct, 10)
                        text_safe = s['text'][:280].replace('<', '&lt;').replace('>', '&gt;')
                        cards_html += (
                            f"<div class='citation-card'>"
                            f"<div class='citation-meta'><span>Page {s['page']}</span>"
                            f"<span style='color:var(--accent-green);'>{sim_pct}% match</span></div>"
                            f"<div style='height:2px;background:var(--bg-tertiary);border-radius:1px;margin-bottom:0.5rem;'>"
                            f"<div style='height:100%;width:{bar_w}%;background:linear-gradient(to right,var(--teal-mid),var(--accent-green));border-radius:1px;'></div></div>"
                            f"<div class='citation-text'>{text_safe}…</div>"
                            f"</div>"
                        )
                    cards_html += "</div>"
                    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # chat-container
    st.markdown("</div>", unsafe_allow_html=True)  # main-wrapper


# ── Fixed input bar ────────────────────────────────────────────────────────────
st.markdown("<div class='input-bar-wrapper'><div class='input-bar-inner'>", unsafe_allow_html=True)

input_col, btn_col = st.columns([5, 1])

with input_col:
    user_input = st.text_area(
        "Query",
        key="query_input",
        placeholder="Ask about HITECH Act provisions, breach notifications, PHR security…",
        label_visibility="collapsed",
        height=68,
    )

with btn_col:
    submit = st.button("Send ➤", use_container_width=True)

st.markdown("</div></div>", unsafe_allow_html=True)


# ── Handle submission ──────────────────────────────────────────────────────────
if submit and user_input.strip():
    query = user_input.strip()

    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar first.")
        st.stop()

    # Append user message
    st.session_state.messages.append({"role": "user", "content": query, "sources": []})

    # Build chain if needed
    chain = get_chain()
    if chain is None:
        st.error("Could not initialise RAG pipeline. Check your API key.")
        st.stop()

    # Run retrieval + generation
    with st.spinner(""):
        st.markdown(
            """
            <div class='thinking-row'>
              <div class='thinking-dot'></div>
              <div class='thinking-dot'></div>
              <div class='thinking-dot'></div>
              <span class='thinking-text'>Retrieving relevant sections…</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            from rag_pipeline import get_source_chunks
            result = chain.invoke({"query": query})
            answer = result.get("result", "No answer generated.")
            sources = get_source_chunks(query, api_key=st.session_state.api_key)
        except Exception as e:
            answer = f"⚠️ Error: {e}"
            sources = []

    # Append AI message
    st.session_state.messages.append(
        {"role": "ai", "content": answer, "sources": sources}
    )
    st.rerun()
