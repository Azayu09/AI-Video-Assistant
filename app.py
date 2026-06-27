"""
AI Meeting Assistant — Frontend
================================
This file is responsible ONLY for presentation / UX.
The AI pipeline (utils.audio_processor, core.transcriber, core.summarizer,
core.extractor, core.rag_engine) is untouched — every backend function is
called exactly as before, with the same arguments and the same
st.session_state keys (`result`, `chat_history`, `processing`,
`pipeline_done`, `pipeline_steps`).

Structure of this file:
  1. Page config + global CSS (design system)
  2. Session state initialisation
  3. Small render helpers (hero, processing screen, workspace sections)
  4. Pipeline runner (wires the real backend calls to the processing screen)
  5. Top-level router: landing -> processing -> workspace
"""

import os
import time
import tempfile

import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()


# ─────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG + DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Design tokens ────────────────────────────────────────────────────── */
:root {
    --bg: #0A0A0A;
    --surface: #111111;
    --surface-2: #161616;
    --border: #242424;
    --accent: #10A37F;
    --accent-soft: rgba(16,163,127,0.12);
    --accent-soft-strong: rgba(16,163,127,0.22);
    --text: #F5F5F5;
    --text-muted: #8B8B8B;
    --radius-lg: 22px;
    --radius-md: 16px;
    --radius-sm: 10px;
    --shadow-soft: 0 8px 30px rgba(0,0,0,0.35);
}

/* ── Resets ───────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }

/* Hide Streamlit chrome so the app reads as a standalone product */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 980px !important;
}

h1, h2, h3, h4, h5, h6 { font-family: 'Sora', sans-serif !important; color: var(--text) !important; }

/* ── Fade-in animation used across screens ───────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeUp 0.45s ease both; }

/* ── Glass surface ────────────────────────────────────────────────────── */
.glass {
    background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.01)), var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(6px);
}

/* ── Top-left brand mark (persists across landing/processing/workspace) ── */
.topbar-brand {
    position: fixed;
    top: 1.1rem;
    left: 1.5rem;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text);
    letter-spacing: 0.01em;
}
.topbar-brand .brand-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent-soft-strong);
    flex-shrink: 0;
}

/* ── Hero ─────────────────────────────────────────────────────────────── */
.hero-wrap { text-align: center; padding: 2.5rem 0 1rem 0; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--accent); background: var(--accent-soft);
    border: 1px solid var(--accent-soft-strong);
    padding: 0.3rem 0.8rem; border-radius: 999px; margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Sora', sans-serif; font-weight: 800;
    font-size: clamp(2rem, 4.2vw, 3rem); line-height: 1.15;
    color: var(--text); margin-bottom: 0.6rem;
}
.hero-sub {
    font-size: 1rem; color: var(--text-muted); max-width: 540px;
    margin: 0 auto; line-height: 1.6;
}

/* ── Input card on landing ───────────────────────────────────────────── */
.input-card { padding: 2rem; margin: 2rem auto 1.5rem auto; max-width: 640px; }

/* Segmented control (source mode) */
div[role="radiogroup"] {
    display: flex; gap: 0.4rem; background: var(--surface-2);
    border: 1px solid var(--border); border-radius: 999px; padding: 0.3rem;
    width: fit-content; margin: 0 auto 1.5rem auto;
}
div[role="radiogroup"] label {
    border-radius: 999px !important; padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important; color: var(--text-muted) !important;
    transition: all 0.2s ease;
}
div[role="radiogroup"] label:has(input:checked) {
    background: var(--accent) !important; color: #ffffff !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stFileUploader section {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
.stFileUploader section { border-style: dashed !important; padding: 1.2rem !important; }
label { color: var(--text-muted) !important; font-size: 0.82rem !important; }

/* Primary button */
.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 1.5rem !important;
    width: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 10px 24px var(--accent-soft) !important; }
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* ── Feature chips on landing ─────────────────────────────────────────── */
.chip-row { display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap; margin-top: 1.5rem; }
.chip {
    font-size: 0.72rem; color: var(--text-muted); border: 1px solid var(--border);
    background: var(--surface); padding: 0.35rem 0.85rem; border-radius: 999px;
}

