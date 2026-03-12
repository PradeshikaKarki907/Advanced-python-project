import html
import urllib.parse

import pandas as pd
import streamlit as st

from components.styles import TMDB_IMG
from recommendation.engine import (
    CollaborativeRecommender,
    HybridRecommender,
    MovieRecommender,
)

TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"
_PLACEHOLDER = "https://via.placeholder.com/300x450/161B22/E50914?text=No+Poster"


@st.cache_resource(show_spinner="Building content-based model …")
def _get_recommender() -> MovieRecommender:
    return MovieRecommender().build()


@st.cache_resource(show_spinner="Building collaborative model …")
def _get_collaborative() -> CollaborativeRecommender:
    return CollaborativeRecommender().build()


@st.cache_resource(show_spinner="Building hybrid model …")
def _get_hybrid() -> HybridRecommender:
    return HybridRecommender(
        content=_get_recommender(),
        collaborative=_get_collaborative(),
    )


def display_browse_movies(browse_df: pd.DataFrame | None) -> None:
    # ── If a card was clicked, show its detail page instead ───────
    expanded_title = st.query_params.get("expanded")
    if expanded_title and browse_df is not None:
        _render_movie_detail(expanded_title, browse_df)
        return

    st.markdown('<p class="section-title">Browse Movies</p>', unsafe_allow_html=True)

    if browse_df is None or browse_df.empty:
        st.warning(
            "No scraped movie data found. Run the scraper first:\n\n"
            "```python\nfrom extraction.scraper import MovieDataScraper\n"
            "s = MovieDataScraper()\n"
            "df = s.scrape_real_data(source='tmdb', num_movies=100)\n"
            "s.save_scraped_data(df, 'real_movie_data.csv')\n```"
        )
        return

    # ── Filters ───────────────────────────────────────────────────────
    all_genres = sorted({g for gl in browse_df["genre_list"] for g in gl})
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        search = st.text_input("Search by title", placeholder="e.g. Avatar...")
    with fc2:
        sel_genres = st.multiselect("Filter by genre", all_genres)
    with fc3:
        sort_by = st.selectbox(
            "Sort by",
            ["Popularity ↓", "Rating ↓", "Votes ↓", "Release Date ↓"],
        )

    filtered = browse_df.copy()
    if search:
        filtered = filtered[filtered["title"].str.contains(search, case=False, na=False)]
    if sel_genres:
        filtered = filtered[
            filtered["genre_list"].apply(lambda g: any(x in g for x in sel_genres))
        ]

    sort_map = {
        "Popularity ↓": ("popularity", False),
        "Rating ↓": ("rating", False),
        "Votes ↓": ("vote_count", False),
        "Release Date ↓": ("release_date", False),
    }
    col_s, asc_s = sort_map[sort_by]
    filtered = filtered.sort_values(col_s, ascending=asc_s)

    # ── Pagination ────────────────────────────────────────────────────
    PER_PAGE = 12
    total_pages = max(1, -(-len(filtered) // PER_PAGE))

    if "browse_page" not in st.session_state:
        st.session_state.browse_page = 1
    st.session_state.browse_page = max(1, min(st.session_state.browse_page, total_pages))

    start = (st.session_state.browse_page - 1) * PER_PAGE
    end = start + PER_PAGE
    page = filtered.iloc[start:end]

    st.caption(f"Showing **{len(filtered)}** movies")
    st.markdown("---")

    # ── Clickable cards grid ──────────────────────────────────────────
    cols = st.columns(3)
    for i, (_, row) in enumerate(page.iterrows()):
        with cols[i % 3]:
            _render_clickable_card(row)

    # ── Pagination controls ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _, p_prev, p_info, p_next, _ = st.columns([2, 1, 1, 1, 2])
    with p_prev:
        if st.button("◀ Prev", disabled=st.session_state.browse_page <= 1):
            st.session_state.browse_page -= 1
            st.rerun()
    with p_info:
        st.markdown(
            f"<div style='text-align:center;padding:8px;color:#E50914;"
            f"font-weight:600;letter-spacing:2px;'>"
            f"{st.session_state.browse_page} / {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with p_next:
        if st.button("Next ▶", disabled=st.session_state.browse_page >= total_pages):
            st.session_state.browse_page += 1
            st.rerun()

    st.caption(f"Showing {start + 1}–{min(end, len(filtered))} of {len(filtered)} movies")


# ── Clickable card ────────────────────────────────────────────────────────

def _render_clickable_card(row: pd.Series) -> None:
    """Render a movie card wrapped in a clickable <a> tag."""
    poster = row.get("poster_path", "")
    poster_url = (
        f"{TMDB_IMG}{poster}"
        if pd.notna(poster) and poster
        else _PLACEHOLDER
    )
    genres_html = "".join(
        f'<span class="badge">{html.escape(g)}</span>' for g in row["genre_list"][:3]
    )
    vote_avg = float(row.get("rating", 0) or 0)
    stars = "★" * int(round(vote_avg / 2)) + "☆" * (5 - int(round(vote_avg / 2)))
    vote_cnt = int(row.get("vote_count", 0) or 0)

    date_str = ""
    if pd.notna(row.get("release_date")):
        try:
            date_str = row["release_date"].strftime("%Y-%m-%d")
        except Exception:
            date_str = str(row.get("release_year", ""))

    overview_text = html.escape(str(row.get("overview", ""))[:200])
    title_safe = html.escape(str(row["title"]))
    title_encoded = urllib.parse.quote(str(row["title"]))

    st.markdown(
        f"""
        <a href="?expanded={title_encoded}" target="_self" class="movie-card-link">
          <div class="movie-card">
            <img src="{poster_url}" alt="{title_safe}"
                 onerror="this.src='{_PLACEHOLDER}'"/>
            <div class="movie-card-body">
              <p class="movie-card-title">{title_safe}</p>
              <div class="movie-card-genre">{date_str}</div>
              <span class="star">{stars}</span>
              <small style="color:#8B949E"> {vote_avg:.1f} ({vote_cnt:,} votes)</small>
              {genres_html}
              <p class="movie-card-overview">{overview_text}</p>
            </div>
          </div>
        </a>
        <br/>
        """,
        unsafe_allow_html=True,
    )


# ── Detail view (shown when a card is clicked) ───────────────────────────

def _render_movie_detail(title: str, browse_df: pd.DataFrame) -> None:
    """Full-page detail view for a movie with similar recommendations."""
    if st.button("← Back to Browse"):
        if "expanded" in st.query_params:
            del st.query_params["expanded"]
        st.rerun()

    matches = browse_df[browse_df["title"] == title]
    if matches.empty:
        st.warning(f"Movie not found in the dataset.")
        return

    row = matches.iloc[0]
    title_safe = html.escape(str(row["title"]))

    st.markdown(
        f'<p class="section-title">🎬 {title_safe}</p>',
        unsafe_allow_html=True,
    )

    # ── Movie info layout ─────────────────────────────────────────
    col_poster, col_info = st.columns([1, 3])
    with col_poster:
        poster = row.get("poster_path", "")
        if pd.notna(poster) and poster:
            st.image(f"{TMDB_IMG}{poster}", width="stretch")
        else:
            st.image(_PLACEHOLDER, width="stretch")

    with col_info:
        vote_avg = float(row.get("rating", 0) or 0)
        stars = "★" * int(round(vote_avg / 2)) + "☆" * (5 - int(round(vote_avg / 2)))
        vote_cnt = int(row.get("vote_count", 0) or 0)
        pop = float(row.get("popularity", 0) or 0)

        date_str = ""
        if pd.notna(row.get("release_date")):
            try:
                date_str = row["release_date"].strftime("%Y-%m-%d")
            except Exception:
                date_str = str(row.get("release_year", ""))

        st.markdown(f"**Release Date:** {date_str}")
        st.markdown(f"**Rating:** {stars} {vote_avg:.1f}/10  ({vote_cnt:,} votes)")
        st.markdown(f"**Popularity:** {pop:,.1f}")

        genres = row.get("genre_list", [])
        if genres:
            genre_badges = " ".join(
                f'<span class="badge">{html.escape(g)}</span>' for g in genres
            )
            st.markdown(f"**Genres:** {genre_badges}", unsafe_allow_html=True)

        overview = str(row.get("overview", ""))
        if overview:
            st.markdown(f"**Overview:** {overview}")

    # ── Similar movies (content-based) ──────────────────────────
    st.markdown("---")
    st.markdown(
        '<p class="section-title">🎬 Similar Movies</p>',
        unsafe_allow_html=True,
    )

    recommender = _get_recommender()

    # Initial 5 similar movies
    see_more_key = f"see_more_{title}"
    if see_more_key not in st.session_state:
        st.session_state[see_more_key] = False

    top_k = 10 if st.session_state[see_more_key] else 5
    results = recommender.recommend(title, top_k=top_k)

    if not results:
        st.caption("No similar movies found for this title.")
    else:
        _render_rec_row(results)
        if not st.session_state[see_more_key] and len(results) >= 5:
            if st.button("See More ▸", key=f"btn_{see_more_key}"):
                st.session_state[see_more_key] = True
                st.rerun()

    # ── For You (hybrid: content + collaborative) ─────────────────
    st.markdown("---")
    st.markdown(
        '<p class="section-title">🍿 For You</p>',
        unsafe_allow_html=True,
    )

    hybrid = _get_hybrid()

    see_more_hybrid_key = f"see_more_hybrid_{title}"
    if see_more_hybrid_key not in st.session_state:
        st.session_state[see_more_hybrid_key] = False

    hybrid_k = 10 if st.session_state[see_more_hybrid_key] else 5
    hybrid_results = hybrid.recommend(title, top_k=hybrid_k)

    if not hybrid_results:
        st.caption("No personalised recommendations available.")
    else:
        _render_rec_row(hybrid_results)
        if not st.session_state[see_more_hybrid_key] and len(hybrid_results) >= 5:
            if st.button("See More ▸", key=f"btn_{see_more_hybrid_key}"):
                st.session_state[see_more_hybrid_key] = True
                st.rerun()


def _render_rec_row(results: list) -> None:
    """Render a horizontal row of recommended movie cards."""
    rec_cols = st.columns(min(len(results), 5))
    for j, rec in enumerate(results):
        with rec_cols[j % len(rec_cols)]:
            rec_poster = rec.get("poster_path", "")
            rec_poster_url = (
                f"{TMDB_IMG_BASE}{rec_poster}"
                if rec_poster and isinstance(rec_poster, str) and rec_poster.startswith("/")
                else "https://via.placeholder.com/500x750?text=No+Poster"
            )
            rec_title_safe = html.escape(rec["title"])
            rec_title_encoded = urllib.parse.quote(rec["title"])
            score_pct = int(rec["score"] * 100)

            st.markdown(
                f"""
                <a href="?expanded={rec_title_encoded}" target="_self"
                   class="movie-card-link">
                  <div style="cursor:pointer;text-align:center;">
                    <img src="{rec_poster_url}"
                         style="width:100%;border-radius:8px;"
                         onerror="this.src='https://via.placeholder.com/500x750?text=No+Poster'"/>
                    <p style="color:#FAFAFA;font-weight:600;margin:8px 0 2px;
                              font-size:0.9rem;">{rec_title_safe}</p>
                    <p style="color:#8B949E;font-size:0.8rem;margin:0;">
                      ⭐ {rec['rating']}  ·  {rec.get('release_year', '?')}
                    </p>
                    <div style="background:#21262D;border-radius:4px;
                                height:6px;margin:6px 0 2px;">
                      <div style="background:#E50914;border-radius:4px;
                                  height:6px;width:{score_pct}%;"></div>
                    </div>
                    <small style="color:#8B949E;">{score_pct}% match</small>
                  </div>
                </a>
                """,
                unsafe_allow_html=True,
            )
