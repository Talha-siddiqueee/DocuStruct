"""
DocuStruct — document workspace.

Run with:  streamlit run app.py
Optional:  put config.toml inside a .streamlit/ folder next to this file
           (pins the light theme so the design never clashes with dark mode).
"""

import html
import json
import re
import tempfile
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

# The extraction engine is imported defensively so the UI always loads,
# even if the module is missing or broken. The problem is shown politely.
try:
    from extractors.document_extractor import DocumentExtractor
    EXTRACTOR_ERROR = None
except Exception as exc:  # noqa: BLE001
    DocumentExtractor = None
    EXTRACTOR_ERROR = exc


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="DocuStruct · Document Workspace",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAV = ["Dashboard", "Document Extractor", "History", "Settings"]
FORMATS = ["pdf", "docx", "xlsx", "xlsm", "txt", "jpg", "jpeg", "png", "tiff", "bmp"]
PREVIEW_LIMIT = 60_000  # characters shown in the JSON preview (download is always full)
MIN_LOADER_SECONDS = 0.9  # keeps the scanner animation from flashing on tiny files


# =====================================================
# SESSION STATE
# =====================================================

st.session_state.setdefault("page", "Dashboard")
st.session_state.setdefault("result", None)
st.session_state.setdefault("result_meta", None)
st.session_state.setdefault("history", [])


def go_to(page_name):
    """Button callback: safe way to change the radio-controlled page."""
    st.session_state.page = page_name


def clear_session():
    st.session_state.history = []
    st.session_state.result = None
    st.session_state.result_meta = None
    st.session_state.flash = "Session history cleared."


# =====================================================
# STYLES
# =====================================================

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

@property --n { syntax: '<integer>'; inherits: false; initial-value: 0; }

:root {
    --paper: #F2EDE1;
    --paper-2: #FAF7EF;
    --paper-3: #E9E2D0;
    --ink: #16140F;
    --ink-2: #4A453B;
    --mute: #6E6859;
    --hair: rgba(22, 20, 15, .16);
    --accent: #E8472B;
    --accent-d: #C23516;
    --hi: #F5D547;
    --ok: #2F6B4F;
    --r: 6px;
    --display: 'Bricolage Grotesque', 'IBM Plex Sans', system-ui, sans-serif;
    --body: 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
    --mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    color-scheme: light;
}

/* ---------- base ---------- */

html, body { background: var(--paper); }

.stApp {
    background: var(--paper);
    color: var(--ink);
    font-family: var(--body);
    -webkit-font-smoothing: antialiased;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: .06;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .7 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }
footer { visibility: hidden; }

.block-container {
    padding: 3rem 2.6rem 3rem;
    max-width: 1180px;
}

::selection { background: var(--hi); color: var(--ink); }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--ink); border-radius: 10px; border: 2px solid var(--paper); }

button:focus-visible, [role="radio"]:focus-visible, input:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

/* ---------- motion primitives ---------- */

@keyframes rise { from { opacity: 0; transform: translateY(18px); } }
@keyframes reveal { to { transform: translateY(0); } }
@keyframes hl { to { background-size: 100% 36%; } }
@keyframes grow { from { transform: scaleX(0); } }
@keyframes ping { 0% { transform: scale(.4); opacity: .9; } 100% { transform: scale(1.5); opacity: 0; } }
@keyframes marquee { to { transform: translateX(-50%); } }
@keyframes countUp { from { --n: 0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes floatA { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-7px); } }
@keyframes floatB { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(6px); } }

.rise { animation: rise .8s cubic-bezier(.2, .8, .2, 1) backwards; }

/* ---------- sidebar ---------- */

[data-testid="stSidebar"] {
    background: var(--paper-3);
    border-right: 1.5px solid var(--ink);
}

.brand { display: flex; align-items: center; gap: 12px; padding: 6px 2px 0; }
.brand svg { flex: none; transition: transform .5s cubic-bezier(.2, .8, .2, 1); }
.brand:hover svg { transform: rotate(-8deg) scale(1.07); }
.brand .nm { font: 800 25px/1 var(--display); letter-spacing: -.03em; color: var(--ink); }
.brand .nm i { font-style: normal; color: var(--accent); }
.brand-sub {
    font: 500 10px var(--mono);
    letter-spacing: .2em;
    text-transform: uppercase;
    color: var(--mute);
    margin: 12px 0 6px;
}
.side-h {
    font: 600 10.5px var(--mono);
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--mute);
    margin: 26px 0 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.side-h::after { content: ""; flex: 1; height: 1px; background: var(--hair); }

[data-testid="stRadio"] [role="radiogroup"] { gap: 6px; width: 100%; }

[data-testid="stRadio"] label[data-baseweb="radio"] {
    width: 100%;
    margin: 0;
    padding: 11px 14px;
    border: 1.5px solid transparent;
    border-radius: var(--r);
    cursor: pointer;
    transition: transform .25s cubic-bezier(.2, .8, .2, 1), background .2s, border-color .2s, box-shadow .25s;
}

[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child:not([data-testid="stMarkdownContainer"]) {
    display: none;
}

[data-testid="stRadio"] label[data-baseweb="radio"] * {
    font: 500 12.5px var(--mono) !important;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--ink) !important;
}

[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: var(--paper-2);
    border-color: var(--ink);
    transform: translateX(4px);
}

[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: var(--ink);
    border-color: var(--ink);
    box-shadow: 4px 4px 0 var(--accent);
}

[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) * {
    color: var(--paper) !important;
}

.status { border: 1.5px solid var(--ink); border-radius: var(--r); background: var(--paper-2); }
.status-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 13px;
    font: 500 12px var(--body);
    color: var(--ink);
}
.status-row + .status-row { border-top: 1px solid var(--hair); }
.status-row b { margin-left: auto; font: 600 10px var(--mono); letter-spacing: .14em; color: var(--mute); }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--ok); flex: none; position: relative; }
.dot.bad { background: var(--accent); }
.dot.live::after {
    content: "";
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    border: 1.5px solid var(--ok);
    animation: ping 1.9s ease-out infinite;
}
.side-foot { margin-top: 28px; font: 500 10.5px/1.8 var(--mono); letter-spacing: .1em; color: var(--mute); text-transform: uppercase; }

