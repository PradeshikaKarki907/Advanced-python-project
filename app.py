import streamlit as st
from datetime import datetime

from components.styles import inject_css
from components.data import load_data, load_scraped_data
from components.filters import create_filters, apply_filters
from components.kpis import display_kpis
from components import charts
from components.browse import display_browse_movies
from components.insights import display_insights_tab

# ── Page config (must be the very first Streamlit call) ──────────────────
st.set_page_config(
    page_title="Movie Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

inject_css()


# ── Page: Dashboard ──────────────────────────────────────────────────────

def _render_dashboard() -> None:
    with st.spinner("Loading data..."):
        df = load_data()

    if df is None or df.empty:
        st.error(
            "No movie data found. Run the pipeline first or place a CSV in "
            "the `extracted_data/` folder."
        )
        return

    st.sidebar.markdown("---")
    filters = create_filters(df)
    filtered = apply_filters(df, filters)

    st.sidebar.markdown("---")
    st.sidebar.info(f"Showing **{len(filtered):,}** of **{len(df):,}** movies")

    if filtered.empty:
        st.warning("No movies match the selected filters. Adjust your criteria.")
        return

    display_kpis(filtered)
    st.markdown("---")

    tab_overview, tab_trends, tab_genres, tab_top, tab_rels, tab_insights = st.tabs(
        ["Overview", "Trends", "Genres", "Top Movies", "Relationships", "Insights"]
    )

    # ── Overview ─────────────────────────────────────────────────────
    with tab_overview:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.rating_distribution(filtered), width="stretch")
        with c2:
            st.plotly_chart(charts.vote_count_distribution(filtered), width="stretch")

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(charts.era_distribution(filtered), width="stretch")
        with c4:
            st.plotly_chart(charts.popularity_bucket_chart(filtered), width="stretch")

    # ── Trends ───────────────────────────────────────────────────────
    with tab_trends:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.movies_per_year(filtered), width="stretch")
        with c2:
            st.plotly_chart(charts.age_vs_rating(filtered), width="stretch")

        st.plotly_chart(charts.rating_trend(filtered), width="stretch")

    # ── Genres ───────────────────────────────────────────────────────
    with tab_genres:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.genre_distribution(filtered), width="stretch")
        with c2:
            st.plotly_chart(charts.genres_by_rating(filtered), width="stretch")

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(charts.rating_category_chart(filtered), width="stretch")
        with c4:
            st.plotly_chart(charts.popularity_bucket_bar(filtered), width="stretch")

    # ── Top Movies ───────────────────────────────────────────────────
    with tab_top:
        _render_top_movies(filtered)

    # ── Relationships ────────────────────────────────────────────────
    with tab_rels:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.popularity_vs_rating(filtered), width="stretch")
        with c2:
            st.plotly_chart(charts.correlation_heatmap(filtered), width="stretch")

        st.markdown(
            '<p class="section-title">Statistical Summary</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            filtered[["rating", "popularity", "vote_count", "movie_age"]]
            .describe()
            .T.style.format("{:.2f}"),
            width="stretch",
        )

    # ── Insights ─────────────────────────────────────────────────────
    with tab_insights:
        display_insights_tab(filtered)

    # Footer
    st.markdown("---")
    st.markdown(
        f'<div class="dash-footer">'
        f"Updated {datetime.now():%Y-%m-%d %H:%M:%S} · {len(df):,} movies in dataset"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_top_movies(df) -> None:
    st.markdown(
        '<p class="section-title">Top Movies by Weighted Score</p>',
        unsafe_allow_html=True,
    )
    top = df.nlargest(20, "weighted_score")[
        ["title", "release_year", "genres", "rating", "popularity", "weighted_score"]
    ].copy()
    top["weighted_score"] = top["weighted_score"].round(2)
    top["rating"] = top["rating"].round(1)
    top["popularity"] = top["popularity"].round(1)
    top.insert(0, "Rank", range(1, len(top) + 1))

    st.dataframe(
        top,
        hide_index=True,
        width="stretch",
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "title": st.column_config.TextColumn("Title", width="large"),
            "release_year": st.column_config.NumberColumn("Year", width="small"),
            "genres": st.column_config.TextColumn("Genres", width="medium"),
            "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
            "popularity": st.column_config.NumberColumn("Popularity", format="%.1f"),
            "weighted_score": st.column_config.NumberColumn("Score", format="%.2f"),
        },
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<p class="section-title">Highest Rated</p>', unsafe_allow_html=True
        )
        st.dataframe(
            df.nlargest(10, "rating")[["title", "rating", "release_year"]],
            hide_index=True,
            width="stretch",
        )
    with c2:
        st.markdown(
            '<p class="section-title">Most Popular</p>', unsafe_allow_html=True
        )
        st.dataframe(
            df.nlargest(10, "popularity")[["title", "popularity", "release_year"]],
            hide_index=True,
            width="stretch",
        )


# ── Main entry ───────────────────────────────────────────────────────────

def main():
    st.markdown(
        '<div class="main-header">🎬 Movie Analytics Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<p style="font-size:1.3rem;font-weight:700;letter-spacing:0.3px;">'
        '🎬 Movie Analytics</p>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "🎥 Browse Movies"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")

    if page == "🎥 Browse Movies":
        browse_df = load_scraped_data()
        if browse_df is not None:
            st.sidebar.info(f"Scraped dataset: **{len(browse_df)} movies**")
        display_browse_movies(browse_df)
    else:
        _render_dashboard()


if __name__ == "__main__":
    main()