/* ── Processing screen ────────────────────────────────────────────────── */
.processing-wrap { padding: 3rem 2.5rem; max-width: 640px; margin: 2rem auto; text-align: left; }
.processing-title { font-size: 1.4rem; font-weight: 700; text-align: center; margin-bottom: 0.3rem; }
.processing-sub { text-align: center; color: var(--text-muted); font-size: 0.85rem; margin-bottom: 2rem; }

.progress-track {
    width: 100%; height: 8px; background: var(--surface-2);
    border-radius: 999px; overflow: hidden; margin-bottom: 0.6rem;
}
.progress-fill {
    height: 100%; background: var(--accent); border-radius: 999px;
    transition: width 0.6s ease;
}
.progress-meta {
    display: flex; justify-content: space-between; font-size: 0.75rem;
    color: var(--text-muted); margin-bottom: 2rem;
}
.progress-meta b { color: var(--text); }

.step-row {
    display: flex; align-items: center; gap: 0.85rem;
    padding: 0.65rem 0; border-bottom: 1px solid var(--border);
}
.step-row:last-child { border-bottom: none; }

.step-icon {
    width: 26px; height: 26px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; border: 1.5px solid var(--border);
    color: var(--text-muted); background: var(--surface-2);
}
.step-icon.done   { background: var(--accent); border-color: var(--accent); color: #fff; }
.step-icon.active { border-color: var(--accent); color: var(--accent); animation: spin 0.9s linear infinite; }
.step-icon.pending { opacity: 0.55; }

@keyframes spin { to { transform: rotate(360deg); } }

.step-label { font-size: 0.88rem; }
.step-label.done    { color: var(--text); }
.step-label.active  { color: var(--text); font-weight: 600; }
.step-label.pending { color: var(--text-muted); }

/* ── Workspace sections ───────────────────────────────────────────────── */
.workspace-topbar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.8rem;
}
.workspace-title {
    font-family: 'Sora', sans-serif; font-weight: 800; font-size: 1.6rem;
}
.workspace-eyebrow {
    font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 0.3rem;
}

.section {
    padding: 1.8rem 2rem; margin-bottom: 1.4rem;
}
.section-title {
    display: flex; align-items: center; gap: 0.6rem;
    font-size: 1.02rem; font-weight: 700; margin-bottom: 0.9rem; color: var(--text);
}
.section-body { font-size: 0.92rem; line-height: 1.75; color: var(--text); }

/* Stat grid */
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.9rem; }
.stat-box {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1rem 1.1rem;
}
.stat-value { font-family: 'Sora', sans-serif; font-weight: 800; font-size: 1.3rem; }
.stat-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.2rem; }

/* Transcript (monospace, collapsed by default via st.expander) */
.transcript-box {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.2rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; line-height: 1.8;
    color: var(--text-muted); max-height: 320px; overflow-y: auto; white-space: pre-wrap;
}

