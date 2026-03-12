"""
Movie Recommendation Engine
============================

Three recommendation strategies are implemented:

1. **Content-Based Filtering** (`MovieRecommender`)
   - Vectorizes movie overview + genres with CountVectorizer (BoW, 5 000 features)
   - Ranks candidates by cosine similarity on the BoW matrix
   - Used for the "Similar Movies" section

2. **Collaborative Filtering** (`CollaborativeRecommender`)
   - Builds a synthetic user–movie ratings matrix from genre preferences
   - Applies Truncated SVD to learn latent factors
   - Computes item–item similarity in the latent space
   - Used as a signal inside the Hybrid recommender

3. **Hybrid Filtering** (`HybridRecommender`)
   - Blends content-based and collaborative similarity scores
   - Configurable weight (default 0.6 content / 0.4 collaborative)
   - Used for the "For You" section

All models rebuild on cold start so they always reflect the latest
scraped data — no stale pickle files required.
"""

import logging
import os
from typing import List

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir,
    "extracted_data", "real_movie_data.csv",
)
_MAX_FEATURES = 5_000
_N_SYNTHETIC_USERS = 50
_SVD_COMPONENTS = 20
_HYBRID_CONTENT_WEIGHT = 0.6   # collaborative gets 1 - this


# ───────────────────────────────────────────────────────────────────────────
# Helper: row → dict
# ───────────────────────────────────────────────────────────────────────────

def _row_to_dict(row: pd.Series, score: float) -> dict:
    return {
        "title": row["title"],
        "genres": row["genres"],
        "release_year": int(row["release_year"]) if pd.notna(row["release_year"]) else None,
        "rating": round(float(row["rating"]), 1) if pd.notna(row["rating"]) else None,
        "popularity": round(float(row["popularity"]), 1) if pd.notna(row["popularity"]) else None,
        "poster_path": row.get("poster_path", ""),
        "score": round(float(score), 4),
    }


# ───────────────────────────────────────────────────────────────────────────
# Helper: load & clean the shared dataframe
# ───────────────────────────────────────────────────────────────────────────

def _load_movie_df(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["title", "overview"]).copy()
    df = df.drop_duplicates(subset="movie_id", keep="last").reset_index(drop=True)
    return df


# ═══════════════════════════════════════════════════════════════════════════
# 1. Content-Based Recommender
# ═══════════════════════════════════════════════════════════════════════════

class MovieRecommender:
    """Content-based movie recommender built on the project's own scraped data."""

    def __init__(self, csv_path: str | None = None):
        self.csv_path = csv_path or os.path.normpath(_DATA_PATH)
        self.df: pd.DataFrame = pd.DataFrame()
        self._similarity = None
        self._is_ready = False

    # ----- public API -------------------------------------------------------

    def build(self) -> "MovieRecommender":
        """Load data, engineer tags, vectorize, and compute similarity."""
        logger.info("Building content-based recommendation model …")

        df = _load_movie_df(self.csv_path)

        # --- tag construction: overview words + genre tokens ---------
        df["_genres_clean"] = (
            df["genres"]
            .fillna("")
            .str.replace("|", " ", regex=False)
            .str.replace(",", " ", regex=False)
        )
        df["_tags"] = (
            df["overview"].fillna("").str.lower() + " " +
            df["_genres_clean"].str.lower()
        )

        vectorizer = CountVectorizer(
            max_features=_MAX_FEATURES,
            stop_words="english",
        )
        vectors = vectorizer.fit_transform(df["_tags"])
        self._similarity = cosine_similarity(vectors)

        # keep only the columns the UI needs
        self.df = df[["movie_id", "title", "genres", "release_year",
                       "rating", "popularity", "poster_path", "overview"]].copy()
        self._is_ready = True
        logger.info("Content-based model ready — %d movies indexed", len(self.df))
        return self

    def recommend(self, title: str, top_k: int = 5) -> List[dict]:
        if not self._is_ready:
            self.build()

        matches = self.df[self.df["title"] == title]
        if matches.empty:
            logger.warning("Title not found: %s", title)
            return []

        idx = matches.index[0]
        sim_scores = sorted(enumerate(self._similarity[idx]),
                            key=lambda x: x[1], reverse=True)

        return [_row_to_dict(self.df.iloc[i], score)
                for i, score in sim_scores[1: top_k + 1]]

    def similarity_vector(self, title: str) -> np.ndarray | None:
        """Return the full similarity row for *title* (used by Hybrid)."""
        if not self._is_ready:
            self.build()
        matches = self.df[self.df["title"] == title]
        if matches.empty:
            return None
        return self._similarity[matches.index[0]]

    @property
    def titles(self) -> list:
        if not self._is_ready:
            self.build()
        return sorted(self.df["title"].tolist())


# ═══════════════════════════════════════════════════════════════════════════
# 2. Collaborative Filtering Recommender  (item-based, SVD on synthetic
#    user–movie ratings)
# ═══════════════════════════════════════════════════════════════════════════