/* ---------- masthead + type ---------- */

.masthead {
    display: flex;
    align-items: center;
    gap: 14px;
    font: 500 11px/1 var(--mono);
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--ink);
    padding-bottom: 13px;
    border-bottom: 1.5px solid var(--ink);
    margin-bottom: 40px;
}
.masthead .grow {
    flex: 1;
    height: 1px;
    background: repeating-linear-gradient(90deg, var(--ink) 0 2px, transparent 2px 7px);
    opacity: .35;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 11px;
    font: 500 11px var(--mono);
    letter-spacing: .16em;
    text-transform: uppercase;
    color: var(--accent-d);
}
.pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); position: relative; flex: none; }
.pulse-dot::after {
    content: "";
    position: absolute;
    inset: -5px;
    border-radius: 50%;
    border: 1.5px solid var(--accent);
    animation: ping 1.8s ease-out infinite;
}

.display {
    font-family: var(--display);
    font-weight: 800;
    font-size: clamp(40px, 5.2vw, 68px);
    line-height: .98;
    letter-spacing: -.035em;
    color: var(--ink);
    margin: 18px 0 22px;
}
.display.md { font-size: clamp(34px, 4.2vw, 54px); margin: 16px 0 18px; }

.reveal { display: block; overflow: hidden; padding-bottom: .12em; margin-bottom: -.12em; }
.reveal > span {
    display: inline-block;
    transform: translateY(112%);
    animation: reveal .95s cubic-bezier(.2, .8, .2, 1) forwards;
}

.hl {
    background-image: linear-gradient(var(--hi), var(--hi));
    background-repeat: no-repeat;
    background-position: 0 90%;
    background-size: 0% 36%;
    animation: hl .9s cubic-bezier(.2, .8, .2, 1) .95s forwards;
    -webkit-box-decoration-break: clone;
    box-decoration-break: clone;
}

.lead { font-size: 17px; line-height: 1.65; color: var(--ink-2); max-width: 540px; margin-bottom: 26px; }
.pghead { margin-bottom: 26px; }

/* ---------- hero artwork ---------- */

.hero-art {
    position: relative;
    border: 1.5px solid var(--ink);
    border-radius: var(--r);
    background-color: var(--paper-2);
    background-image: radial-gradient(rgba(22, 20, 15, .17) 1px, transparent 1.4px);
    background-size: 18px 18px;
    box-shadow: 7px 7px 0 var(--ink);
    overflow: hidden;
    animation: rise .9s cubic-bezier(.2, .8, .2, 1) .15s backwards;
}
.hero-art svg { display: block; width: 100%; height: auto; }
.hero-art text { font-family: var(--mono); }

