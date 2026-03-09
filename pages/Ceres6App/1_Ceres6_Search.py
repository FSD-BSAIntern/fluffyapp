# Project Title:        Ceres6 Cheat Sheet Search Tool
# Description:          A scipt to power a Streamlit web app for searching various reports in Ceres6.
# Author:               Isaiah De La Rosa
# Project Manager:      Kristin Cruz
# Date Created:         January 21, 2026
# Last Modified:        January 26, 2026

import re
from pathlib import Path
import pandas as pd
import streamlit as st


# ---------- Config ----------
STOPWORDS = {
    "where","can","i","find","the","a","an","of","to","for","in","on","and","or",
    "is","are","do","does","what","whats","please","me","show","tell"
}

ENTITY_HINTS = {
    "agency": {"agency", "agencies"},
    "donors": {"donor", "donors"},
    "vendors": {"vendor", "vendors", "supplier", "suppliers"},
    "items": {"item", "items", "product", "sku"},
    "ledger": {"gl", "g/l", "ledger", "general ledger", "journal"}
}

COL_COMMON = "Common"
COL_KEYWORD = "Keyword / Search Term"
COL_REPORT = "Database/Report Location"
COL_FULLKEY = "Full Information Key"
COL_ENTITY = "Entity Type"
COL_CANON = "Canonical Field"
COL_SYNONYMS = "Synonyms / Ask Phrases"

# ---------- Text utilities ----------
def normalize(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s,/-]", " ", text)
    text = text.replace("/", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> set[str]:
    t = normalize(text)
    return {w for w in t.split() if len(w) >= 3 and w not in STOPWORDS}

def phrase_list(synonyms: str) -> list[str]:
    parts = [(synonyms or "").split(",")]
    # flatten
    raw = []
    for chunk in parts:
        raw.extend(chunk)
    cleaned = [normalize(p) for p in raw]
    return [p for p in cleaned if len(p) >= 3]

# ---------- Scoring ----------
def score_row(q_norm: str, q_tokens: set[str], row: pd.Series) -> tuple[int, dict]:
    common = normalize(str(row.get(COL_COMMON, "")))
    keyword = normalize(str(row.get(COL_KEYWORD, "")))
    report = normalize(str(row.get(COL_REPORT, "")))
    synonyms = str(row.get(COL_SYNONYMS, ""))
    entity = normalize(str(row.get(COL_ENTITY, "")))

    score = 0
    why = {"syn_phrase_hit": 0, "token_overlap": 0, "entity_bonus": 0}

    # 1) Phrase hits in synonyms (strong)
    best_phrase = 0
    for phr in phrase_list(synonyms):
        if phr and phr in q_norm:
            best_phrase = max(best_phrase, 8 + (len(phr) // 10))
    score += best_phrase
    why["syn_phrase_hit"] = best_phrase

    # 2) Token overlap with common/keyword/report (medium)
    row_tokens = tokenize(common) | tokenize(keyword) | tokenize(report)
    overlap = len(q_tokens & row_tokens)
    tok_pts = min(6, overlap * 2)
    score += tok_pts
    why["token_overlap"] = tok_pts

    # 3) Entity hint bonus
    for ent, words in ENTITY_HINTS.items():
        if any(w in q_norm for w in words):
            if ent == entity:
                score += 4
                why["entity_bonus"] = 4
            else:
                score -= 1
            break

    return score, why

# ---------- Streamlit UI ----------
st.title("Ceres6 Report / Field Finder")
st.write('Ask Something Like: "Where can I find agency delivery zone codes?"')

APP_DIR = Path(__file__).resolve().parent
CSV_PATH = APP_DIR / "Ceres6 Cheatsheet.csv"

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

df = load_data(CSV_PATH)

# Validate columns
required_cols = [COL_COMMON, COL_KEYWORD, COL_REPORT, COL_FULLKEY, COL_ENTITY, COL_CANON, COL_SYNONYMS]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.stop()

q = st.text_input("Your question")
top_k = st.slider("Results to show", 1, 10, 3)

if q:
    q_norm = normalize(q)
    q_tokens = tokenize(q)

    scored = []
    for _, row in df.iterrows():
        s, why = score_row(q_norm, q_tokens, row)
        scored.append((s, why, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[:top_k]

    st.subheader("Top Matches")
    for rank, (s, why, row) in enumerate(best, start=1):
        st.markdown(
            f"**{rank}. {row[COL_COMMON]}**  \n"
            f"- Table: `{row[COL_REPORT]}`  \n"
            f"- Column: `{row[COL_KEYWORD]}`  \n"
            f"- Key: `{row[COL_FULLKEY]}`  \n"
        )

    st.subheader("Best Answer")
    best_row = best[0][2]
    st.code(
        f"{best_row[COL_COMMON]} | {best_row[COL_REPORT]}"
    )

