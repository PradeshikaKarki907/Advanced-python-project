"""
Movie Data Loading Module
Loads processed data into SQLite database with proper schema
"""

import pandas as pd
import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MovieDatabaseLoader:
    """Load movie data into SQLite database"""
    
    def __init__(self, db_path='../database/movies.db'):
        self.db_path = db_path
        self.conn = None
        logger.info(f"MovieDatabaseLoader initialized with database: {db_path}")
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info("Database connection established")
            return self.conn
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def create_schema(self):
        """Create database schema with proper tables and indexes"""
        logger.info("Creating database schema...")
        
        try:
            cursor = self.conn.cursor()
            
            # Create movies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    movie_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    release_year INTEGER NOT NULL,
                    runtime INTEGER,
                    rating REAL,
                    vote_count INTEGER,
                    popularity REAL,
                    overview TEXT,
                    movie_age INTEGER,
                    rating_category TEXT,
                    popularity_bucket TEXT,
                    runtime_category TEXT,
                    era TEXT,
                    genre_count INTEGER,
                    weighted_score REAL,
                    extraction_date TEXT,
                    load_date TEXT
                )
            """)
            logger.info("Created 'movies' table")
            
            # Create genres table (normalized)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS genres (
                    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    genre_name TEXT UNIQUE NOT NULL
                )
            """)
            logger.info("Created 'genres' table")
            
            # Create movie_genres junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movie_genres (
                    movie_id TEXT,
                    genre_id INTEGER,
                    PRIMARY KEY (movie_id, genre_id),
                    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
                    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
                )
            """)
            logger.info("Created 'movie_genres' junction table")
            
            # Create ratings aggregation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ratings_summary (
                    rating_category TEXT PRIMARY KEY,
                    movie_count INTEGER,
                    avg_rating REAL,
                    avg_popularity REAL,
                    total_votes INTEGER
                )
            """)
            logger.info("Created 'ratings_summary' table")
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_release_year ON movies(release_year)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON movies(rating)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_popularity ON movies(popularity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_era ON movies(era)")
            logger.info("Created performance indexes")
            
            self.conn.commit()
            logger.info("Database schema created successfully")
            
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            raise
    
    def load_genres(self, df):
        """Load and normalize genres"""
        logger.info("Loading genres...")
        
        try:
            # Extract unique genres
            all_genres = set()
            for genres_str in df['genres'].dropna():
                genres = genres_str.split('|')
                all_genres.update(genres)
            
            # Insert genres
            cursor = self.conn.cursor()
            for genre in sorted(all_genres):
                cursor.execute(
                    "INSERT OR IGNORE INTO genres (genre_name) VALUES (?)",
                    (genre,)
                )
            
            self.conn.commit()
            logger.info(f"Loaded {len(all_genres)} unique genres")
            
        except Exception as e:
            logger.error(f"Error loading genres: {str(e)}")
            raise
    
    def load_movies(self, df):
        """Load movies data"""
        logger.info("Loading movies...")
        
        try:
            load_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor = self.conn.cursor()
            
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO movies VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (
                    row['movie_id'],
                    row['title'],
                    row['release_year'],
                    row['runtime'],
                    row['rating'],
                    row['vote_count'],
                    row['popularity'],
                    row['overview'],
                    row['movie_age'],
                    row['rating_category'],
                    str(row['popularity_bucket']),
                    row['runtime_category'],
                    row['era'],
                    row['genre_count'],
                    row['weighted_score'],
                    row['extraction_date'],
                    load_date
                ))
            
            self.conn.commit()
            logger.info(f"Loaded {len(df)} movies")
            
        except Exception as e:
            logger.error(f"Error loading movies: {str(e)}")
            raise
    
    def load_movie_genres(self, df):
        """Load movie-genre relationships"""
        logger.info("Loading movie-genre relationships...")
        
        try:
            cursor = self.conn.cursor()
            
            for _, row in df.iterrows():
                movie_id = row['movie_id']
                genres = row['genres'].split('|')
                
                for genre in genres:
                    # Get genre_id
                    cursor.execute("SELECT genre_id FROM genres WHERE genre_name = ?", (genre,))
                    genre_id = cursor.fetchone()[0]
                    
                    # Insert relationship
                    cursor.execute(
                        "INSERT OR IGNORE INTO movie_genres VALUES (?, ?)",
                        (movie_id, genre_id)
                    )
            
            self.conn.commit()
            logger.info("Movie-genre relationships loaded")
            
        except Exception as e:
            logger.error(f"Error loading movie-genre relationships: {str(e)}")
            raise
    
    def create_aggregations(self):
        """Create summary aggregations"""
        logger.info("Creating summary aggregations...")
        
        try:
            cursor = self.conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM ratings_summary")
            
            # Insert aggregated data
            cursor.execute("""
                INSERT INTO ratings_summary
                SELECT 
                    rating_category,
                    COUNT(*) as movie_count,
                    AVG(rating) as avg_rating,
                    AVG(popularity) as avg_popularity,
                    SUM(vote_count) as total_votes
                FROM movies
                GROUP BY rating_category
            """)
            
            self.conn.commit()
            logger.info("Summary aggregations created")
            
        except Exception as e:
            logger.error(f"Error creating aggregations: {str(e)}")
            raise
    
    def verify_load(self):
        """Verify data was loaded correctly"""
        logger.info("Verifying data load...")
        
        try:
            cursor = self.conn.cursor()
            
            # Count movies
            cursor.execute("SELECT COUNT(*) FROM movies")
            movie_count = cursor.fetchone()[0]
            logger.info(f"Total movies in database: {movie_count}")
            
            # Count genres
            cursor.execute("SELECT COUNT(*) FROM genres")
            genre_count = cursor.fetchone()[0]
            logger.info(f"Total genres in database: {genre_count}")
            
            # Count relationships
            cursor.execute("SELECT COUNT(*) FROM movie_genres")
            relation_count = cursor.fetchone()[0]
            logger.info(f"Total movie-genre relationships: {relation_count}")
            
            logger.info("Data verification completed")
            
        except Exception as e:
            logger.error(f"Error during verification: {str(e)}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    """Main loading workflow"""
    logger.info("=" * 80)
    logger.info("PHASE 3: DATA LOADING STARTED")
    logger.info("=" * 80)
    
    loader = None
    
    try:
        # Load processed data
        df = pd.read_csv('../data/processed/processed_movies.csv')
        logger.info(f"Loaded processed data: {len(df)} movies")
        
        # Initialize loader
        loader = MovieDatabaseLoader()
        loader.connect()
        
        # Create schema
        loader.create_schema()
        
        # Load data
        loader.load_genres(df)
        loader.load_movies(df)
        loader.load_movie_genres(df)
        
        # Create aggregations
        loader.create_aggregations()
        
        # Verify
        loader.verify_load()
        
        logger.info("Data loading completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Data loading failed: {str(e)}")
        raise
    
    finally:
        if loader:
            loader.close()


if __name__ == "__main__":
    main()
