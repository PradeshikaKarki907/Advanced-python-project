import streamlit as st
import pandas as pd
from typing import Dict, Any


def create_filters(df: pd.DataFrame) -> Dict[str, Any]:
    st.sidebar.markdown('<p class="section-title">Filters</p>', unsafe_allow_html=True)

    min_year = int(df["release_year"].min())
    max_year = int(df["release_year"].max())
    year_range = st.sidebar.slider(
        "Release Year", min_year, max_year, (min_year, max_year)
    )

    all_genres = sorted(
        {g for gs in df["genres"].dropna() for g in gs.split("|") if g}
    )
    selected_genres = st.sidebar.multiselect("Genres", all_genres)

    min_rating = st.sidebar.slider(
        "Minimum Rating",
        float(df["rating"].min()),
        float(df["rating"].max()),
        float(df["rating"].min()),
        0.1,
    )

    rating_categories = st.sidebar.multiselect(
        "Rating Category",
        df["rating_category"].unique().tolist(),
        default=df["rating_category"].unique().tolist(),
    )

    eras = st.sidebar.multiselect(
        "Era",
        sorted(df["era"].unique()),
        default=sorted(df["era"].unique()),
    )

    return {
        "year_range": year_range,
        "genres": selected_genres,
        "min_rating": min_rating,
        "rating_categories": rating_categories,
        "eras": eras,
    }


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    out = df.copy()
    out = out[
        out["release_year"].between(filters["year_range"][0], filters["year_range"][1])
    ]
    if filters["genres"]:
        out = out[
            out["genres"].apply(
                lambda x: any(g in str(x) for g in filters["genres"])
            )
        ]
    out = out[out["rating"] >= filters["min_rating"]]
    out = out[out["rating_category"].isin(filters["rating_categories"])]
    out = out[out["era"].isin(filters["eras"])]
    return out
