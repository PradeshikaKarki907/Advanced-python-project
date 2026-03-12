"""Streamlit UI component for the Movie Recommender tab."""

import streamlit as st

from recommendation.engine import (
    CollaborativeRecommender,
    HybridRecommender,
    MovieRecommender,
)

TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"


@st.cache_resource(show_spinner="Building content-based model …")
def _get_content_recommender() -> MovieRecommender:
    return MovieRecommender().build()


@st.cache_resource(show_spinner="Building collaborative model …")
def _get_collaborative_recommender() -> CollaborativeRecommender:
    return CollaborativeRecommender().build()


@st.cache_resource(show_spinner="Building hybrid model …")
def _get_hybrid_recommender() -> HybridRecommender:
    return HybridRecommender(
        content=_get_content_recommender(),
        collaborative=_get_collaborative_recommender(),
    )


def _render_movie_cards(results: list) -> None:
    """Display a row of movie poster cards."""
    cols = st.columns(min(len(results), 5))
    for i, rec in enumerate(results):
        with cols[i % len(cols)]:
            poster = rec.get("poster_path", "")
            if poster and isinstance(poster, str) and poster.startswith("/"):
                st.image(f"{TMDB_IMG_BASE}{poster}", width="stretch")
            else:
                st.image(
                    "https://via.placeholder.com/500x750?text=No+Poster",
                    width="stretch",
                )
            st.markdown(f"**{rec['title']}**")
            st.caption(
                f"⭐ {rec['rating']}  ·  {rec.get('release_year', '?')}  \n"
                f"{rec.get('genres', '')}"
            )
            st.progress(rec["score"], text=f"Score: {rec['score']:.0%}")


def display_recommendations() -> None:
    """Render the recommendation page inside the Streamlit app."""

    st.markdown(
        '<p class="section-title">🎯 Movie Recommendation Engine</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Three algorithms work together: **Content-Based** (overview & genres), "
        "**Collaborative Filtering** (latent-factor SVD on user–movie patterns), "
        "and a **Hybrid** blend of both."
    )

    content_rec = _get_content_recommender()
    _get_collaborative_recommender()        # warm up cache
    hybrid_rec = _get_hybrid_recommender()

    selected = st.selectbox(
        "Type or select a movie",
        options=[""] + content_rec.titles,
        index=0,
        placeholder="Search for a movie …",
    )

    top_k = st.slider("Number of recommendations", 3, 10, 5)

    if not selected:
        return

    # ── Section 1: Similar Movies (content-based) ──────────────────────
    cb_results = content_rec.recommend(selected, top_k=top_k)

    st.markdown("---")
    st.subheader(f"🎬 Similar Movies  ·  *{selected}*")

    if cb_results:
        _render_movie_cards(cb_results)
    else:
        st.warning("No similar movies found.")

    # ── Section 2: For You (hybrid) ────────────────────────────────────
    hybrid_results = hybrid_rec.recommend(selected, top_k=top_k)

    st.markdown("---")
    st.subheader(f"🍿 For You  ·  *{selected}*")

    if hybrid_results:
        _render_movie_cards(hybrid_results)
    else:
        st.warning("No personalised recommendations available.")
