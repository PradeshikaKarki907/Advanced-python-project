import logging
import json
import re
import time
import os
from typing import Dict, List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

# ============================================================================
# Logger Configuration
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# TMDB Credentials
# ============================================================================

TMDB_API_KEY = os.environ.get(
    "TMDB_API_KEY",
    "c2092a8aac44f904b920094800e44448",
)
TMDB_READ_TOKEN = os.environ.get(
    "TMDB_READ_TOKEN",
    "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjMjA5MmE4YWFjNDRmOTA0YjkyMDA5NDgwMGU0NDQ0OCIsIm5iZiI6MTc3MzIwNjUwOS43MTQsInN1YiI6IjY5YjBmYmVkZmZlOTk1MTU2ODk1OTZjYSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.3tiHsAC8sCavROB_YITFDz4W0oLi0HqZKWQHCtFzsjI",
)


# ============================================================================
# Wikipedia Live Scraper
# ============================================================================

class WikipediaMovieScraper:
    """
    Live-scrape movie data from Wikipedia's publicly available film tables.

    Primary source: "List of highest-grossing films" (has Rank, Title, Year,
    Worldwide gross in a clean wikitable).
    Secondary: year-based American film lists.
    Falls back to embedded sample data only when Wikipedia is unreachable.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'MovieDataPipeline/2.0 '
                '(Advanced Python Project; educational use) '
                'requests/' + requests.__version__
            )
        })
        logger.info("WikipediaMovieScraper initialized")

    # ------------------------------------------------------------------ #
    #  Primary method – highest-grossing films from Wikipedia             #
    # ------------------------------------------------------------------ #
    def scrape_highest_rated_films(self, limit: int = 250) -> pd.DataFrame:
        """
        Live-scrape the highest-grossing films table from Wikipedia.
        Falls back to embedded sample data if Wikipedia is unreachable.
        """
        logger.info(
            f"Attempting to live-scrape up to {limit} films from Wikipedia..."
        )

        urls_to_try = [
            "https://en.wikipedia.org/wiki/List_of_highest-grossing_films",
            "https://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture",
        ]

        for url in urls_to_try:
            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
                logger.info(f"✅ Connected to {url}")
                df = self._parse_wikitable(resp.text, limit)
                if not df.empty:
                    logger.info(
                        f"✅ Live-scraped {len(df)} films from {url}"
                    )
                    return df
            except Exception as e:
                logger.warning(f"Could not scrape {url}: {e}")

        logger.warning("All Wikipedia URLs failed – using embedded fallback data")
        return self._fallback_data(limit)

    # ------------------------------------------------------------------ #
    #  Generic wikitable parser                                          #
    # ------------------------------------------------------------------ #
    def _parse_wikitable(self, html: str, limit: int) -> pd.DataFrame:
        """
        Find the first wikitable with a recognisable 'Title' / 'Film' column
        and extract rows into a standardised DataFrame.
        """
        soup = BeautifulSoup(html, 'html.parser')
        movies: List[dict] = []

        for table in soup.find_all('table', class_='wikitable'):
            rows = table.find_all('tr')
            if len(rows) < 5:
                continue

            header_cells = [
                th.get_text(strip=True).lower()
                for th in rows[0].find_all(['th', 'td'])
            ]

            # Map columns by keyword
            col_map: Dict[str, int] = {}
            for idx, h in enumerate(header_cells):
                h_lower = h.lower()
                if ('rank' in h_lower or h_lower == '#') and 'rank' not in col_map:
                    col_map['rank'] = idx
                elif ('title' in h_lower or 'film' in h_lower) and 'title' not in col_map:
                    col_map['title'] = idx
                elif 'year' in h_lower and 'title' not in h_lower and 'year' not in col_map:
                    col_map['year'] = idx
                elif ('gross' in h_lower or 'box office' in h_lower) and 'gross' not in col_map:
                    col_map['gross'] = idx
                elif ('rating' in h_lower or 'score' in h_lower) and 'rating' not in col_map:
                    col_map['rating'] = idx
                elif 'genre' in h_lower and 'genre' not in col_map:
                    col_map['genre'] = idx
                elif 'director' in h_lower and 'director' not in col_map:
                    col_map['director'] = idx
                elif 'studio' in h_lower and 'studio' not in col_map:
                    col_map['studio'] = idx

            if 'title' not in col_map:
                continue

            max_col = max(col_map.values())

            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) <= max_col:
                    continue

                title = cells[col_map['title']].get_text(strip=True)
                if not title or len(title) < 2:
                    continue

                # Year
                year = 0
                if 'year' in col_map:
                    ym = re.search(r'(\d{4})', cells[col_map['year']].get_text(strip=True))
                    year = int(ym.group(1)) if ym else 0

                # Rating (if present)
                rating = 0.0
                if 'rating' in col_map:
                    rm = re.search(r'(\d+\.?\d*)', cells[col_map['rating']].get_text(strip=True))
                    rating = float(rm.group(1)) if rm else 0.0

                # Gross (convert to popularity proxy)
                gross_val = 0
                if 'gross' in col_map:
                    raw = cells[col_map['gross']].get_text(strip=True)
                    raw_digits = re.sub(r'[^0-9]', '', raw)
                    gross_val = int(raw_digits) if raw_digits else 0

                genre = 'Unknown'
                if 'genre' in col_map:
                    genre = cells[col_map['genre']].get_text(strip=True).replace(', ', '|')

                movies.append({
                    'movie_id': f"WIKI{len(movies)+1:05d}",
                    'title': title,
                    'genres': genre,
                    'release_year': year,
                    'runtime': 0,
                    'rating': rating,
                    'vote_count': 0,
                    'popularity': gross_val / 1_000_000 if gross_val else 0.0,
                    'overview': f"{title} ({year})" if year else title,
                })

                if len(movies) >= limit:
                    break

            if movies:
                break

        return pd.DataFrame(movies)

    # ------------------------------------------------------------------ #
    #  Scrape films by year                                               #
    # ------------------------------------------------------------------ #
    def scrape_films_by_year(self, year: int, limit: int = 50) -> pd.DataFrame:
        """
        Live-scrape a year-based American film list from Wikipedia.
        """
        logger.info(f"Scraping up to {limit} films from {year}...")
        url = f"https://en.wikipedia.org/wiki/List_of_American_films_of_{year}"

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching films for {year}: {e}")
            return pd.DataFrame()

        soup = BeautifulSoup(resp.text, 'html.parser')
        movies: List[dict] = []

        for table in soup.find_all('table', class_='wikitable'):
            rows = table.find_all('tr')
            if len(rows) < 3:
                continue

            headers = [
                th.get_text(strip=True).lower()
                for th in rows[0].find_all(['th', 'td'])
            ]

            title_idx = next(
                (i for i, h in enumerate(headers) if 'title' in h or 'film' in h),
                None,
            )
            if title_idx is None:
                continue

            genre_idx = next(
                (i for i, h in enumerate(headers) if 'genre' in h), None
            )

            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) <= title_idx:
                    continue
                title = cells[title_idx].get_text(strip=True)
                if not title or len(title) < 2:
                    continue

                genre = 'Unknown'
                if genre_idx is not None and len(cells) > genre_idx:
                    genre = cells[genre_idx].get_text(strip=True)

                movies.append({
                    'movie_id': f"WIKI{len(movies)+1:05d}",
                    'title': title,
                    'genres': genre.replace(', ', '|'),
                    'release_year': year,
                    'runtime': 0,
                    'rating': 0.0,
                    'vote_count': 0,
                    'popularity': 0.0,
                    'overview': f"A film from {year}",
                })

                if len(movies) >= limit:
                    break
            if movies:
                break

        df = pd.DataFrame(movies)
        logger.info(f"Scraped {len(df)} films from {year}")
        return df

    # ------------------------------------------------------------------ #
    #  Embedded fallback data (used only when Wikipedia is unreachable)   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _fallback_data(limit: int) -> pd.DataFrame:
        fallback = [
            ('The Shawshank Redemption', 1994, 9.3, 'Drama', 142),
            ('The Godfather', 1972, 9.2, 'Crime|Drama', 175),
            ('The Dark Knight', 2008, 9.0, 'Action|Crime|Drama', 152),
            ('Pulp Fiction', 1994, 8.9, 'Crime|Drama', 154),
            ('Forrest Gump', 1994, 8.8, 'Drama|Romance', 142),
            ('Inception', 2010, 8.8, 'Action|Sci-Fi', 148),
            ('The Matrix', 1999, 8.7, 'Action|Sci-Fi', 136),
            ('Goodfellas', 1990, 8.7, 'Crime|Drama', 146),
            ('Interstellar', 2014, 8.6, 'Adventure|Drama|Sci-Fi', 169),
            ('Fight Club', 1999, 8.8, 'Drama', 139),
            ('Gladiator', 2000, 8.5, 'Action|Adventure|Drama', 155),
            ('The Silence of the Lambs', 1991, 8.6, 'Crime|Drama|Thriller', 118),
            ('Saving Private Ryan', 1998, 8.6, 'Drama|War', 169),
            ('Jurassic Park', 1993, 8.2, 'Action|Adventure|Sci-Fi', 127),
            ('The Avengers', 2012, 8.0, 'Action|Adventure|Sci-Fi', 143),
            ('Avatar', 2009, 7.8, 'Action|Adventure|Sci-Fi', 162),
            ('Titanic', 1997, 7.8, 'Drama|Romance', 194),
            ('Parasite', 2019, 8.5, 'Drama|Thriller', 132),
            ('Oppenheimer', 2023, 8.1, 'Drama|History', 180),
            ('The Lion King', 1994, 8.5, 'Animation|Adventure|Drama', 88),
            ('Back to the Future', 1985, 8.5, 'Adventure|Comedy|Sci-Fi', 116),
            ('Se7en', 1995, 8.6, 'Crime|Drama|Mystery', 127),
            ('The Green Mile', 1999, 8.6, 'Crime|Drama|Fantasy', 189),
            ('City of God', 2002, 8.8, 'Crime|Drama', 130),
            ('The Prestige', 2006, 8.5, 'Drama|Mystery|Sci-Fi', 130),
            ('The Departed', 2006, 8.5, 'Crime|Drama|Thriller', 151),
            ('Whiplash', 2014, 8.5, 'Drama|Music', 106),
            ("Schindler's List", 1993, 9.0, 'Biography|Drama|History', 195),
            ('No Country for Old Men', 2007, 8.4, 'Crime|Drama|Thriller', 122),
            ('Catch Me If You Can', 2002, 8.1, 'Biography|Crime|Drama', 141),
        ]
        rows = []
        for i, (title, year, rating, genres, runtime) in enumerate(fallback[:limit]):
            rows.append({
                'movie_id': f"WIKI{i+1:05d}",
                'title': title,
                'genres': genres,
                'release_year': year,
                'runtime': runtime,
                'rating': rating,
                'vote_count': int(1_000_000 * (rating / 10)),
                'popularity': rating * 10,
                'overview': f"{title} is a highly-rated film from {year}",
            })
        return pd.DataFrame(rows)


# ============================================================================
# TMDB Live API Scraper
# ============================================================================

class TMDbAPIScraper:
    """
    Live extraction from The Movie Database (TMDB) REST API.

    Uses the v4 Bearer token for authentication (passed via the
    Authorization header) so no query-string key is needed, but the
    v3 api_key param is also supported as a fallback.

    Free tier limits: 40 requests per 10 seconds.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        read_token: Optional[str] = None,
    ):
        self.api_key = api_key or TMDB_API_KEY
        self.read_token = read_token or TMDB_READ_TOKEN
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        # Prefer Bearer token auth (v4 style on v3 endpoints)
        self.session.headers.update({
            'Authorization': f'Bearer {self.read_token}',
            'Accept': 'application/json',
        })
        self._genre_cache: Dict[int, str] = {}
        logger.info("TMDbAPIScraper initialized (live API)")

    # ------------------------------------------------------------------ #
    #  Genre resolution                                                   #
    # ------------------------------------------------------------------ #
    def _load_genres(self) -> None:
        """Fetch the genre-id → name mapping from TMDB."""
        if self._genre_cache:
            return
        try:
            resp = self.session.get(
                f"{self.base_url}/genre/movie/list",
                params={'language': 'en-US'},
                timeout=10,
            )
            resp.raise_for_status()
            for g in resp.json().get('genres', []):
                self._genre_cache[g['id']] = g['name']
            logger.info(f"Loaded {len(self._genre_cache)} TMDB genre mappings")
        except Exception as e:
            logger.warning(f"Could not load TMDB genres: {e}")

    def _resolve_genres(self, genre_ids: list) -> str:
        """Convert a list of genre IDs to pipe-separated names."""
        self._load_genres()
        names = [self._genre_cache.get(gid, f"Genre{gid}") for gid in genre_ids]
        return '|'.join(names) if names else 'Unknown'

    # ------------------------------------------------------------------ #
    #  Movie detail (runtime)                                             #
    # ------------------------------------------------------------------ #
    def _get_runtime(self, movie_id: int) -> int:
        """Fetch runtime for a single movie from the /movie/{id} endpoint."""
        try:
            resp = self.session.get(
                f"{self.base_url}/movie/{movie_id}",
                params={'language': 'en-US'},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get('runtime', 0) or 0
        except Exception:
            return 0

    # ------------------------------------------------------------------ #
    #  List endpoints                                                     #
    # ------------------------------------------------------------------ #
    def _fetch_list(self, endpoint: str, num_pages: int, fetch_runtime: bool) -> pd.DataFrame:
        """Generic fetcher for any TMDB list endpoint (popular, top_rated, etc.)."""
        logger.info(f"Fetching {endpoint} from TMDB ({num_pages} pages)...")
        movies: List[dict] = []

        for page in range(1, num_pages + 1):
            try:
                resp = self.session.get(
                    f"{self.base_url}/movie/{endpoint}",
                    params={'language': 'en-US', 'page': page},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error(f"TMDB request failed (page {page}): {e}")
                break

            for m in data.get('results', []):
                release = m.get('release_date', '') or ''
                year = int(release[:4]) if len(release) >= 4 else 0

                runtime = 0
                if fetch_runtime:
                    runtime = self._get_runtime(m['id'])
                    time.sleep(0.15)  # stay within rate limits

                genre_ids = m.get('genre_ids', [])

                movies.append({
                    'movie_id': f"TMDB{m['id']}",
                    'title': m.get('title', 'Unknown'),
                    'genres': self._resolve_genres(genre_ids),
                    'genre_ids': ', '.join(str(g) for g in genre_ids),
                    'release_year': year,
                    'release_date': release,
                    'runtime': runtime,
                    'rating': m.get('vote_average', 0.0),
                    'vote_count': m.get('vote_count', 0),
                    'popularity': m.get('popularity', 0.0),
                    'overview': m.get('overview', ''),
                    'poster_path': m.get('poster_path', ''),
                    'backdrop_path': m.get('backdrop_path', ''),
                    'original_language': m.get('original_language', ''),
                    'original_title': m.get('original_title', ''),
                    'adult': m.get('adult', False),
                    'video': m.get('video', False),
                })

            logger.info(f"  page {page}: {len(data.get('results', []))} movies")
            time.sleep(0.3)

        df = pd.DataFrame(movies)
        logger.info(f"✅ Fetched {len(df)} movies from TMDB /{endpoint}")
        return df

    def search_popular_movies(self, num_pages: int = 1, fetch_runtime: bool = False) -> pd.DataFrame:
        """Get popular movies from TMDB (live)."""
        return self._fetch_list('popular', num_pages, fetch_runtime)

    def search_top_rated_movies(self, num_pages: int = 1, fetch_runtime: bool = False) -> pd.DataFrame:
        """Get top-rated movies from TMDB (live)."""
        return self._fetch_list('top_rated', num_pages, fetch_runtime)

    def search_now_playing(self, num_pages: int = 1, fetch_runtime: bool = False) -> pd.DataFrame:
        """Get now-playing movies from TMDB (live)."""
        return self._fetch_list('now_playing', num_pages, fetch_runtime)

    # ------------------------------------------------------------------ #
    #  Discover endpoint – filter by year range, sort, vote threshold     #
    # ------------------------------------------------------------------ #
    def discover_movies(
        self,
        start_year: int = 1990,
        end_year: int = 2026,
        pages_per_decade: int = 5,
        min_votes: int = 200,
        sort_by: str = 'vote_count.desc',
        fetch_runtime: bool = False,
    ) -> pd.DataFrame:
        """
        Use TMDB /discover/movie to fetch movies across a year range.

        Splits the range into per-year batches so we get good coverage
        from the 1990s through today.

        Parameters
        ----------
        start_year, end_year : int
            Inclusive year range.
        pages_per_decade : int
            How many pages (20 results each) to fetch **per year**.
            Default 5 → ~100 movies per year sampled.
        min_votes : int
            Minimum vote_count filter to keep quality data.
        sort_by : str
            TMDB sort key (vote_count.desc, popularity.desc, etc.).
        fetch_runtime : bool
            If True, hit /movie/{id} for each movie (slower).
        """
        logger.info(
            f"Discover: years {start_year}-{end_year}, "
            f"{pages_per_decade} pages/year, min_votes={min_votes}"
        )
        self._load_genres()
        all_movies: List[dict] = []
        seen_ids: set = set()

        for year in range(start_year, end_year + 1):
            for page in range(1, pages_per_decade + 1):
                try:
                    resp = self.session.get(
                        f"{self.base_url}/discover/movie",
                        params={
                            'language': 'en-US',
                            'sort_by': sort_by,
                            'primary_release_date.gte': f'{year}-01-01',
                            'primary_release_date.lte': f'{year}-12-31',
                            'vote_count.gte': min_votes,
                            'page': page,
                        },
                        timeout=10,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as e:
                    logger.error(f"Discover {year} page {page}: {e}")
                    break

                results = data.get('results', [])
                if not results:
                    break  # no more pages for this year

                for m in results:
                    mid = m['id']
                    if mid in seen_ids:
                        continue
                    seen_ids.add(mid)

                    release = m.get('release_date', '') or ''
                    yr = int(release[:4]) if len(release) >= 4 else year

                    runtime = 0
                    if fetch_runtime:
                        runtime = self._get_runtime(mid)
                        time.sleep(0.15)

                    genre_ids = m.get('genre_ids', [])
                    all_movies.append({
                        'movie_id': f"TMDB{mid}",
                        'title': m.get('title', 'Unknown'),
                        'genres': self._resolve_genres(genre_ids),
                        'genre_ids': ', '.join(str(g) for g in genre_ids),
                        'release_year': yr,
                        'release_date': release,
                        'runtime': runtime,
                        'rating': m.get('vote_average', 0.0),
                        'vote_count': m.get('vote_count', 0),
                        'popularity': m.get('popularity', 0.0),
                        'overview': m.get('overview', ''),
                        'poster_path': m.get('poster_path', ''),
                        'backdrop_path': m.get('backdrop_path', ''),
                        'original_language': m.get('original_language', ''),
                        'original_title': m.get('original_title', ''),
                        'adult': m.get('adult', False),
                        'video': m.get('video', False),
                    })

                time.sleep(0.3)  # rate-limit courtesy

            if all_movies and len(all_movies) % 200 < 20:
                logger.info(f"  ... {year}: {len(all_movies)} total so far")

        df = pd.DataFrame(all_movies)
        logger.info(f"\u2705 Discover complete: {len(df)} unique movies ({start_year}-{end_year})")
        return df


# ============================================================================
# Unified Scraper
# ============================================================================

class MovieDataScraper:
    """
    Unified scraper using the best available source.
    Tries TMDB live API first, falls back to Wikipedia live scrape.
    """

    def __init__(
        self,
        tmdb_api_key: Optional[str] = None,
        tmdb_read_token: Optional[str] = None,
    ):
        self.wikipedia = WikipediaMovieScraper()
        self.tmdb = TMDbAPIScraper(
            api_key=tmdb_api_key,
            read_token=tmdb_read_token,
        )
        logger.info("MovieDataScraper initialized")

    def scrape_real_data(
        self,
        source: str = 'auto',
        num_movies: int = 50,
        fetch_runtime: bool = False,
    ) -> pd.DataFrame:
        """
        Scrape real movie data from available sources.

        Parameters
        ----------
        source : str
            'auto'      – Try TMDB first, fall back to Wikipedia
            'tmdb'      – TMDB API only
            'wikipedia' – Wikipedia only
        num_movies : int
            Approximate number of movies to scrape.
        fetch_runtime : bool
            If True, fetch per-movie runtime from TMDB (slower but complete).

        Returns
        -------
        pd.DataFrame   Standardized movie data.
        """
        pages = max(1, num_movies // 20)

        if source == 'auto':
            df = self.tmdb.search_popular_movies(num_pages=pages, fetch_runtime=fetch_runtime)
            if not df.empty:
                logger.info(f"Using TMDB data ({len(df)} movies)")
                return df
            logger.info("TMDB unavailable – falling back to Wikipedia")
            return self.wikipedia.scrape_highest_rated_films(limit=num_movies)

        if source == 'tmdb':
            return self.tmdb.search_popular_movies(num_pages=pages, fetch_runtime=fetch_runtime)

        if source == 'wikipedia':
            return self.wikipedia.scrape_highest_rated_films(limit=num_movies)

        logger.error(f"Unknown source: {source}")
        return pd.DataFrame()

    def scrape_all_eras(
        self,
        start_year: int = 1990,
        end_year: int = 2026,
        pages_per_decade: int = 5,
        min_votes: int = 200,
        fetch_runtime: bool = False,
    ) -> pd.DataFrame:
        """
        Scrape a broad dataset spanning decades using TMDB Discover,
        supplemented with popular / top-rated lists and Wikipedia.
        """
        # 1. Discover across year range (bulk of the dataset)
        df_discover = self.tmdb.discover_movies(
            start_year=start_year,
            end_year=end_year,
            pages_per_decade=pages_per_decade,
            min_votes=min_votes,
            fetch_runtime=fetch_runtime,
        )

        # 2. Supplement with popular + top-rated lists
        df_pop = self.tmdb.search_popular_movies(num_pages=3, fetch_runtime=fetch_runtime)
        df_top = self.tmdb.search_top_rated_movies(num_pages=3, fetch_runtime=fetch_runtime)

        # 3. Merge & deduplicate
        combined = pd.concat([df_discover, df_pop, df_top], ignore_index=True)
        combined.drop_duplicates(subset='movie_id', keep='first', inplace=True)
        combined.sort_values('release_year', ascending=False, inplace=True)
        combined.reset_index(drop=True, inplace=True)

        logger.info(f"\u2705 All-eras scrape: {len(combined)} unique movies")
        return combined

    def save_scraped_data(self, df: pd.DataFrame, filename: str = 'scraped_movies.csv') -> str:
        """Save scraped data to CSV. Merges with existing data if present."""
        os.makedirs('extracted_data', exist_ok=True)
        filepath = os.path.join('extracted_data', filename)

        # Merge with existing CSV to accumulate over time
        if os.path.exists(filepath):
            try:
                existing = pd.read_csv(filepath)
                df = pd.concat([existing, df], ignore_index=True)
                df.drop_duplicates(subset='movie_id', keep='last', inplace=True)
                logger.info(f"Merged with existing data → {len(df)} unique movies")
            except Exception as e:
                logger.warning(f"Could not merge with existing CSV: {e}")

        df.to_csv(filepath, index=False)
        logger.info(f"Scraped data saved to {filepath}")
        return filepath


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

def example_1_wikipedia():
    """Live-scrape from Wikipedia (no API key needed)."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Live scrape from Wikipedia")
    print("=" * 80)

    scraper = MovieDataScraper()
    df = scraper.scrape_real_data(source='wikipedia', num_movies=50)

    print(f"\n✅ Scraped {len(df)} movies from Wikipedia")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    if not df.empty:
        path = scraper.save_scraped_data(df, filename='wikipedia_movies.csv')
        print(f"\n✅ Saved to: {path}")


def example_2_tmdb():
    """Live-fetch from TMDB API."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Live fetch from TMDB API")
    print("=" * 80)

    scraper = MovieDataScraper()
    df = scraper.scrape_real_data(source='tmdb', num_movies=40)

    print(f"\n✅ Fetched {len(df)} movies from TMDB")
    if not df.empty:
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False))
        path = scraper.save_scraped_data(df, filename='tmdb_movies.csv')
        print(f"\n✅ Saved to: {path}")


def example_3_auto_fallback():
    """Auto-detect best source."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Auto-detect Best Source")
    print("=" * 80)

    scraper = MovieDataScraper()
    df = scraper.scrape_real_data(source='auto', num_movies=50)

    print(f"✅ Scraped {len(df)} movies (auto)")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    if not df.empty:
        path = scraper.save_scraped_data(df, filename='real_movie_data.csv')
        print(f"\n✅ Saved to: {path}")


if __name__ == "__main__":
    print("\n🎬  Movie Data Scraper v2.0 – Live Wikipedia + TMDB\n")
    example_1_wikipedia()
    example_2_tmdb()
    example_3_auto_fallback()
