import logging
import os
import streamlit as st
from config.config import validate_config, MODE_CONCISE, MODE_DETAILED
from models.llm import stream_llm_response
from utils.rag_utils import build_index_from_file, retrieve_context, FAISSIndex, FAISS_AVAILABLE
from utils.web_search import web_search

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="AI Research Assistant", page_icon="🔬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); color: #e8e8f0; }
[data-testid="stSidebar"] { background: rgba(255,255,255,0.04); border-right: 1px solid rgba(255,255,255,0.08); }
.main-header { text-align: center; padding: 2rem 0 1rem; }
.main-header h1 { font-size: 2.4rem; font-weight: 700; background: linear-gradient(90deg,#a78bfa,#60a5fa,#34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.2rem; }
.main-header p { color: #8888aa; font-size: 0.95rem; margin: 0; }
.source-badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; margin-bottom: 6px; }
.badge-rag  { background: rgba(52,211,153,0.15);  color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-web  { background: rgba(96,165,250,0.15);  color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }
.badge-llm  { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }
[data-testid="stChatMessage"] { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; margin-bottom: 0.5rem; padding: 0.8rem !important; }
[data-testid="stChatInput"] textarea { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(167,139,250,0.35) !important; border-radius: 10px !important; color: #e8e8f0 !important; }
[data-testid="stFileUploader"] { background: rgba(255,255,255,0.04); border: 1px dashed rgba(167,139,250,0.35); border-radius: 10px; padding: 0.5rem; }
.status-box { padding: 0.6rem 1rem; border-radius: 8px; font-size: 0.85rem; margin: 0.4rem 0; }
.status-ok   { background: rgba(52,211,153,0.1);  border-left: 3px solid #34d399; color: #a7f3d0; }
.status-warn { background: rgba(251,191,36,0.1);  border-left: 3px solid #fbbf24; color: #fde68a; }
.status-err  { background: rgba(248,113,113,0.1); border-left: 3px solid #f87171; color: #fecaca; }
.stButton > button { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.4); border-radius: 8px; font-weight: 500; transition: all 0.2s; }
.stButton > button:hover { background: rgba(167,139,250,0.28); }
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "messages": [], "faiss_index": None, "uploaded_filename": "",
        "rag_available": False, "total_queries": 0, "rag_hits": 0, "web_hits": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

with st.sidebar:
    st.markdown("## 🔬 Research Assistant")
    st.markdown("---")

    # ── API Key Debug Section ──────────────────────────────────────────────
    from config.config import GROQ_API_KEY
    if GROQ_API_KEY:
        st.markdown(f'<div class="status-box status-ok">✅ Key loaded: <code>...{GROQ_API_KEY[-6:]}</code></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-err">❌ No API key found in .env</div>', unsafe_allow_html=True)

    # Manual key input as fallback
    st.markdown("**Or paste your key directly here:**")
    manual_key = st.text_input("Groq API Key", type="password",
                                placeholder="gsk_...",
                                help="Paste your key from https://console.groq.com")
    if manual_key:
        os.environ["GROQ_API_KEY"] = manual_key
        # Re-import to pick up the new value
        import importlib
        import config.config as cfg
        importlib.reload(cfg)
        st.success("✅ Key applied! Now ask a question.")

    st.markdown("---")
    st.markdown("### ⚙️ Response Mode")
    mode = st.radio("Choose depth:", options=[MODE_CONCISE, MODE_DETAILED], index=0)
    cls = "status-ok" if mode == MODE_CONCISE else "status-warn"
    st.markdown(f'<div class="status-box {cls}">Mode: <b>{mode}</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📄 Upload Document (RAG)")
    uploaded_file = st.file_uploader("PDF or TXT file", type=["pdf", "txt", "md"])

    if uploaded_file and uploaded_file.name != st.session_state.uploaded_filename:
        with st.spinner(f"Indexing **{uploaded_file.name}**…"):
            try:
                idx = build_index_from_file(uploaded_file.read(), uploaded_file.name)
                st.session_state.faiss_index = idx
                st.session_state.uploaded_filename = uploaded_file.name
                st.session_state.rag_available = True
                st.success(f"✅ Indexed **{len(idx.chunks)} chunks**")
            except Exception as exc:
                st.error(f"❌ Indexing failed: {exc}")
                st.session_state.rag_available = False

    if st.session_state.rag_available:
        st.markdown(f'<div class="status-box status-ok">📚 RAG Active: <b>{st.session_state.uploaded_filename}</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-warn">📭 No doc — will use web search</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    c1, c2, c3 = st.columns(3)
    c1.metric("Queries", st.session_state.total_queries)
    c2.metric("RAG hits", st.session_state.rag_hits)
    c3.metric("Web hits", st.session_state.web_hits)

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_queries = st.session_state.rag_hits = st.session_state.web_hits = 0
        st.rerun()

    st.markdown('<p style="color:#555577;font-size:0.75rem;text-align:center;margin-top:0.5rem;"><br> <b style="color:#34d399">$0</b></p>', unsafe_allow_html=True)


st.markdown("""
<div class="main-header">
  <h1>🔬 AI Research Assistant</h1>
  <p>Documents (RAG) · Live web search · Groq LLaMA · 100% Free</p>
</div>
""", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "source" in msg:
            src = msg["source"]
            if src == "rag":
                st.markdown('<span class="source-badge badge-rag">📚 RAG · Document</span>', unsafe_allow_html=True)
            elif src == "web":
                st.markdown(f'<span class="source-badge badge-web">🌐 Web · {msg.get("search_engine","")}</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="source-badge badge-llm">🤖 Groq LLaMA</span>', unsafe_allow_html=True)
        st.markdown(msg["content"])


if prompt := st.chat_input("Ask a research question…"):

    # Always read the freshest key from env at query time
    live_key = os.environ.get("GROQ_API_KEY", "")
    if not live_key:
        st.error("⚠️ No API key found. Paste your Groq key in the sidebar field above.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.total_queries += 1
    context = ""
    source_key = "llm"
    search_engine_label = ""
    pipeline_info = []

    if st.session_state.rag_available and st.session_state.faiss_index:
        try:
            with st.status("🔍 Searching document…", expanded=False):
                context, rag_ok = retrieve_context(prompt, st.session_state.faiss_index)
            if rag_ok:
                source_key = "rag"
                st.session_state.rag_hits += 1
                pipeline_info.append("✅ RAG found relevant context in document.")
            else:
                pipeline_info.append("⚠️ RAG: nothing relevant found — trying web search.")
        except Exception as exc:
            pipeline_info.append(f"⚠️ RAG error: {exc}")

    if not context:
        try:
            with st.status("🌐 Searching the web…", expanded=False):
                context, search_engine_label = web_search(prompt)
            source_key = "web"
            st.session_state.web_hits += 1
            pipeline_info.append(f"✅ Web search ({search_engine_label}) returned results.")
        except Exception as exc:
            pipeline_info.append(f"⚠️ Web search failed: {exc}. Using Groq's own knowledge.")

    with st.chat_message("assistant"):
        if source_key == "rag":
            st.markdown('<span class="source-badge badge-rag">📚 RAG · Document</span>', unsafe_allow_html=True)
        elif source_key == "web":
            st.markdown(f'<span class="source-badge badge-web">🌐 Web · {search_engine_label}</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="source-badge badge-llm">🤖 Groq LLaMA</span>', unsafe_allow_html=True)

        placeholder = st.empty()
        full_response = ""
        try:
            for token in stream_llm_response(query=prompt, context=context, mode=mode):
                full_response += token
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as exc:
            full_response = f"❌ LLM error: {exc}"
            placeholder.error(full_response)

        if pipeline_info:
            with st.expander("🔧 Pipeline trace", expanded=False):
                for info in pipeline_info:
                    st.markdown(f"- {info}")

    st.session_state.messages.append({
        "role": "assistant", "content": full_response,
        "source": source_key, "search_engine": search_engine_label,
    })
