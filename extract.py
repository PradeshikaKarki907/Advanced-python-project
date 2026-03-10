"""
Movie Data Extraction Module
Simulates TMDB API data extraction using realistic sample data
Automatically loads real scraped data if available
"""

import json
import logging
import pandas as pd
from datetime import datetime
import random
import os

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


class MovieDataExtractor:
    """Extract movie data from various sources"""
    
    def __init__(self):
        self.extraction_time = datetime.now()
        logger.info("MovieDataExtractor initialized")
    
    def generate_sample_data(self, num_movies=500):
        """
        Generate realistic sample movie data
        In production, this would call TMDB API
        """
        logger.info(f"Starting data extraction for {num_movies} movies")
        
        genres_list = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 
            'Documentary', 'Drama', 'Family', 'Fantasy', 'Horror',
            'Mystery', 'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'
        ]
        
        movie_titles = [
            'The Last Echo', 'Midnight Runner', 'Silent Storm', 'Digital Dreams',
            'Beyond the Horizon', 'Shadow Protocol', 'Crystal Empire', 'Neon City',
            'The Forgotten Path', 'Quantum Divide', 'Eternal Flame', 'Dark Waters',
            'Phoenix Rising', 'Lost in Time', 'Broken Compass', 'Steel Heart',
            'Velvet Revolution', 'Ghost in Machine', 'Sacred Ground', 'Wild Spirit',
            'Golden Hour', 'Crimson Tide', 'Silver Lining', 'Iron Will',
            'Frozen Destiny', 'Burning Sky', 'Rising Sun', 'Falling Stars',
            'Hidden Truth', 'Perfect Storm', 'Blind Faith', 'Pure Chaos',
            'Sweet Revenge', 'Bitter End', 'Final Stand', 'First Light',
            'Last Dance', 'New Dawn', 'Old Soul', 'Young Blood',
            'Ancient Wisdom', 'Modern Warfare', 'Classic Tale', 'Future Shock',
            'Past Lives', 'Present Danger', 'Tomorrow Never', 'Yesterday Once',
            'Forever After', 'Never Again', 'Always Remember', 'Sometimes Why'
        ]
        
        movies_data = []
        
        try:
            for i in range(num_movies):
                # Generate realistic movie data
                title = f"{random.choice(movie_titles)} {random.choice(['', 'Returns', 'Reloaded', 'Rising', 'Begins', '2', 'Redemption'])}"
                release_year = random.randint(1990, 2024)
                runtime = random.randint(80, 180)
                rating = round(random.uniform(4.0, 9.5), 1)
                vote_count = random.randint(100, 50000)
                popularity = round(random.uniform(1.0, 100.0), 2)
                
                # Select 1-3 genres
                num_genres = random.randint(1, 3)
                genres = random.sample(genres_list, num_genres)
                
                overview = f"A {genres[0].lower()} story set in {release_year}. This compelling narrative explores themes of adventure, drama, and human emotion."
                
                movie = {
                    'movie_id': f'TM{i+1:05d}',
                    'title': title.strip(),
                    'genres': '|'.join(genres),
                    'release_year': release_year,
                    'runtime': runtime,
                    'rating': rating,
                    'vote_count': vote_count,
                    'popularity': popularity,
                    'overview': overview,
                    'extraction_date': self.extraction_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                movies_data.append(movie)
            
            logger.info(f"Successfully extracted {len(movies_data)} movies")
            return movies_data
            
        except Exception as e:
            logger.error(f"Error during data extraction: {str(e)}")
            raise
    
    def save_raw_data(self, data, filename='raw_movies.csv'):
        """Save raw extracted data"""
        try:
            df = pd.DataFrame(data)
            filepath = f'../data/raw/{filename}'
            df.to_csv(filepath, index=False)
            logger.info(f"Raw data saved to {filepath}")
            
            # Also save as JSON
            json_filepath = filepath.replace('.csv', '.json')
            df.to_json(json_filepath, orient='records', indent=2)
            logger.info(f"Raw data also saved as JSON to {json_filepath}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error saving raw data: {str(e)}")
            raise


def main():
    """Main extraction workflow"""
    logger.info("=" * 80)
    logger.info("PHASE 1: DATA EXTRACTION STARTED")
    logger.info("=" * 80)
    
    try:
        # First, try to load real data that was scraped
        real_data_path = 'extracted_data/real_movie_data.csv'
        if os.path.exists(real_data_path):
            logger.info(f"Loading REAL movie data from: {real_data_path}")
            df = pd.read_csv(real_data_path)
            logger.info(f"✅ Loaded real data: {len(df)} movies")
        else:
            # Fallback: generate sample data
            logger.info("Real data not found. Generating sample data...")
            extractor = MovieDataExtractor()
            movies_data = extractor.generate_sample_data(num_movies=500)
            df = extractor.save_raw_data(movies_data)
            logger.info(f"✅ Generated sample data: {len(df)} movies")
        
        logger.info(f"Data extraction completed successfully!")
        logger.info(f"Total movies: {len(df)}")
        logger.info(f"Data shape: {df.shape}")
        logger.info("=" * 80)
        
        return df
        
    except Exception as e:
        logger.error(f"Data extraction failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