class CollaborativeRecommender:
    """
    Collaborative-filtering recommender using Truncated SVD on a synthetic
    user–movie ratings matrix.

    Because the scraped dataset has no real user-interaction data, we
    synthesize plausible ratings: each virtual user has a random genre
    preference profile, and rates movies higher when their genres align
    with those preferences (also influenced by movie popularity & rating).
    SVD then learns latent factors, and item–item similarity is computed
    in that latent space.
    """

    def __init__(self, csv_path: str | None = None,
                 n_users: int = _N_SYNTHETIC_USERS,
                 n_components: int = _SVD_COMPONENTS):
        self.csv_path = csv_path or os.path.normpath(_DATA_PATH)
        self.n_users = n_users
        self.n_components = n_components
        self.df: pd.DataFrame = pd.DataFrame()
        self._similarity = None
        self._is_ready = False

    def build(self) -> "CollaborativeRecommender":
        logger.info("Building collaborative filtering model …")

        df = _load_movie_df(self.csv_path)

        # --- build a genre one-hot matrix --------------------------------
        all_genres: set[str] = set()
        for g in df["genres"].fillna(""):
            for token in g.replace(",", "|").split("|"):
                token = token.strip()
                if token:
                    all_genres.add(token)
        all_genres_list = sorted(all_genres)

        genre_matrix = np.zeros((len(df), len(all_genres_list)), dtype=np.float32)
        for i, g in enumerate(df["genres"].fillna("")):
            for token in g.replace(",", "|").split("|"):
                token = token.strip()
                if token in all_genres_list:
                    genre_matrix[i, all_genres_list.index(token)] = 1.0

        # --- synthesize user–movie ratings --------------------------------
        rng = np.random.default_rng(42)
        user_genre_pref = rng.random((self.n_users, len(all_genres_list)))

        # base affinity = user-genre preferences × genre matrix^T  → (users, movies)
        ratings = user_genre_pref @ genre_matrix.T

        # inject movie quality: scale by normalised rating & popularity
        norm_rating = MinMaxScaler().fit_transform(
            df["rating"].fillna(df["rating"].median()).values.reshape(-1, 1)
        ).ravel()
        norm_pop = MinMaxScaler().fit_transform(
            df["popularity"].fillna(df["popularity"].median()).values.reshape(-1, 1)
        ).ravel()
        quality = 0.7 * norm_rating + 0.3 * norm_pop
        ratings = ratings * quality[np.newaxis, :]

        # add small noise so SVD has meaningful variance
        ratings += rng.normal(0, 0.05, ratings.shape)
        ratings = np.clip(ratings, 0, None)

        # --- SVD in latent space -----------------------------------------
        n_comp = min(self.n_components, min(ratings.shape) - 1)
        svd = TruncatedSVD(n_components=n_comp, random_state=42)
        item_factors = svd.fit_transform(ratings.T)       # (movies, components)
        self._similarity = cosine_similarity(item_factors)

        self.df = df[["movie_id", "title", "genres", "release_year",
                       "rating", "popularity", "poster_path", "overview"]].copy()
        self._is_ready = True
        logger.info("Collaborative model ready — %d movies, %d latent factors",
                     len(self.df), n_comp)
        return self

    def recommend(self, title: str, top_k: int = 5) -> List[dict]:
        if not self._is_ready:
            self.build()

        matches = self.df[self.df["title"] == title]
        if matches.empty:
            logger.warning("Title not found: %s", title)
            return []

        idx = matches.index[0]
        sim_scores = sorted(enumerate(self._similarity[idx]),
                            key=lambda x: x[1], reverse=True)

        return [_row_to_dict(self.df.iloc[i], score)
                for i, score in sim_scores[1: top_k + 1]]

    def similarity_vector(self, title: str) -> np.ndarray | None:
        if not self._is_ready:
            self.build()
        matches = self.df[self.df["title"] == title]
        if matches.empty:
            return None
        return self._similarity[matches.index[0]]

    @property
    def titles(self) -> list:
        if not self._is_ready:
            self.build()
        return sorted(self.df["title"].tolist())


# ═══════════════════════════════════════════════════════════════════════════
# 3. Hybrid Recommender  (weighted blend of content + collaborative)
# ═══════════════════════════════════════════════════════════════════════════

class HybridRecommender:
    """
    Weighted hybrid of content-based and collaborative similarity scores.

    hybrid_score = α · content_sim + (1 − α) · collaborative_sim
    where α = content_weight (default 0.6).
    """

    def __init__(self,
                 content: MovieRecommender,
                 collaborative: CollaborativeRecommender,
                 content_weight: float = _HYBRID_CONTENT_WEIGHT):
        self.content = content
        self.collaborative = collaborative
        self.alpha = content_weight

    def recommend(self, title: str, top_k: int = 5) -> List[dict]:
        cb_vec = self.content.similarity_vector(title)
        cf_vec = self.collaborative.similarity_vector(title)

        if cb_vec is None or cf_vec is None:
            logger.warning("Title not found for hybrid: %s", title)
            return []

        # align lengths (both should be identical if same CSV was used)
        n = min(len(cb_vec), len(cf_vec))
        hybrid_scores = self.alpha * cb_vec[:n] + (1 - self.alpha) * cf_vec[:n]

        matches = self.content.df[self.content.df["title"] == title]
        idx = matches.index[0]

        scored = sorted(enumerate(hybrid_scores), key=lambda x: x[1], reverse=True)

        return [_row_to_dict(self.content.df.iloc[i], score)
                for i, score in scored if i != idx][:top_k]

    @property
    def titles(self) -> list:
        return self.content.titles