.hero-art .ln { fill: #D9D0BA; animation: lit 6s linear infinite backwards; }
.hero-art .scan { opacity: 0; animation: scan 6s linear infinite; }
.hero-art .chipg { animation: chipIn 6s linear infinite backwards; }
.hero-art .conn { stroke-dasharray: 4 4; animation: connIn 6s linear infinite backwards, march .7s linear infinite; }
.hero-art .fl-a { animation: floatA 8s ease-in-out infinite; }
.hero-art .fl-b { animation: floatB 9s ease-in-out infinite; }
.hero-art .ring { transform-box: fill-box; transform-origin: center; animation: spin 14s linear infinite; }

@keyframes lit { 0% { fill: #D9D0BA; } 3% { fill: #16140F; } 50% { fill: #16140F; } 62% { fill: #D9D0BA; } 100% { fill: #D9D0BA; } }
@keyframes scan {
    0% { transform: translateY(96px); opacity: 0; }
    4% { opacity: 1; }
    50% { transform: translateY(312px); opacity: 1; }
    56% { transform: translateY(312px); opacity: 0; }
    100% { transform: translateY(312px); opacity: 0; }
}
@keyframes chipIn {
    0% { opacity: 0; transform: translateX(-14px); }
    4% { opacity: 1; transform: translateX(0); }
    52% { opacity: 1; transform: translateX(0); }
    64% { opacity: 0; transform: translateX(6px); }
    100% { opacity: 0; transform: translateX(6px); }
}
@keyframes connIn { 0% { opacity: 0; } 3% { opacity: 1; } 52% { opacity: 1; } 64% { opacity: 0; } 100% { opacity: 0; } }
@keyframes march { to { stroke-dashoffset: -16; } }

/* ---------- ticker ---------- */

.ticker {
    overflow: hidden;
    background: var(--ink);
    color: var(--paper);
    border-radius: var(--r);
    margin: 48px 0 6px;
    padding: 14px 0;
    animation: rise .8s cubic-bezier(.2, .8, .2, 1) .3s backwards;
}
.ticker-track { display: inline-flex; white-space: nowrap; animation: marquee 34s linear infinite; will-change: transform; }
.ticker:hover .ticker-track { animation-play-state: paused; }
.ticker-item {
    display: inline-flex;
    align-items: center;
    gap: 22px;
    padding-right: 22px;
    font: 500 13px var(--mono);
    letter-spacing: .2em;
    text-transform: uppercase;
    color: var(--paper);
}
.ticker-item i { width: 7px; height: 7px; background: var(--accent); transform: rotate(45deg); display: inline-block; }

/* ---------- sections, metrics, rows ---------- */

.sec { display: flex; align-items: center; gap: 16px; margin: 58px 0 22px; animation: rise .8s cubic-bezier(.2, .8, .2, 1) backwards; }
.sec .no { font: 500 12px var(--mono); letter-spacing: .14em; color: var(--accent-d); }
.sec .ttl { font: 700 30px/1.05 var(--display); letter-spacing: -.025em; color: var(--ink); }
.sec .rule { flex: 1; height: 1.5px; background: var(--ink); transform-origin: left; animation: grow 1.1s cubic-bezier(.2, .8, .2, 1) .15s backwards; }

.metric {
    background: var(--paper-2);
    border: 1.5px solid var(--ink);
    border-radius: var(--r);
    padding: 20px 22px 22px;
    min-height: 122px;
    transition: transform .25s cubic-bezier(.2, .8, .2, 1), box-shadow .25s;
    animation: rise .8s cubic-bezier(.2, .8, .2, 1) backwards;
}
.metric:hover { transform: translate(-3px, -3px); box-shadow: 5px 5px 0 var(--ink); }
.metric .k { font: 500 10.5px var(--mono); letter-spacing: .16em; text-transform: uppercase; color: var(--mute); }
.metric .v { font: 700 40px/1.05 var(--display); letter-spacing: -.03em; margin-top: 16px; color: var(--ink); overflow-wrap: anywhere; }
.metric .v.sm { font-size: 21px; letter-spacing: -.01em; line-height: 1.25; margin-top: 18px; }

.cnt { counter-reset: num var(--n); animation: countUp 1.6s cubic-bezier(.2, .8, .2, 1) backwards; }
.cnt::after { content: counter(num); }

.index { border-top: 1.5px solid var(--ink); }
.row {
    position: relative;
    isolation: isolate;
    display: grid;
    grid-template-columns: 56px 1.1fr 1.7fr auto;
    gap: 20px;
    align-items: baseline;
    padding: 24px 12px;
    border-bottom: 1px solid var(--hair);
    animation: rise .8s cubic-bezier(.2, .8, .2, 1) backwards;
}
.row::before {
    content: "";
    position: absolute;
    inset: 0;
    background: var(--hi);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform .5s cubic-bezier(.2, .8, .2, 1);
    z-index: -1;
}
.row:hover::before { transform: scaleX(1); }
.row .n { font: 500 12px var(--mono); letter-spacing: .12em; color: var(--accent-d); }
.row .t { font: 700 25px/1.1 var(--display); letter-spacing: -.02em; color: var(--ink); transition: transform .4s cubic-bezier(.2, .8, .2, 1); }
.row:hover .t { transform: translateX(8px); }
.row .d { font-size: 15px; line-height: 1.6; color: var(--ink-2); }
.row .tg { font: 500 10.5px var(--mono); letter-spacing: .12em; color: var(--ink); white-space: nowrap; border: 1.5px solid var(--ink); border-radius: 999px; padding: 4px 11px; background: var(--paper-2); }

.ledger { border-top: 1.5px solid var(--ink); }
.entry {
    display: grid;
    grid-template-columns: 52px 1fr auto auto;
    gap: 18px;
    align-items: center;
    padding: 16px 12px;
    border-bottom: 1px solid var(--hair);
    transition: background .25s, padding .3s cubic-bezier(.2, .8, .2, 1);
    animation: rise .7s cubic-bezier(.2, .8, .2, 1) backwards;
}
.entry:hover { background: var(--paper-3); padding-left: 20px; }
.entry .n { font: 500 12px var(--mono); color: var(--mute); }
.entry .f { font-weight: 600; font-size: 15px; overflow-wrap: anywhere; color: var(--ink); }
.entry .m { font: 400 11px var(--mono); letter-spacing: .08em; color: var(--mute); text-transform: uppercase; margin-top: 3px; }
.entry .w { font: 400 11px var(--mono); letter-spacing: .08em; color: var(--mute); text-transform: uppercase; text-align: right; }

.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 22px; }
.chip {
    display: inline-block;
    border: 1.5px solid var(--ink);
    border-radius: 999px;
    padding: 3px 11px;
    font: 600 10.5px var(--mono);
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--ink);
    background: var(--paper-2);
    transition: transform .2s, background .2s;
}
.chips .chip:hover { background: var(--hi); transform: translateY(-2px); }
.chip.ok { background: var(--ok); border-color: var(--ok); color: #fff; }
.chip.soon { background: transparent; border-style: dashed; color: var(--mute); border-color: var(--mute); }

.note {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    border: 1.5px solid var(--ink);
    border-radius: var(--r);
    padding: 14px 16px;
    background: var(--paper-2);
    font-size: 14px;
    line-height: 1.55;
    color: var(--ink);
    margin: 14px 0;
    animation: rise .6s cubic-bezier(.2, .8, .2, 1) backwards;
}
.note b { font: 600 10.5px var(--mono); letter-spacing: .14em; text-transform: uppercase; padding: 4px 9px; border-radius: 3px; background: var(--ink); color: var(--paper); white-space: nowrap; }
.note span { flex: 1; overflow-wrap: anywhere; padding-top: 1px; }
.note.ok b { background: var(--ok); color: #fff; }
.note.err { border-color: var(--accent-d); background: #FCEDE8; }
.note.err b { background: var(--accent-d); color: #fff; }

.cap { font: 500 11px var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--mute); margin: 4px 0 12px; }

.kv { border-top: 1.5px solid var(--ink); }
.kvr { display: flex; align-items: baseline; gap: 14px; padding: 15px 4px; border-bottom: 1px solid var(--hair); animation: rise .7s cubic-bezier(.2, .8, .2, 1) backwards; }
.kvr .k { font: 500 11.5px var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--mute); }
.kvr .dots { flex: 1; border-bottom: 1.5px dotted rgba(22, 20, 15, .3); transform: translateY(-4px); }
.kvr .v { font-weight: 600; color: var(--ink); }

.empty { text-align: center; border: 1.5px dashed var(--ink); border-radius: var(--r); padding: 46px 20px 40px; background: var(--paper-2); animation: rise .8s cubic-bezier(.2, .8, .2, 1) backwards; }
.empty svg { width: 150px; height: auto; }
.empty .t { font: 700 26px var(--display); letter-spacing: -.02em; margin-top: 6px; color: var(--ink); }
.empty .d { color: var(--mute); font-size: 14.5px; margin-top: 6px; }
.empty .fl-a { animation: floatA 4s ease-in-out infinite; }

.footer {
    margin-top: 76px;
    padding-top: 18px;
    border-top: 1.5px solid var(--ink);
    display: flex;
    justify-content: space-between;
    gap: 14px;
    flex-wrap: wrap;
    font: 500 11px var(--mono);
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--mute);
}

/* ---------- uploader ---------- */

[data-testid="stFileUploader"] { color: var(--ink); }
[data-testid="stFileUploader"] small { color: var(--mute); }

[data-testid="stFileUploaderDropzone"] {
    background: var(--paper-2);
    border: 1.5px dashed var(--ink);
    border-radius: var(--r);
    padding: 28px;
    transition: transform .25s cubic-bezier(.2, .8, .2, 1), box-shadow .25s, background .2s;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: #FFFDF7;
    border-style: solid;
    transform: translate(-3px, -3px);
    box-shadow: 5px 5px 0 var(--ink);
}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] p { color: var(--ink-2); }
[data-testid="stFileUploaderDropzone"] button {
    background: var(--ink);
    color: var(--paper);
    border: 1.5px solid var(--ink);
    border-radius: var(--r);
    font: 600 12px var(--mono);
    letter-spacing: .1em;
    text-transform: uppercase;
    transition: background .2s, color .2s;
}
[data-testid="stFileUploaderDropzone"] button:hover { background: var(--accent); color: var(--ink); border-color: var(--ink); }
[data-testid="stFileUploaderDropzone"] button * { color: inherit; }

/* ---------- buttons ---------- */

.stButton > button, .stDownloadButton > button {
    font: 600 13px var(--mono);
    letter-spacing: .1em;
    text-transform: uppercase;
    border: 1.5px solid var(--ink);
    border-radius: var(--r);
    padding: .8rem 1.5rem;
    min-height: 0;
    box-shadow: 0 0 0 var(--ink);
    transition: transform .2s cubic-bezier(.2, .8, .2, 1), box-shadow .2s, background .2s, color .2s;
}
.stButton > button *, .stDownloadButton > button * { color: inherit !important; font: inherit !important; }

.stButton > button, .stButton > button:focus:not(:active) {
    background: var(--ink);
    color: var(--paper);
    border-color: var(--ink);
}
.stButton > button:hover, .stButton > button:hover:focus:not(:active) {
    background: var(--accent);
    color: var(--ink);
    border-color: var(--ink);
    transform: translate(-3px, -3px);
    box-shadow: 4px 4px 0 var(--ink);
}
.stButton > button:active { transform: translate(0, 0); box-shadow: 0 0 0 var(--ink); }
.stButton > button:disabled { opacity: .4; transform: none; box-shadow: none; background: var(--ink); color: var(--paper); }

.stDownloadButton > button, .stDownloadButton > button:focus:not(:active) {
    background: var(--hi);
    color: var(--ink);
    border-color: var(--ink);
}
.stDownloadButton > button:hover, .stDownloadButton > button:hover:focus:not(:active) {
    background: #FFE46B;
    color: var(--ink);
    border-color: var(--ink);
    transform: translate(-3px, -3px);
    box-shadow: 4px 4px 0 var(--ink);
}

/* ---------- tabs, json, code ---------- */

[data-baseweb="tab-list"] { gap: 6px; background: transparent; border-bottom: 1.5px solid var(--ink); }
button[data-baseweb="tab"] {
    background: transparent;
    border-radius: var(--r) var(--r) 0 0;
    padding: 10px 18px;
    transition: background .2s, color .2s;
}
button[data-baseweb="tab"] * { font: 600 12px var(--mono) !important; letter-spacing: .08em; text-transform: uppercase; color: var(--mute) !important; }
button[data-baseweb="tab"]:hover { background: var(--paper-3); }
button[data-baseweb="tab"]:hover * { color: var(--ink) !important; }
button[data-baseweb="tab"][aria-selected="true"] { background: var(--ink); }
button[data-baseweb="tab"][aria-selected="true"] * { color: var(--paper) !important; }
[data-baseweb="tab-highlight"] { background: var(--accent); height: 3px; }
[data-baseweb="tab-border"] { background: transparent; }
[data-baseweb="tab-panel"] { padding-top: 18px; }

[data-testid="stJson"] {
    background: var(--paper-2);
    border: 1.5px solid var(--ink);
    border-radius: var(--r);
    padding: 16px;
    color: var(--ink);
}

[data-testid="stCode"] { border: 1.5px solid var(--ink); border-radius: var(--r); background: var(--paper-2); }
[data-testid="stCode"] pre { background: var(--paper-2) !important; }
[data-testid="stCode"] code { font-family: var(--mono) !important; font-size: 13px; }

/* ---------- scanner loader ---------- */

.loader {
    display: grid;
    grid-template-columns: 112px 1fr;
    gap: 26px;
    align-items: center;
    border: 1.5px solid var(--ink);
    border-radius: var(--r);
    padding: 22px 26px;
    background: var(--paper-2);
    box-shadow: 6px 6px 0 var(--ink);
    margin: 18px 0;
}
.loader .sheet {
    position: relative;
    width: 96px;
    height: 124px;
    border: 1.5px solid var(--ink);
    border-radius: 3px;
    background: var(--paper);
    overflow: hidden;
    padding-top: 14px;
}
.loader .sheet i {
    display: block;
    height: 6px;
    border-radius: 3px;
    background: rgba(22, 20, 15, .2);
    margin: 0 0 9px 12px;
    animation: inkp 1.6s ease-in-out infinite alternate;
}
.loader .sheet i:nth-child(2) { animation-delay: .15s; }
.loader .sheet i:nth-child(3) { animation-delay: .3s; }
.loader .sheet i:nth-child(4) { animation-delay: .45s; }
.loader .sheet i:nth-child(5) { animation-delay: .6s; }
.loader .sheet i:nth-child(6) { animation-delay: .75s; }
.loader .beam {
    position: absolute;
    left: -4px;
    right: -4px;
    top: 0;
    height: 3px;
    background: var(--accent);
    box-shadow: 0 0 14px 3px rgba(232, 71, 43, .45);
    animation: beam 1.6s ease-in-out infinite alternate;
}
.loader .stat { position: relative; height: 34px; font: 700 24px var(--display); letter-spacing: -.02em; color: var(--ink); }
.loader .stat span { position: absolute; left: 0; top: 0; opacity: 0; white-space: nowrap; animation: cycle 4.5s infinite; }
.loader .stat span:nth-child(2) { animation-delay: 1.5s; }
.loader .stat span:nth-child(3) { animation-delay: 3s; }
.loader .bar { position: relative; height: 7px; border: 1.5px solid var(--ink); border-radius: 99px; overflow: hidden; margin: 14px 0 12px; }
.loader .bar::after { content: ""; position: absolute; top: 0; bottom: 0; width: 34%; background: var(--accent); border-radius: 99px; animation: slide 1.3s ease-in-out infinite; }
.loader .m { font: 500 11px var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--mute); }

