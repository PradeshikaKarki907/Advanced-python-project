import pandas as pd
import streamlit as st

from components.styles import TMDB_IMG


def display_browse_movies(browse_df: pd.DataFrame | None) -> None:
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

    # ── Cards grid ────────────────────────────────────────────────────
    cols = st.columns(3)
    for i, (_, row) in enumerate(page.iterrows()):
        with cols[i % 3]:
            poster = row.get("poster_path", "")
            poster_url = (
                f"{TMDB_IMG}{poster}"
                if pd.notna(poster) and poster
                else "https://via.placeholder.com/300x450/161B22/E50914?text=No+Poster"
            )
            genres_html = "".join(
                f'<span class="badge">{g}</span>' for g in row["genre_list"][:3]
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

            overview = str(row.get("overview", ""))[:200]

            st.markdown(
                f"""
                <div class="movie-card">
                  <img src="{poster_url}" alt="{row['title']}"
                       onerror="this.src='https://via.placeholder.com/300x450/161B22/E50914?text=No+Poster'"/>
                  <div class="movie-card-body">
                    <p class="movie-card-title">{row['title']}</p>
                    <div class="movie-card-genre">{date_str}</div>
                    <span class="star">{stars}</span>
                    <small style="color:#8B949E"> {vote_avg:.1f} ({vote_cnt:,} votes)</small>
                    {genres_html}
                    <p class="movie-card-overview">{overview}</p>
                  </div>
                </div>
                <br/>
                """,
                unsafe_allow_html=True,
            )

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
