"""
Gaby AI Data Companion - Simplified
A lightweight Streamlit app for file upload, preview, tagging, and AI assistant view.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Gaby Data Cleaning Agent", page_icon="🤖", layout="wide")
st.title("💬 Gaby AI: Your Data Team's Companion")

# ---------------- HELPERS ----------------
def get_sample_files():
    path = Path(__file__).parent / "data" / "input"
    return [f.name for f in path.glob("*.csv")] if path.exists() else []

def load_data(file, uploaded=False):
    try:
        return pd.read_csv(file) if uploaded else pd.read_csv(str(file)), None
    except Exception as e:
        return None, str(e)

def describe_dataframe(df: pd.DataFrame):
    pass
# ---------------- STATE ----------------
if "df" not in st.session_state:
    st.session_state.df = None
if "tags" not in st.session_state:
    st.session_state.tags = ""

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([1, 3])

# ---- Left: Controls ----
with col1:
    st.subheader("⚙️ Controls")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    sample = st.selectbox("Or choose a sample:", ["None"] + get_sample_files())
    st.session_state.tags = st.text_input("Tags (comma separated)", st.session_state.tags)

    if st.button("🚀 Analyze", type="primary"):
        if uploaded_file:
            df, err = load_data(uploaded_file, uploaded=True)
        elif sample != "None":
            df, err = load_data(Path(__file__).parent / "data" / "input" / sample)
        else:
            df, err = None, "No file selected"

        if df is not None:
            st.session_state.df = df
        else:
            st.error(f"Error: {err}")

    if st.button("🔄 Reset"):
        st.session_state.df = None
        st.session_state.tags = ""

# ---- Right: Gaby Window ----
with col2:
    st.subheader("🧠 Gaby's Window")
    if st.session_state.df is not None:
        df = st.session_state.df
        st.success(f"Loaded {df.shape[0]} rows × {df.shape[1]} columns")

        st.markdown("### 📋 Column Summary")
        st.dataframe(describe_dataframe(df), width='stretch')

        st.markdown("### 🤖 Gaby's Analysis")
        st.write(f"Based on your tags: {st.session_state.tags}")
        st.write("- Handle missing values")
        st.write("- Remove duplicates")
        st.write("- Standardize formats")
    else:
        st.info("👋 Upload or select a dataset to begin.")