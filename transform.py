"""
Movie Data Transformation Module
Handles data cleaning, preprocessing, and feature engineering
"""

import pandas as pd
import numpy as np
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


class MovieDataTransformer:
    """Transform and clean movie data"""
    
    def __init__(self):
        logger.info("MovieDataTransformer initialized")
        self.current_year = datetime.now().year
    
    def load_raw_data(self, filepath='../data/raw/raw_movies.csv'):
        """Load raw data from extraction phase"""
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded raw data: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading raw data: {str(e)}")
            raise
    
    def handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        logger.info("Handling missing values...")
        
        initial_nulls = df.isnull().sum().sum()
        logger.info(f"Total missing values before cleaning: {initial_nulls}")
        
        # Fill missing ratings with median
        if df['rating'].isnull().any():
            median_rating = df['rating'].median()
            df['rating'].fillna(median_rating, inplace=True)
            logger.info(f"Filled missing ratings with median: {median_rating}")
        
        # Fill missing vote_count with 0
        if df['vote_count'].isnull().any():
            df['vote_count'].fillna(0, inplace=True)
            logger.info("Filled missing vote_count with 0")
        
        # Drop rows with missing essential fields
        essential_cols = ['title', 'release_year']
        df.dropna(subset=essential_cols, inplace=True)
        
        final_nulls = df.isnull().sum().sum()
        logger.info(f"Total missing values after cleaning: {final_nulls}")
        
        return df
    
    def remove_duplicates(self, df):
        """Remove duplicate movie entries"""
        logger.info("Removing duplicates...")
        
        initial_count = len(df)
        df.drop_duplicates(subset=['title', 'release_year'], keep='first', inplace=True)
        
        removed_count = initial_count - len(df)
        logger.info(f"Removed {removed_count} duplicate entries")
        
        return df
    
    def normalize_data(self, df):
        """Normalize and standardize data fields"""
        logger.info("Normalizing data fields...")
        
        # Ensure proper data types
        df['release_year'] = df['release_year'].astype(int)
        df['runtime'] = df['runtime'].astype(int)
        df['rating'] = df['rating'].astype(float)
        df['vote_count'] = df['vote_count'].astype(int)
        df['popularity'] = df['popularity'].astype(float)
        
        # Normalize genres (ensure consistent formatting)
        df['genres'] = df['genres'].str.strip()
        
        # Clean titles
        df['title'] = df['title'].str.strip()
        
        logger.info("Data normalization completed")
        
        return df
    
    def feature_engineering(self, df):
        """Create new features from existing data"""
        logger.info("Performing feature engineering...")
        
        # Movie age
        df['movie_age'] = self.current_year - df['release_year']
        logger.info("Created 'movie_age' feature")
        
        # Rating category
        def categorize_rating(rating):
            if rating >= 8.0:
                return 'Excellent'
            elif rating >= 7.0:
                return 'Good'
            elif rating >= 6.0:
                return 'Average'
            else:
                return 'Poor'
        
        df['rating_category'] = df['rating'].apply(categorize_rating)
        logger.info("Created 'rating_category' feature")
        
        # Popularity buckets
        df['popularity_bucket'] = pd.cut(
            df['popularity'],
            bins=[0, 20, 50, 80, 100],
            labels=['Low', 'Medium', 'High', 'Very High'],
            include_lowest=True
        )
        logger.info("Created 'popularity_bucket' feature")
        
        # Runtime category
        def categorize_runtime(runtime):
            if runtime < 90:
                return 'Short'
            elif runtime < 120:
                return 'Medium'
            else:
                return 'Long'
        
        df['runtime_category'] = df['runtime'].apply(categorize_runtime)
        logger.info("Created 'runtime_category' feature")
        
        # Era classification
        def classify_era(year):
            if year >= 2020:
                return '2020s'
            elif year >= 2010:
                return '2010s'
            elif year >= 2000:
                return '2000s'
            else:
                return 'Pre-2000'
        
        df['era'] = df['release_year'].apply(classify_era)
        logger.info("Created 'era' feature")
        
        # Genre count
        df['genre_count'] = df['genres'].str.split('|').str.len()
        logger.info("Created 'genre_count' feature")
        
        # Weighted score (combines rating and vote count)
        min_votes = df['vote_count'].quantile(0.25)
        mean_rating = df['rating'].mean()
        
        def weighted_rating(row):
            v = row['vote_count']
            R = row['rating']
            return (v / (v + min_votes) * R) + (min_votes / (v + min_votes) * mean_rating)
        
        df['weighted_score'] = df.apply(weighted_rating, axis=1)
        logger.info("Created 'weighted_score' feature")
        
        return df
    
    def save_processed_data(self, df, filename='processed_movies.csv'):
        """Save processed data"""
        try:
            filepath = f'../data/processed/{filename}'
            df.to_csv(filepath, index=False)
            logger.info(f"Processed data saved to {filepath}")
            
            # Save summary statistics
            summary_path = '../data/processed/data_summary.txt'
            with open(summary_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("PROCESSED DATA SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Total Movies: {len(df)}\n")
                f.write(f"Columns: {', '.join(df.columns)}\n\n")
                f.write("Data Types:\n")
                f.write(str(df.dtypes) + "\n\n")
                f.write("Statistical Summary:\n")
                f.write(str(df.describe()) + "\n\n")
                f.write("Missing Values:\n")
                f.write(str(df.isnull().sum()) + "\n")
            
            logger.info(f"Data summary saved to {summary_path}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error saving processed data: {str(e)}")
            raise
    
    def transform(self, df):
        """Execute complete transformation pipeline"""
        logger.info("Starting transformation pipeline...")
        
        # Data cleaning
        df = self.handle_missing_values(df)
        df = self.remove_duplicates(df)
        df = self.normalize_data(df)
        
        # Feature engineering
        df = self.feature_engineering(df)
        
        logger.info("Transformation pipeline completed")
        
        return df


def main():
    """Main transformation workflow"""
    logger.info("=" * 80)
    logger.info("PHASE 2: DATA TRANSFORMATION STARTED")
    logger.info("=" * 80)
    
    try:
        transformer = MovieDataTransformer()
        
        # Load raw data
        df = transformer.load_raw_data()
        
        # Transform data
        df_processed = transformer.transform(df)
        
        # Save processed data
        transformer.save_processed_data(df_processed)
        
        logger.info(f"Data transformation completed successfully!")
        logger.info(f"Processed data shape: {df_processed.shape}")
        logger.info("=" * 80)
        
        return df_processed
        
    except Exception as e:
        logger.error(f"Data transformation failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
