from datetime import datetime
from io import StringIO

import numpy as np
import pandas as pd
import streamlit as st


def generate_insights_report(df: pd.DataFrame) -> str:
    out = StringIO()
    w = out.write

    w("=" * 80 + "\n")
    w("MOVIE ANALYTICS INSIGHTS REPORT\n")
    w("=" * 80 + "\n")
    w(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    w(f"Total Records: {len(df)}\n\n")

    # Dataset overview
    w("\n  DATASET OVERVIEW\n")
    w("-" * 80 + "\n")
    w(f"  Total Movies: {len(df)}\n")
    w(f"  Date Range: {df['release_year'].min():.0f} - {df['release_year'].max():.0f}\n")
    w(f"  Features Analyzed: {len(df.columns)}\n")

    # Rating insights
    w("\n  RATING INSIGHTS\n")
    w("-" * 80 + "\n")
    w(f"  Average Rating: {df['rating'].mean():.2f}/10\n")
    w(f"  Median Rating: {df['rating'].median():.2f}/10\n")
    w(f"  Std Dev: {df['rating'].std():.2f}\n")
    w(f"  Rating Range: {df['rating'].min():.1f} - {df['rating'].max():.1f}\n\n")

    excellent = (df["rating"] >= 8.0).sum()
    good = ((df["rating"] >= 7.0) & (df["rating"] < 8.0)).sum()
    avg = ((df["rating"] >= 6.0) & (df["rating"] < 7.0)).sum()
    poor = (df["rating"] < 6.0).sum()

    w("  Rating Distribution:\n")
    w(f"    Excellent (8.0+): {excellent} ({excellent/len(df)*100:.1f}%)\n")
    w(f"    Good (7.0-7.9): {good} ({good/len(df)*100:.1f}%)\n")
    w(f"    Average (6.0-6.9): {avg} ({avg/len(df)*100:.1f}%)\n")
    w(f"    Below Average (<6.0): {poor} ({poor/len(df)*100:.1f}%)\n")

    # Genre insights
    w("\n  GENRE INSIGHTS\n")
    w("-" * 80 + "\n")
    genre_counts: dict[str, int] = {}
    genre_ratings: dict[str, list] = {}
    for _, row in df.iterrows():
        if pd.notna(row["genres"]):
            for g in str(row["genres"]).split("|"):
                if g:
                    genre_counts[g] = genre_counts.get(g, 0) + 1
                    genre_ratings.setdefault(g, []).append(row["rating"])

    w(f"  Total Unique Genres: {len(genre_counts)}\n")
    w(f"  Genres: {', '.join(sorted(genre_counts))}\n\n")

    w("  Most Common Genres:\n")
    for g, c in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        w(f"    {g}: {c} movies ({c/len(df)*100:.1f}%)\n")

    w("\n  Top 5 Highest-Rated Genres (by average):\n")
    for g in sorted(genre_ratings, key=lambda x: np.mean(genre_ratings[x]), reverse=True)[:5]:
        a = np.mean(genre_ratings[g])
        w(f"    {g}: {a:.2f}/10 ({len(genre_ratings[g])} movies)\n")

    # Popularity insights
    w("\n  POPULARITY INSIGHTS\n")
    w("-" * 80 + "\n")
    w(f"  Average Popularity: {df['popularity'].mean():.2f}\n")
    w(f"  Median Popularity: {df['popularity'].median():.2f}\n\n")

    w("  Top 5 Highest-Rated Movies:\n")
    for i, (_, m) in enumerate(df.nlargest(5, "rating").iterrows(), 1):
        w(f"    {i}. {m['title']} ({int(m['release_year'])})\n")
        w(f"       Rating: {m['rating']:.1f}/10 | Popularity: {m['popularity']:.1f}\n")

    # Release year patterns
    w("\n  RELEASE YEAR PATTERNS\n")
    w("-" * 80 + "\n")
    tmp = df.copy()
    tmp["decade"] = (tmp["release_year"] // 10 * 10).astype(int)
    w("  Movies per Decade:\n")
    for dec, cnt in tmp["decade"].value_counts().sort_index().items():
        w(f"    {int(dec)}s: {cnt} movies ({cnt/len(df)*100:.1f}%)\n")

    w("\n  Average Rating by Decade:\n")
    for dec, a in tmp.groupby("decade")["rating"].mean().sort_index().items():
        w(f"    {int(dec)}s: {a:.2f}/10\n")

    # Key findings
    w("\n  KEY FINDINGS & RECOMMENDATIONS\n")
    w("-" * 80 + "\n")
    w(f"  1. Movies around {df.loc[df['rating'].idxmax(), 'release_year']:.0f} have highest quality\n")
    w(f"  2. Genre '{max(genre_counts, key=genre_counts.get)}' is most represented\n")
    w(f"  3. {good/len(df)*100:.0f}% of movies meet 'Good' quality threshold (7.0+)\n")
    w(f"  4. Multi-genre movies average {df[df['genre_count'] > 1]['rating'].mean():.2f}/10\n")

    # Outlier analysis
    _write_outliers(w, df)

    w("\n" + "=" * 80 + "\n")
    return out.getvalue()


def _write_outliers(w, df: pd.DataFrame) -> None:
    w("\n  OUTLIER ANALYSIS\n")
    w("-" * 80 + "\n")

    # Rating
    q1, q3 = df["rating"].quantile(0.25), df["rating"].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    low_out = df[df["rating"] < lo]
    high_out = df[df["rating"] > hi]

    w(f"\n  Rating Outliers (IQR: {q1:.2f} – {q3:.2f}, bounds: {lo:.2f} – {hi:.2f}):\n")
    if len(low_out):
        w(f"    ▼ {len(low_out)} unusually LOW-rated movies (< {lo:.2f}):\n")
        for _, r in low_out.nsmallest(5, "rating").iterrows():
            w(f"      • {r['title']} ({int(r['release_year'])}) — {r['rating']:.1f}/10\n")
        w("    → These films score well below the typical range.\n")
    else:
        w("    No low-rating outliers detected.\n")

    if len(high_out):
        w(f"    ▲ {len(high_out)} unusually HIGH-rated movies (> {hi:.2f}):\n")
        for _, r in high_out.nlargest(5, "rating").iterrows():
            w(f"      • {r['title']} ({int(r['release_year'])}) — {r['rating']:.1f}/10\n")
        w("    → Critically acclaimed films that significantly exceed the norm.\n")
    else:
        w("    No high-rating outliers detected.\n")

    # Popularity
    q1p, q3p = df["popularity"].quantile(0.25), df["popularity"].quantile(0.75)
    hi_p = q3p + 1.5 * (q3p - q1p)
    pop_out = df[df["popularity"] > hi_p]
    w(f"\n  Popularity Outliers (> {hi_p:.1f}):\n")
    if len(pop_out):
        w(f"    ▲ {len(pop_out)} movies with unusually high popularity:\n")
        for _, r in pop_out.nlargest(5, "popularity").iterrows():
            w(f"      • {r['title']} ({int(r['release_year'])}) — pop {r['popularity']:.1f}, rating {r['rating']:.1f}\n")
        w("    → Often recent blockbusters or viral franchise entries.\n")
    else:
        w("    No popularity outliers detected.\n")

    # Vote count
    q1v, q3v = df["vote_count"].quantile(0.25), df["vote_count"].quantile(0.75)
    hi_v = q3v + 1.5 * (q3v - q1v)
    vote_out = df[df["vote_count"] > hi_v]
    w(f"\n  Vote Count Outliers (> {hi_v:.0f} votes):\n")
    if len(vote_out):
        w(f"    ▲ {len(vote_out)} movies with very high engagement:\n")
        for _, r in vote_out.nlargest(5, "vote_count").iterrows():
            w(f"      • {r['title']} ({int(r['release_year'])}) — {int(r['vote_count']):,} votes\n")
        w("    → Films with enduring cultural presence.\n")
    else:
        w("    No vote-count outliers detected.\n")

    # Age-popularity anomalies
    if "movie_age" in df.columns:
        old_pop = df[(df["movie_age"] > 20) & (df["popularity"] > hi_p)]
        if len(old_pop):
            w(f"\n  Age-Popularity Anomalies ({len(old_pop)} movies 20+ yrs old with outlier popularity):\n")
            for _, r in old_pop.nlargest(5, "popularity").iterrows():
                w(f"      • {r['title']} ({int(r['release_year'])}) — age {int(r['movie_age'])}y, pop {r['popularity']:.1f}\n")
            w("    → Enduring classics or films boosted by remakes/streaming.\n")


def display_insights_tab(df: pd.DataFrame) -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            '<p class="section-title">Analytics Insights Report</p>',
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Generate Report"):
            st.session_state.report_generated = True

    if st.session_state.get("report_generated", False):
        report_text = generate_insights_report(df)
        st.markdown("---")
        st.text(report_text)
        st.markdown("---")
        _, dl, _ = st.columns(3)
        with dl:
            st.download_button(
                "Download Report (.txt)",
                data=report_text,
                file_name=f"movie_insights_{datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain",
            )
