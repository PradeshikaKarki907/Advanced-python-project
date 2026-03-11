import streamlit as st
import pandas as pd


def _abbreviate(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return f"{n:,}"


def display_kpis(df: pd.DataFrame) -> None:
    metrics = [
        ("🎬", "Total Movies", f"{len(df):,}"),
        ("⭐", "Avg Rating", f"{df['rating'].mean():.2f}"),
        ("📈", "Avg Popularity", f"{df['popularity'].mean():.1f}"),
        ("🗳️", "Total Votes", _abbreviate(int(df["vote_count"].sum()))),
        (
            "🎭",
            "Unique Genres",
            str(len({g for gs in df["genres"].dropna() for g in gs.split("|") if g})),
        ),
    ]

    cols = st.columns(len(metrics))
    for col, (icon, label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-icon">{icon}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