@keyframes beam { from { transform: translateY(8px); } to { transform: translateY(112px); } }
@keyframes inkp { from { background: rgba(22, 20, 15, .14); } to { background: rgba(22, 20, 15, .75); } }
@keyframes cycle {
    0% { opacity: 0; transform: translateY(10px); }
    6%, 30% { opacity: 1; transform: none; }
    36%, 100% { opacity: 0; transform: translateY(-10px); }
}
@keyframes slide { from { left: -34%; } to { left: 100%; } }

/* ---------- responsive + reduced motion ---------- */

@media (max-width: 820px) {
    .block-container { padding: 2.4rem 1.1rem 2.4rem; }
    .row { grid-template-columns: 40px 1fr; gap: 8px 14px; }
    .row .d, .row .tg { grid-column: 2; justify-self: start; }
    .entry { grid-template-columns: 40px 1fr; }
    .entry .chip, .entry .w { grid-column: 2; justify-self: start; text-align: left; }
    .loader { grid-template-columns: 1fr; }
    .masthead span:nth-child(2) { display: none; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .001s !important;
        animation-delay: 0s !important;
        animation-iteration-count: 1 !important;
        transition-duration: .001s !important;
    }
    .ticker-track { animation: none !important; }
}
/* ---------- sidebar text visibility fix ---------- */

