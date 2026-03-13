import os
from datetime import datetime

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(__file__))
    candidates = [
        os.path.join(base, "processed_movies.csv"),
        os.path.join(base, "data", "processed", "processed_movies.csv"),
        os.path.join(base, "extracted_data", "real_movie_data.csv"),
    ]

    df = None
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except Exception:
                continue

    if df is None:
        return None

    _add_derived_columns(df)
    return df


@st.cache_data
def load_scraped_data():
    base = os.path.dirname(os.path.dirname(__file__))
    candidates = [
        os.path.join(base, "extracted_data", "real_movie_data.csv"),
        os.path.join(base, "extracted_data", "tmdb_movies.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["genre_list"] = (
                df["genres"].fillna("").apply(
                    lambda x: [g.strip() for g in str(x).split("|") if g.strip()]
                )
                if "genres" in df.columns
                else [[] for _ in range(len(df))]
            )
            for col, default in [
                ("poster_path", ""), ("backdrop_path", ""),
                ("release_date", ""), ("overview", ""),
                ("rating", 0.0), ("vote_count", 0), ("popularity", 0.0),
            ]:
                if col not in df.columns:
                    df[col] = default
            df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
            return df
    return None


# ── helpers ──────────────────────────────────────────────────────────────

def _add_derived_columns(df: pd.DataFrame) -> None:
    if "release_year" not in df.columns and "release_date" in df.columns:
        df["release_year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year

    if "release_year" in df.columns:
        df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce").fillna(0).astype(int)
        df["movie_age"] = datetime.now().year - df["release_year"]
        df["era"] = df["release_year"].map(_era_label)

    if "rating" in df.columns:
        df["rating_category"] = df["rating"].map(_rating_category)

    if "genres" in df.columns:
        df["genre_count"] = df["genres"].fillna("").apply(
            lambda g: len([x for x in g.split("|") if x])
        )

    if "weighted_score" not in df.columns:
        r = df.get("rating", pd.Series(dtype=float))
        v = df.get("vote_count", pd.Series(dtype=float))
        p = df.get("popularity", pd.Series(dtype=float))
        if not r.empty:
            r_norm = r / 10
            v_norm = v / v.max() if v.max() > 0 else v * 0
            p_norm = p / p.max() if p.max() > 0 else p * 0
            df["weighted_score"] = (r_norm * 0.5 + v_norm * 0.3 + p_norm * 0.2) * 10
        else:
            df["weighted_score"] = 0


def _era_label(y: int) -> str:
    if y >= 2020: return "2020s"
    if y >= 2010: return "2010s"
    if y >= 2000: return "2000s"
    if y >= 1990: return "1990s"
    if y >= 1980: return "1980s"
    return "Pre-1980"


def _rating_category(r: float) -> str:
    if r >= 8: return "Excellent"
    if r >= 6: return "Good"
    if r >= 4: return "Average"
    return "Poor"