/* Chat */
.chat-container {
    max-height: 380px; overflow-y: auto; padding: 0.4rem 0.2rem; margin-bottom: 0.8rem;
}
.chat-msg { margin-bottom: 0.9rem; display: flex; flex-direction: column; gap: 0.2rem; }
.chat-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); }
.chat-bubble { display: inline-block; padding: 0.65rem 1rem; border-radius: var(--radius-sm); font-size: 0.85rem; line-height: 1.6; max-width: 88%; }
.user-bubble { background: var(--accent-soft); border: 1px solid var(--accent-soft-strong); align-self: flex-end; }
.bot-bubble  { background: var(--surface-2); border: 1px solid var(--border); align-self: flex-start; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.6rem 0 !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 2. SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,      # True while the pipeline is actively running
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Display labels for each backend pipeline key. Only the LABEL changes —
# the underlying step keys ("audio", "transcript", "title", "summary",
# "extract", "rag") are exactly what the pipeline already emits.
PIPELINE_STEPS = [
    ("audio",      "Downloading Audio"),
    ("transcript", "Transcribing"),
    ("title",      "Translating"),
    ("summary",    "Summarizing"),
    ("extract",    "Extracting Action Items"),
    ("rag",        "Building Knowledge Base"),
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def render_hero():
    """Landing screen: welcome message + source input + analyze button."""
    st.markdown("""
    <div class="hero-wrap fade-in">
        <div class="hero-eyebrow">● AI Meeting Assistant</div>
        <div class="hero-title">Turn any meeting<br>into clear, searchable insight.</div>
        <div class="hero-sub">
            Drop in a YouTube link or upload a recording. We'll transcribe it,
            summarize it, surface action items, and let you chat with it.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass input-card fade-in">', unsafe_allow_html=True)

    source_mode = st.radio(
        "Source",
        ["YouTube Link", "Upload Recording"],
        horizontal=True,
        label_visibility="collapsed",
    )

    source = ""
    if source_mode == "YouTube Link":
        source = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload audio or video",
            type=["mp3", "wav", "m4a", "mp4", "mov", "webm"],
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            # Persist the upload to a temp path so the existing
            # process_input(source) pipeline call can stay unchanged —
            # it just receives a file path instead of a URL.
            suffix = os.path.splitext(uploaded_file.name)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(uploaded_file.getbuffer())
            tmp.close()
            source = tmp.name

    col_lang, col_btn = st.columns([1, 1.4])
    with col_lang:
        language = st.selectbox("Language", ["english", "hinglish"], index=0, label_visibility="visible")
    with col_btn:
        st.markdown("<div style='height:1.55rem'></div>", unsafe_allow_html=True)  # align with selectbox
        analyze_clicked = st.button("Analyze Meeting", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="chip-row fade-in">
        <span class="chip">Transcription</span>
        <span class="chip">Summarization</span>
        <span class="chip">Action Items</span>
        <span class="chip">Knowledge Base Chat</span>
    </div>
    """, unsafe_allow_html=True)

    return source, language, analyze_clicked


def render_processing_frame(placeholder, start_time):
    """
    Render the full animated processing screen into `placeholder`.
    Reads live progress from st.session_state.pipeline_steps, so calling
    this after each pipeline stage produces a smoothly updating UI.
    """
    steps = st.session_state.pipeline_steps
    total = len(PIPELINE_STEPS)
    done_count = sum(1 for key, _ in PIPELINE_STEPS if steps.get(key) == "done")
    percent = int((done_count / total) * 100)

    elapsed = time.time() - start_time
    if done_count > 0:
        avg_per_step = elapsed / done_count
        remaining_seconds = max(0, round(avg_per_step * (total - done_count)))
        eta_text = f"~{remaining_seconds}s remaining"
    else:
        eta_text = "Calculating…"

    steps_html = ""
    for key, label in PIPELINE_STEPS:
        state = steps.get(key, "pending")
        if state == "done":
            icon, icon_cls, label_cls = "✓", "done", "done"
        elif state == "active":
            icon, icon_cls, label_cls = "", "active", "active"
        else:
            icon, icon_cls, label_cls = "", "pending", "pending"

        steps_html += f"""
        <div class="step-row">
            <div class="step-icon {icon_cls}">{icon}</div>
            <div class="step-label {label_cls}">{label}</div>
        </div>"""

    html = f"""
    <div class="glass processing-wrap fade-in">
        <div class="processing-title">Analyzing your meeting</div>
        <div class="processing-sub">This usually takes about a minute — feel free to wait here.</div>
        <div class="progress-track">
            <div class="progress-fill" style="width:{percent}%;"></div>
        </div>
        <div class="progress-meta">
            <span><b>{percent}%</b> complete</span>
            <span>{eta_text}</span>
        </div>
        {steps_html}
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)


def render_overview_section(r):
    st.markdown(f"""
    <div class="glass section fade-in">
        <div class="section-title">📌 Overview</div>
        <div class="section-body">{r['summary']}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stats_section(r):
    word_count = len(r["transcript"].split()) if r.get("transcript") else 0
    read_minutes = max(1, round(word_count / 200))
    st.markdown(f"""
    <div class="glass section fade-in">
        <div class="section-title">📊 Meeting Statistics</div>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{word_count:,}</div>
                <div class="stat-label">Words Transcribed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">~{read_minutes} min</div>
                <div class="stat-label">Read Time</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">Ready</div>
                <div class="stat-label">Knowledge Base</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_list_section(title, icon, content):
    st.markdown(f"""
    <div class="glass section fade-in">
        <div class="section-title">{icon} {title}</div>
        <div class="section-body">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_transcript_section(transcript):
    st.markdown('<div class="glass section fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗒️ Transcript</div>', unsafe_allow_html=True)
    with st.expander("Show full transcript", expanded=False):
        st.markdown(f'<div class="transcript-box">{transcript}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_chat_section(r):
    st.markdown('<div class="glass section fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 Chat with this Meeting</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label">Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-body" style="color:var(--text-muted)">Ask anything about this meeting — e.g. "What did we decide about the launch date?"</div>', unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="Ask a question…", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear conversation", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_workspace(r):
    """Sectioned workspace shown after the pipeline has completed."""
    st.markdown(f"""
    <div class="workspace-topbar fade-in">
        <div>
            <div class="workspace-eyebrow">Meeting analyzed</div>
            <div class="workspace-title">{r['title']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    new_analysis = st.button("🔄  New Analysis", type="secondary")
    if new_analysis:
        st.session_state.result = None
        st.session_state.pipeline_done = False
        st.session_state.processing = False
        st.session_state.pipeline_steps = {}
        st.session_state.chat_history = []
        st.rerun()

    render_overview_section(r)
    render_stats_section(r)
    render_list_section("Action Items", "✅", r["action_items"])
    render_list_section("Key Decisions", "🔑", r["key_decisions"])
    render_list_section("Open Questions", "❓", r["open_questions"])
    render_transcript_section(r["transcript"])
    render_chat_section(r)


# ─────────────────────────────────────────────────────────────────────────────
# 4. PIPELINE RUNNER (unchanged backend calls, wired to the new UI)
# ─────────────────────────────────────────────────────────────────────────────
def run_pipeline(source: str, language: str, screen_placeholder):
    """Executes the existing AI pipeline, updating the processing screen
    live after every stage. No backend function signatures are changed."""

    st.session_state.pipeline_done = False
    st.session_state.result = None
    st.session_state.chat_history = []
    st.session_state.pipeline_steps = {}
    st.session_state.processing = True

    start_time = time.time()

    def update_step(key, state):
        st.session_state.pipeline_steps[key] = state
        render_processing_frame(screen_placeholder, start_time)

    try:
        update_step("audio", "active")
        chunks = process_input(source)
        update_step("audio", "done")

        update_step("transcript", "active")
        transcript = transcribe_all(chunks, language)
        update_step("transcript", "done")

        update_step("title", "active")
        title = generate_title(transcript)
        update_step("title", "done")

        update_step("summary", "active")
        summary = summarize(transcript)
        update_step("summary", "done")

        update_step("extract", "active")
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)
        update_step("extract", "done")

        update_step("rag", "active")
        rag_chain = build_rag_chain(transcript)
        update_step("rag", "done")

        st.session_state.result = {
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": decisions,
            "open_questions": questions,
            "rag_chain": rag_chain,
        }
        st.session_state.pipeline_done = True
        st.session_state.processing = False
        time.sleep(0.4)  # let the final "100% complete" frame register visually
        st.rerun()

    except Exception as e:
        for k, _ in PIPELINE_STEPS:
            if st.session_state.pipeline_steps.get(k) == "active":
                st.session_state.pipeline_steps[k] = "pending"
        st.session_state.processing = False
        screen_placeholder.markdown(
            f'<div class="glass section fade-in" style="border-color:#7f1d1d">'
            f'<div class="section-title">⚠️ Something went wrong</div>'
            f'<div class="section-body">{e}</div></div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. TOP-LEVEL ROUTER: landing → processing → workspace
# ─────────────────────────────────────────────────────────────────────────────

# Persistent project name, top-left corner, visible on every screen.
st.markdown(
    '<div class="topbar-brand"><span class="brand-dot"></span>AI Meeting Assistant</div>',
    unsafe_allow_html=True,
)

if st.session_state.pipeline_done and st.session_state.result:
    render_workspace(st.session_state.result)

elif st.session_state.processing:
    placeholder = st.empty()
    # If we got here via a fresh button click, `run_pipeline` (called below)
    # drives this placeholder live. If a rerun lands here mid-flight, just
    # repaint the last known state.
    render_processing_frame(placeholder, time.time())

else:
    source, language, analyze_clicked = render_hero()

    if analyze_clicked:
        if not source or not str(source).strip():
            st.error("Please provide a YouTube URL or upload a recording.")
        else:
            placeholder = st.empty()
            run_pipeline(source, language, placeholder)