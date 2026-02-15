"""
Flexible Data Loader for Multiple Movie Database Sources
Auto-detects and maps columns from various movie databases to standardized schema
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FlexibleDataLoader:
    """
    Universal data loader that auto-detects and maps columns from multiple sources.
    Supports: TMDB, IMDb, Rotten Tomatoes, MovieLens, Letterboxd, Kaggle datasets
    """
    
    # Standard schema that pipeline expects
    STANDARD_SCHEMA = {
        'movie_id': str,
        'title': str,
        'genres': str,  # pipe-separated: 'Action|Drama|Sci-Fi'
        'release_year': int,
        'runtime': int,
        'rating': float,
        'vote_count': int,
        'popularity': float,
        'overview': str
    }
    
    # Column name mappings for different sources
    SOURCE_MAPPINGS = {
        'tmdb': {
            'id': 'movie_id',
            'title': 'title',
            'genres': 'genres',
            'release_date': 'release_year',
            'runtime': 'runtime',
            'vote_average': 'rating',
            'vote_count': 'vote_count',
            'popularity': 'popularity',
            'overview': 'overview'
        },
        'imdb': {
            'tconst': 'movie_id',
            'primary_title': 'title',
            'original_title': 'title',
            'genres': 'genres',
            'start_year': 'release_year',
            'runtime_minutes': 'runtime',
            'average_rating': 'rating',
            'num_votes': 'vote_count',
            'title_id': 'movie_id'
        },
        'movielens': {
            'movieid': 'movie_id',
            'movie_id': 'movie_id',
            'title': 'title',
            'genres': 'genres',
            'rating': 'rating',
            'timestamp': 'vote_count'
        },
        'rotten_tomatoes': {
            'id': 'movie_id',
            'name': 'title',
            'title': 'title',
            'genre': 'genres',
            'genres': 'genres',
            'year': 'release_year',
            'rating': 'rating',
            'audience_score': 'rating',
            'imdb_rating': 'rating'
        },
        'letterboxd': {
            'id': 'movie_id',
            'name': 'title',
            'year': 'release_year',
            'genre': 'genres',
            'rating': 'rating',
            'rating_count': 'vote_count',
            'description': 'overview'
        },
        'kaggle': {
            'movie_id': 'movie_id',
            'film_name': 'title',
            'movie_name': 'title',
            'name': 'title',
            'genre': 'genres',
            'release_year': 'release_year',
            'year': 'release_year',
            'rating': 'rating',
            'votes': 'vote_count',
            'runtime': 'runtime'
        }
    }
    
    # Fuzzy matching for column detection (case-insensitive)
    FUZZY_PATTERNS = {
        'movie_id': ['id', 'movie_id', 'tconst', 'imdb_id', 'film_id'],
        'title': ['title', 'name', 'film_name', 'movie_name', 'primary_title', 'original_title'],
        'genres': ['genre', 'genres', 'genre_list', 'category'],
        'release_year': ['year', 'release_year', 'release_date', 'start_year', 'release_date_published'],
        'runtime': ['runtime', 'duration', 'length', 'running_time'],
        'rating': ['rating', 'score', 'imdb_rating', 'average_rating', 'audience_score', 'vote_average'],
        'vote_count': ['votes', 'vote_count', 'num_votes', 'number_of_votes', 'rating_count', 'count'],
        'popularity': ['popularity', 'popular', 'score'],
        'overview': ['overview', 'description', 'synopsis', 'summary', 'plot']
    }
    
    def __init__(self):
        logger.info("FlexibleDataLoader initialized")
    
    def load_and_map(self, filepath: str, source: Optional[str] = None, 
                     custom_mapping: Optional[Dict] = None) -> pd.DataFrame:
        """
        Load data from file and auto-map columns to standard schema.
        
        Parameters:
        -----------
        filepath : str
            Path to data file (CSV or JSON)
        source : str, optional
            Data source name ('tmdb', 'imdb', 'movielens', 'rotten_tomatoes', 'letterboxd', 'kaggle')
            If None, will attempt to auto-detect
        custom_mapping : dict, optional
            Custom column mappings {original_col: standard_col}
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with standardized schema
        """
        logger.info(f"Loading data from: {filepath}")
        
        # Load file
        try:
            if filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise
        
        # Detect source if not provided
        if source is None:
            source = self._detect_source(df)
            logger.info(f"Auto-detected source: {source}")
        
        # Get mapping
        if custom_mapping:
            mapping = custom_mapping
            logger.info("Using custom column mapping")
        else:
            mapping = self._get_column_mapping(df, source)
            logger.info(f"Using mapping for source: {source}")
        
        # Apply mapping
        df_mapped = self._apply_mapping(df, mapping)
        
        # Validate and clean
        df_cleaned = self._validate_and_clean(df_mapped)
        
        logger.info(f"Successfully mapped to standard schema: {df_cleaned.shape}")
        return df_cleaned
    
    def _detect_source(self, df: pd.DataFrame) -> str:
        """Auto-detect data source based on column names"""
        df_cols_lower = {col.lower() for col in df.columns}
        
        # Check each source's signature columns
        source_signatures = {
            'imdb': {'tconst', 'primary_title', 'start_year'},
            'tmdb': {'id', 'vote_average', 'vote_count'},
            'movielens': {'movieid', 'userid', 'timestamp'},
            'rotten_tomatoes': {'audience_score', 'critics_score'},
            'letterboxd': {'imdb_code', 'imdb_id'},
            'kaggle': {'film_name', 'movie_name', 'name'}
        }
        
        scores = {}
        for source, sig_cols in source_signatures.items():
            match_count = len(sig_cols & df_cols_lower)
            scores[source] = match_count
        
        detected = max(scores, key=scores.get)
        logger.info(f"Source detection scores: {scores}")
        return detected if scores[detected] > 0 else 'kaggle'  # Default fallback
    
    def _get_column_mapping(self, df: pd.DataFrame, source: str) -> Dict[str, str]:
        """
        Get column mapping for a source.
        Tries exact match first, then fuzzy matching.
        """
        df_cols_lower = {col.lower(): col for col in df.columns}
        mapping = {}
        
        # Get source-specific mappings
        source_map = self.SOURCE_MAPPINGS.get(source, {})
        
        # Try exact matches first
        for orig_col, std_col in source_map.items():
            if orig_col.lower() in df_cols_lower:
                actual_col = df_cols_lower[orig_col.lower()]
                mapping[actual_col] = std_col
                logger.info(f"  Matched: {actual_col} -> {std_col}")
        
        # Fuzzy match remaining standard columns
        for std_col, patterns in self.FUZZY_PATTERNS.items():
            if std_col not in mapping.values():
                for pattern in patterns:
                    if pattern.lower() in df_cols_lower:
                        actual_col = df_cols_lower[pattern.lower()]
                        if actual_col not in mapping:
                            mapping[actual_col] = std_col
                            logger.info(f"  Fuzzy matched: {actual_col} -> {std_col}")
                            break
        
        if not mapping:
            logger.warning("No column mappings found! Using best-effort fuzzy matching.")
            mapping = self._fuzzy_match_all(df)
        
        return mapping
    
    def _fuzzy_match_all(self, df: pd.DataFrame) -> Dict[str, str]:
        """Fuzzy match all columns in dataframe"""
        df_cols_lower = {col.lower(): col for col in df.columns}
        mapping = {}
        
        for std_col, patterns in self.FUZZY_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in df_cols_lower:
                    actual_col = df_cols_lower[pattern.lower()]
                    if actual_col not in mapping:
                        mapping[actual_col] = std_col
                        break
        
        return mapping
    
    def _apply_mapping(self, df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Apply column mapping and drop unmapped columns"""
        # Rename mapped columns
        df_renamed = df.rename(columns=mapping)
        
        # Keep only standard schema columns that exist
        existing_std_cols = [col for col in self.STANDARD_SCHEMA.keys() if col in df_renamed.columns]
        df_final = df_renamed[existing_std_cols].copy()
        
        logger.info(f"Kept {len(existing_std_cols)} standard columns: {existing_std_cols}")
        return df_final
    
    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean data"""
        df = df.copy()
        
        # Remove duplicates by title + year
        initial_len = len(df)
        if 'title' in df.columns and 'release_year' in df.columns:
            df = df.drop_duplicates(subset=['title', 'release_year'], keep='first')
            logger.info(f"Removed {initial_len - len(df)} duplicates")
        
        # Fill missing values strategically
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df['rating'].fillna(df['rating'].median(), inplace=True)
        
        if 'vote_count' in df.columns:
            df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce')
            df['vote_count'].fillna(0, inplace=True)
        
        if 'runtime' in df.columns:
            df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
            df['runtime'].fillna(df['runtime'].median(), inplace=True)
        
        if 'release_year' in df.columns:
            df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
            df['release_year'] = df['release_year'].astype('Int64')
        
        if 'popularity' in df.columns:
            df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
            df['popularity'].fillna(0, inplace=True)
        
        # Add missing movie_id if not present
        if 'movie_id' not in df.columns:
            df['movie_id'] = [f"MOV{i+1:05d}" for i in range(len(df))]
            logger.info("Generated movie_ids")
        
        # Ensure genres is pipe-separated string
        if 'genres' in df.columns:
            df['genres'] = df['genres'].astype(str).apply(
                lambda x: x.replace('[', '').replace(']', '').replace("'", '').strip() 
                if pd.notna(x) else 'Unknown'
            )
        
        logger.info(f"Data validation complete. Final shape: {df.shape}")
        return df
    
    def show_mapping_report(self, filepath: str, source: Optional[str] = None) -> None:
        """Show detected columns and proposed mapping (for verification)"""
        try:
            if filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                df = pd.read_csv(filepath)
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            return
        
        if source is None:
            source = self._detect_source(df)
        
        mapping = self._get_column_mapping(df, source)
        
        print("\n" + "="*80)
        print(f"DATA SOURCE MAPPING REPORT")
        print("="*80)
        print(f"File: {filepath}")
        print(f"Detected Source: {source}")
        print(f"Total Columns: {len(df.columns)}")
        print(f"Total Rows: {len(df)}")
        print("\n" + "-"*80)
        print("COLUMN MAPPINGS:")
        print("-"*80)
        
        for orig_col, std_col in mapping.items():
            sample = df[orig_col].dropna().iloc[0] if not df[orig_col].dropna().empty else "N/A"
            print(f"  {orig_col:30} → {std_col:20} (sample: {str(sample)[:40]})")
        
        unmapped = set(df.columns) - set(mapping.keys())
        if unmapped:
            print("\n" + "-"*80)
            print("UNMAPPED COLUMNS (will be dropped):")
            print("-"*80)
            for col in unmapped:
                print(f"  {col}")
        
        print("\n" + "="*80 + "\n")


def example_usage():
    """Example usage of the flexible loader"""
    
    # Example 1: Load TMDB data
    print("Example 1: Loading TMDB data...")
    loader = FlexibleDataLoader()
    # df_tmdb = loader.load_and_map('tmdb_movies.csv', source='tmdb')
    
    # Example 2: Load IMDb data with auto-detection
    print("\nExample 2: Loading IMDb data with auto-detection...")
    # df_imdb = loader.load_and_map('imdb_title_basics.tsv', source='imdb')
    
    # Example 3: Show mapping report before loading
    print("\nExample 3: Preview mapping...")
    # loader.show_mapping_report('my_movie_data.csv')
    
    # Example 4: Custom mapping
    print("\nExample 4: Using custom mapping...")
    custom_map = {
        'Film Name': 'title',
        'Release Year': 'release_year',
        'IMDB Score': 'rating',
        'Genre': 'genres'
    }
    # df_custom = loader.load_and_map('unknown_source.csv', custom_mapping=custom_map)
    
    print("See comments above for actual usage with real files")


if __name__ == "__main__":
    example_usage()