/* Navigate and System headings */
.side-h {
    color: #29251F !important;
    font-weight: 700;
}

/* Navigation menu text */
[data-testid="stRadio"] label[data-baseweb="radio"] p,
[data-testid="stRadio"] label[data-baseweb="radio"] span {
    color: #29251F !important;
    font-weight: 600 !important;
}

/* Selected navigation item */
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p,
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) span {
    color: #FAF7EF !important;
}
/* Sidebar navigation text visibility fix */
[data-testid="stRadio"] label,
[data-testid="stRadio"] label p,
[data-testid="stRadio"] label span,
[data-testid="stRadio"] label div {
    color: #3D3429 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

/* Navigate heading */
.side-h {
    color: #3D3429 !important;
    font-weight: 700 !important;
}
"""

st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)


# =====================================================
# HELPERS
# =====================================================

def esc(value):
    return html.escape(str(value), quote=True)


def flat(markup):
    """Collapse markup to one line so Markdown never mistakes it for code."""
    return "".join(line.strip() for line in markup.strip().splitlines())


def render(markup):
    st.markdown(flat(markup), unsafe_allow_html=True)


def human_size(num):
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "—"
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024 or unit == "GB":
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024


def nav_label(page_name):
    return f"{NAV.index(page_name) + 1:02d} · {page_name}"


def section(number, title):
    render(
        f'<div class="sec"><span class="no">{esc(number)}</span>'
        f'<span class="ttl">{esc(title)}</span><span class="rule"></span></div>'
    )


def notice(kind, label, text):
    text = " ".join(str(text).split())
    render(f'<div class="note {kind}"><b>{esc(label)}</b><span>{esc(text)}</span></div>')


def metric_card(label, value=None, *, count=None, suffix="", small=False, delay=0.0):
    if count is not None:
        n = max(0, int(count))
        body = f'<span class="cnt cnt-{n}"></span>{esc(suffix)}'
        extra = f"<style>.cnt-{n}{{--n:{n}}}</style>"
        cls = "v"
    else:
        body = esc(value)
        extra = ""
        cls = "v sm" if small else "v"
    render(
        f'<div class="metric" style="animation-delay:{delay:.2f}s">'
        f'<div class="k">{esc(label)}</div><div class="{cls}">{body}</div></div>{extra}'
    )


def page_head(number, eyebrow, line1, line2_html, lead):
    render(
        f'<div class="pghead"><div class="eyebrow rise">{number} — {eyebrow}</div>'
        f'<div class="display md"><span class="reveal"><span style="animation-delay:.05s">{line1}</span></span>'
        f'<span class="reveal"><span style="animation-delay:.2s">{line2_html}</span></span></div>'
        f'<div class="lead rise" style="animation-delay:.35s">{lead}</div></div>'
    )


def format_chips():
    chips = "".join(f'<span class="chip">{esc(f)}</span>' for f in FORMATS)
    render(f'<div class="chips rise">{chips}</div>')


def ledger(items, total):
    rows = []
    for i, item in enumerate(items):
        rows.append(
            f'<div class="entry" style="animation-delay:{min(i, 10) * 0.05:.2f}s">'
            f'<span class="n">{total - i:02d}</span>'
            f'<div><div class="f">{esc(item["file_name"])}</div>'
            f'<div class="m">{esc(item["document_type"])}</div></div>'
            f'<span class="chip">{esc(item["file_type"])}</span>'
            f'<span class="w">{esc(item["processed_at"])}</span></div>'
        )
    render(f'<div class="ledger">{"".join(rows)}</div>')


# =====================================================
# ARTWORK + STATIC BLOCKS
# =====================================================

def hero_art():
    """Animated illustration: a messy page is scanned and turned into structured fields."""
    widths = [150, 168, 118, 160, 94, 150, 128, 168, 84]
    y0, step = 108, 24

    def reach(y):  # seconds until the scan beam reaches y
        return max(0.0, (y - 96) / 216 * 3.0)

    bars = "".join(
        f'<rect class="ln" x="62" y="{y0 + i * step}" width="{w}" height="7" rx="3.5" '
        f'style="animation-delay:{reach(y0 + i * step + 3.5):.2f}s"/>'
        for i, w in enumerate(widths)
    )

    spec = [
        ("EMAIL", "hello@northwind.co", 1, False),
        ("DATE", "14 Nov 2026", 3, False),
        ("PHONE", "+91 98765 43210", 5, False),
        ("AMOUNT", "₹ 48,250.00", 7, True),
    ]
    chips = []
    for j, (key, val, src, hot) in enumerate(spec):
        top = 70 + j * 68
        sy = y0 + src * step + 3.5
        sx = 62 + widths[src] + 8
        t = reach(sy) + 0.3
        fill = "#F5D547" if hot else "#FAF7EF"
        chips.append(
            f'<path class="conn" d="M{sx} {sy} C{sx + 36} {sy} 282 {top + 22} 310 {top + 22}" fill="none" '
            f'stroke="#E8472B" stroke-width="1.6" stroke-linecap="round" style="animation-delay:{t - 0.2:.2f}s,0s"/>'
            f'<g class="chipg" style="animation-delay:{t:.2f}s">'
            f'<rect x="314" y="{top + 4}" width="200" height="44" rx="4" fill="#16140F"/>'
            f'<rect x="310" y="{top}" width="200" height="44" rx="4" fill="{fill}" stroke="#16140F" stroke-width="1.5"/>'
            f'<circle cx="310" cy="{top + 22}" r="4.5" fill="#E8472B" stroke="#16140F" stroke-width="1.5"/>'
            f'<text x="326" y="{top + 18}" font-size="9" letter-spacing="1.6" fill="#6E6859">{key}</text>'
            f'<text x="326" y="{top + 35}" font-size="13" font-weight="600" fill="#16140F">{val}</text>'
            f'</g>'
        )
    chips = "".join(chips)

    return f"""
    <div class="hero-art" role="img" aria-label="A messy document is scanned and turned into structured fields">
    <svg viewBox="0 0 540 420" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#16140F" stroke-width="1.5" fill="none" opacity=".5">
    <path d="M14 24V14h10M516 14h10v10M14 396v10h10M526 396v10h-10"/>
    </g>
    <text x="44" y="38" font-size="10" letter-spacing="2" fill="#6E6859">INPUT · MESSY</text>
    <text x="310" y="38" font-size="10" letter-spacing="2" fill="#6E6859">OUTPUT · STRUCTURED</text>
    <g class="fl-a"><rect x="40" y="70" width="204" height="296" rx="3" fill="#E7DFCB" stroke="#16140F" stroke-width="1.5" transform="rotate(-6 142 218)"/></g>
    <g class="fl-b"><rect x="52" y="62" width="204" height="296" rx="3" fill="#F0E9D8" stroke="#16140F" stroke-width="1.5" transform="rotate(4 154 210)"/></g>
    <path d="M44 54H218L248 84V350H44Z" fill="#FBF8F1" stroke="#16140F" stroke-width="1.5" stroke-linejoin="round"/>
    <path d="M218 54L248 84H218Z" fill="#E7DFCB" stroke="#16140F" stroke-width="1.5" stroke-linejoin="round"/>
    <rect x="62" y="72" width="70" height="12" fill="#E8472B"/>
    <rect x="62" y="90" width="40" height="5" rx="2.5" fill="#D9D0BA"/>
    {bars}
    <g class="scan">
    <rect x="44" y="-26" width="204" height="26" fill="#E8472B" opacity=".07"/>
    <rect x="44" y="-16" width="204" height="16" fill="#E8472B" opacity=".10"/>
    <rect x="44" y="-7" width="204" height="7" fill="#E8472B" opacity=".16"/>
    <rect x="36" y="-1.5" width="220" height="3" rx="1.5" fill="#E8472B"/>
    <circle cx="36" cy="0" r="4" fill="#E8472B"/>
    <circle cx="256" cy="0" r="4" fill="#E8472B"/>
    </g>
    {chips}
    <text x="44" y="380" font-size="10.5" letter-spacing="1" fill="#6E6859">unstructured.pdf</text>
    <text x="310" y="380" font-size="10.5" letter-spacing="1" fill="#6E6859">structured.json</text>
    <g transform="translate(480 366)">
    <circle class="ring" r="26" fill="none" stroke="#E8472B" stroke-width="1.6" stroke-dasharray="3 5" stroke-linecap="round"/>
    <circle r="18" fill="#16140F"/>
    <text text-anchor="middle" y="5" font-size="14" font-weight="600" fill="#F2EDE1">{{ }}</text>
    </g>
    </svg>
    </div>
    """


def ticker():
    words = ["Extract", "PDF", "Clean", "DOCX", "Structure", "XLSX", "Identify",
             "TXT", "Export", "PNG", "JPG", "TIFF", "BMP", "XLSM"]
    items = "".join(f'<span class="ticker-item">{esc(w)}<i></i></span>' for w in words)
    render(f'<div class="ticker"><div class="ticker-track">{items}{items}</div></div>')


BRAND = """
<div class="brand">
<svg width="36" height="36" viewBox="0 0 34 34" aria-hidden="true">
<rect x="2" y="2" width="30" height="30" rx="6" fill="#16140F"/>
<path d="M10 8h9l5 5v13H10z" fill="#F2EDE1"/>
<path d="M19 8v5h5z" fill="#E8472B"/>
<rect x="13" y="17" width="8" height="1.8" fill="#16140F"/>
<rect x="13" y="20.5" width="6" height="1.8" fill="#16140F"/>
</svg>
<div class="nm">DocuStruct<i>.</i></div>
</div>
<div class="brand-sub">Document workspace</div>
"""

LOADER = """
<div class="loader">
<div class="sheet"><i style="width:62%"></i><i style="width:48%"></i><i style="width:66%"></i><i style="width:40%"></i><i style="width:58%"></i><i style="width:36%"></i><div class="beam"></div></div>
<div>
<div class="stat"><span>Reading your file…</span><span>Cleaning the text…</span><span>Structuring the output…</span></div>
<div class="bar"></div>
<div class="m">Hang tight — this usually takes a few seconds</div>
</div>
</div>
"""

EMPTY = """
<div class="empty">
<svg viewBox="0 0 160 120" aria-hidden="true">
<g class="fl-a"><rect x="46" y="12" width="68" height="56" rx="3" fill="none" stroke="#16140F" stroke-width="1.5" stroke-dasharray="5 5"/></g>
<path d="M20 70H48L56 84H104L112 70H140V104a4 4 0 0 1-4 4H24a4 4 0 0 1-4-4Z" fill="#FAF7EF" stroke="#16140F" stroke-width="1.5" stroke-linejoin="round"/>
</svg>
<div class="t">Nothing filed yet</div>
<div class="d">Documents you process in this session will be listed here.</div>
</div>
"""

CAPABILITIES = [
    ("01", "Document extraction",
     "Pull the text and tables out of PDFs, Word files, spreadsheets, plain text and images.",
     "PDF · DOCX · XLSX · IMAGES"),
    ("02", "Data cleaning",
     "Tidy whitespace, formatting and stray characters so everything downstream behaves.",
     "NORMALISE"),
    ("03", "Information extraction",
     "Spot emails, phone numbers, dates and other identifiers hiding in the text.",
     "EMAIL · PHONE · DATE"),
    ("04", "Structured results",
     "Get it all back as organised JSON, ready to download or pipe somewhere else.",
     "JSON"),
]


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    render(BRAND)
    render('<div class="side-h">Navigate</div>')

    page = st.radio(
        "Navigate",
        NAV,
        key="page",
        format_func=nav_label,
        label_visibility="collapsed",
    )

    render('<div class="side-h">System</div>')

    engine_ok = EXTRACTOR_ERROR is None
    render(
        '<div class="status">'
        f'<div class="status-row"><i class="dot {"live" if engine_ok else "bad"}"></i>'
        f'Extraction engine<b>{"ONLINE" if engine_ok else "OFFLINE"}</b></div>'
        '<div class="status-row"><i class="dot"></i>Text cleaner<b>READY</b></div>'
        '</div>'
    )

    render(
        '<div class="side-foot">DocuStruct v1.0.0<br>Made with Python &amp; Streamlit</div>'
    )


# =====================================================
# MASTHEAD (every page)
# =====================================================

render(
    '<div class="masthead rise">'
    '<span>DocuStruct</span>'
    f'<span>{esc(page)}</span>'
    '<span class="grow"></span>'
    f'<span>{esc(datetime.now().strftime("%a %d %b %Y").upper())}</span>'
    '</div>'
)


# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":

    left, right = st.columns([1.05, 1], gap="large")

    with left:
        render(
            '<div class="eyebrow rise"><i class="pulse-dot"></i>Document workspace · v1.0</div>'
            '<div class="display">'
            '<span class="reveal"><span style="animation-delay:.1s">Messy files in.</span></span>'
            '<span class="reveal"><span style="animation-delay:.28s"><span class="hl">Clean data</span> out.</span></span>'
            '</div>'
            '<div class="lead rise" style="animation-delay:.5s">'
            'Drop in a PDF, spreadsheet, scan or plain text file. DocuStruct reads it, '
            'tidies it up, and hands back structured JSON you can actually use.'
            '</div>'
        )
        st.button("Open the extractor  →", key="cta_open", on_click=go_to, args=("Document Extractor",))

    with right:
        render(hero_art())

    ticker()

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Documents processed", count=len(st.session_state.history), delay=0.1)
    with c2:
        metric_card("Supported formats", count=len(FORMATS), suffix="+", delay=0.2)
    with c3:
        metric_card("Processing mode", "Hybrid", delay=0.3)

    section("01", "What it does")

    rows = "".join(
        f'<div class="row" style="animation-delay:{0.08 * i:.2f}s">'
        f'<span class="n">{num}</span><span class="t">{esc(title)}</span>'
        f'<span class="d">{esc(desc)}</span><span class="tg">{esc(tag)}</span></div>'
        for i, (num, title, desc, tag) in enumerate(CAPABILITIES)
    )
    render(f'<div class="index">{rows}</div>')

    if st.session_state.history:
        section("02", "Recently filed")
        history = st.session_state.history
        ledger(list(reversed(history))[:3], len(history))


# =====================================================
# DOCUMENT EXTRACTOR
# =====================================================

elif page == "Document Extractor":

    page_head(
        "02", "Extractor",
        "Drop a file.",
        '<span class="hl">Get structure</span> back.',
        "Upload a document to extract, clean and organise its contents. "
        "Everything stays in this session.",
    )

    format_chips()

    if EXTRACTOR_ERROR is not None:
        notice("err", "Engine offline", f"The extraction module could not be loaded: {EXTRACTOR_ERROR}")

    uploaded = st.file_uploader(
        "Choose a document",
        type=FORMATS,
        key="uploader",
        label_visibility="collapsed",
        help="Select a supported document from your computer.",
    )

    if uploaded is not None:

        notice("info", "Ready", f"{uploaded.name} · {human_size(getattr(uploaded, 'size', None))}")

        if st.button("Extract document", key="extract_btn", disabled=EXTRACTOR_ERROR is not None):

            placeholder = st.empty()
            placeholder.markdown(flat(LOADER), unsafe_allow_html=True)
            started = time.time()
            outcome, failure = None, None

            try:
                # Keep the real file name; only strip characters that are illegal in paths.
                safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", Path(uploaded.name).name) or "document"

                with tempfile.TemporaryDirectory() as temp_dir:
                    file_path = Path(temp_dir) / safe_name
                    file_path.write_bytes(uploaded.getvalue())
                    outcome = DocumentExtractor.extract(file_path)

            except Exception as error:  # noqa: BLE001
                failure = error

            remaining = MIN_LOADER_SECONDS - (time.time() - started)
            if remaining > 0:
                time.sleep(remaining)
            placeholder.empty()

            if failure is not None:
                notice("err", "Failed", f"Something went wrong while reading this file: {failure}")
            else:
                if not isinstance(outcome, dict):
                    outcome = {"data": outcome, "cleaned_data": outcome}

                file_name = uploaded.name  # always show the name the person actually uploaded
                file_type = str(outcome.get("file_extension") or Path(uploaded.name).suffix).lstrip(".")
                stamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

                st.session_state.result = outcome
                st.session_state.result_meta = {
                    "name": file_name,
                    "type": file_type or "—",
                    "processed_at": stamp,
                }
                st.session_state.history.append({
                    "file_name": file_name,
                    "file_type": (file_type or "—").upper(),
                    "document_type": str(outcome.get("document_type") or "—"),
                    "processed_at": stamp,
                })
                notice("ok", "Done", f"{file_name} was processed successfully.")

    # ---------- results ----------

    if st.session_state.result is not None:

        result = st.session_state.result
        meta = st.session_state.result_meta or {}

        raw_data = result.get("data")
        cleaned_data = result.get("cleaned_data")
        cleaned_json = json.dumps(cleaned_data, indent=2, ensure_ascii=False, default=str)

        file_name = meta.get("name") or str(result.get("file_name") or "document")
        file_type = (meta.get("type") or "—").upper()
        engine = str(result.get("document_type") or "—")

        section("→", "Results")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card("File name", file_name, small=True, delay=0.05)
        with m2:
            metric_card("File type", file_type, delay=0.15)
        with m3:
            metric_card("Extraction engine", engine, small=True, delay=0.25)
        with m4:
            metric_card("Processed", meta.get("processed_at", "—"), small=True, delay=0.35)

        render('<div class="cap" style="margin-top:26px">Explore your data</div>')

        tab1, tab2, tab3 = st.tabs(["Original data", "Cleaned data", "JSON output"])

        def show_tree(data):
            try:
                st.json(data, expanded=2)
            except Exception:  # older Streamlit versions only accept a bool
                st.json(data)

        with tab1:
            render('<div class="cap">What the extraction engine returned</div>')
            show_tree(raw_data)

        with tab2:
            render('<div class="cap">The normalised version</div>')
            show_tree(cleaned_data)

        with tab3:
            render('<div class="cap">Structured JSON, ready for the next step</div>')
            preview = cleaned_json
            if len(preview) > PREVIEW_LIMIT:
                preview = preview[:PREVIEW_LIMIT] + "\n… preview trimmed — download the file for the full output."
            st.code(preview, language="json")

        stem = re.sub(r"[^\w\-]+", "_", Path(file_name).stem).strip("_") or "extracted_data"

        render('<div style="height:10px"></div>')
        st.download_button(
            label="Download cleaned JSON",
            data=cleaned_json,
            file_name=f"{stem}_structured.json",
            mime="application/json",
            key="dl_json",
        )


# =====================================================
# HISTORY
# =====================================================

elif page == "History":

    page_head(
        "03", "History",
        "A ledger of",
        '<span class="hl">this session.</span>',
        "Everything you have processed since opening the workspace.",
    )

    history = st.session_state.history

    if history:
        ledger(list(reversed(history)), len(history))
    else:
        render(EMPTY)


# =====================================================
# SETTINGS
# =====================================================

elif page == "Settings":

    page_head(
        "04", "Settings",
        "Under the",
        '<span class="hl">hood.</span>',
        "A quick look at what powers the workspace.",
    )

    flash = st.session_state.pop("flash", None)
    if flash:
        notice("ok", "Done", flash)

    section("→", "Application")

    spec = [
        ("Application", "DocuStruct"),
        ("Version", "1.0.0"),
        ("Framework", "Streamlit"),
        ("Language", "Python"),
        ("Documents this session", len(st.session_state.history)),
    ]
    render(
        '<div class="kv">'
        + "".join(
            f'<div class="kvr" style="animation-delay:{0.06 * i:.2f}s">'
            f'<span class="k">{esc(k)}</span><span class="dots"></span><span class="v">{esc(v)}</span></div>'
            for i, (k, v) in enumerate(spec)
        )
        + "</div>"
    )

    section("→", "Processing modules")

    modules = [
        ("Document extraction", True),
        ("Text cleaning", True),
        ("Advanced information extraction", False),
        ("AI-powered processing", False),
    ]
    render(
        '<div class="kv">'
        + "".join(
            f'<div class="kvr" style="animation-delay:{0.06 * i:.2f}s">'
            f'<span class="k">{esc(name)}</span><span class="dots"></span>'
            f'<span class="chip {"ok" if live else "soon"}">{"Active" if live else "Planned"}</span></div>'
            for i, (name, live) in enumerate(modules)
        )
        + "</div>"
    )

    notice(
        "info", "Roadmap",
        "Advanced information extraction and AI-powered processing will be integrated in upcoming stages.",
    )

    render('<div style="height:8px"></div>')
    st.button("Clear session history", key="clear_hist", on_click=clear_session)


# =====================================================
# FOOTER
# =====================================================

render(
    '<div class="footer">'
    '<span>DocuStruct · a quieter way to work with documents</span>'
    f'<span>Built with Python &amp; Streamlit · {datetime.now().year}</span>'
    '</div>'
)