"""
Integration of Flexible Loader into the Extract Pipeline
Shows how to use flexible_loader.py with the existing pipeline
"""

import pandas as pd
import logging
from flexible_loader import FlexibleDataLoader
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UniversalMovieExtractor:
    """
    Unified extractor that supports both generated sample data and
    real data from multiple sources (TMDB, IMDb, Rotten Tomatoes, etc.)
    """
    
    def __init__(self, data_source='sample'):
        """
        Parameters:
        -----------
        data_source : str
            'sample' - generate sample data (default)
            'csv' - load from CSV file
            'json' - load from JSON file
            'imdb', 'tmdb', 'movielens', etc. - specific source type
        """
        self.data_source = data_source
        self.extraction_time = datetime.now()
        self.loader = FlexibleDataLoader()
        logger.info(f"UniversalMovieExtractor initialized with source: {data_source}")
    
    def extract_data(self, filepath=None, num_movies=500, 
                    source_type=None, custom_mapping=None):
        """
        Extract data from various sources.
        
        Parameters:
        -----------
        filepath : str
            Path to data file (if loading from real source)
        num_movies : int
            Number of movies to generate (if source='sample')
        source_type : str
            Specific source type for auto-detection ('imdb', 'tmdb', etc.)
        custom_mapping : dict
            Custom column mapping {original: standard}
        
        Returns:
        --------
        pd.DataFrame
            Standardized movie data
        """
        
        if self.data_source == 'sample':
            logger.info("Extracting sample data...")
            return self._generate_sample_data(num_movies)
        
        elif self.data_source in ['csv', 'json'] and filepath:
            logger.info(f"Loading data from {filepath}...")
            return self.loader.load_and_map(
                filepath, 
                source=source_type, 
                custom_mapping=custom_mapping
            )
        
        else:
            raise ValueError(f"Invalid data_source: {self.data_source}")
    
    def _generate_sample_data(self, num_movies=500):
        """Generate realistic sample data (existing functionality)"""
        import random
        
        genres_list = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 
            'Documentary', 'Drama', 'Family', 'Fantasy', 'Horror',
            'Mystery', 'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'
        ]
        
        movie_titles = [
            'The Last Echo', 'Midnight Runner', 'Silent Storm', 'Digital Dreams',
            'Beyond the Horizon', 'Shadow Protocol', 'Crystal Empire', 'Neon City',
            'The Forgotten Path', 'Quantum Divide', 'Eternal Flame', 'Dark Waters',
            'Phoenix Rising', 'Lost in Time', 'Broken Compass', 'Steel Heart'
        ]
        
        movies_data = []
        for i in range(num_movies):
            title = f"{random.choice(movie_titles)} {random.choice(['', 'Returns', 'Reloaded', 'Rising'])}"
            release_year = random.randint(1990, 2024)
            runtime = random.randint(80, 180)
            rating = round(random.uniform(4.0, 9.5), 1)
            vote_count = random.randint(100, 50000)
            popularity = round(random.uniform(1.0, 100.0), 2)
            
            num_genres = random.randint(1, 3)
            genres = random.sample(genres_list, num_genres)
            
            movie = {
                'movie_id': f'TM{i+1:05d}',
                'title': title.strip(),
                'genres': '|'.join(genres),
                'release_year': release_year,
                'runtime': runtime,
                'rating': rating,
                'vote_count': vote_count,
                'popularity': popularity,
                'overview': f"A {genres[0].lower()} story set in {release_year}.",
            }
            movies_data.append(movie)
        
        df = pd.DataFrame(movies_data)
        logger.info(f"Generated {len(df)} sample movies")
        return df
    
    def save_data(self, df, filename='extracted_movies.csv'):
        """Save extracted data to CSV"""
        try:
            filepath = f'extracted_data/{filename}'
            os.makedirs('extracted_data', exist_ok=True)
            df.to_csv(filepath, index=False)
            logger.info(f"Data saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

def example_1_sample_data():
    """Generate sample data (default behavior)"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Generate Sample Data")
    print("="*80)
    
    extractor = UniversalMovieExtractor(data_source='sample')
    df = extractor.extract_data(num_movies=100)
    
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 rows:")
    print(df.head())


def example_2_load_csv_imdb():
    """Load and map IMDb CSV data"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Load IMDb CSV with Auto-Detection")
    print("="*80)
    
    # First, preview the mapping
    loader = FlexibleDataLoader()
    # loader.show_mapping_report('imdb_title_basics.tsv', source='imdb')
    print("(Uncomment show_mapping_report above with your actual IMDb file)")
    
    # Then load
    try:
        extractor = UniversalMovieExtractor(data_source='csv')
        # df = extractor.extract_data(filepath='imdb_title_basics.tsv', source_type='imdb')
        print("(Data would be loaded here with your actual IMDb file)")
    except Exception as e:
        print(f"Error: {e}")


def example_3_load_csv_auto_detect():
    """Load CSV from unknown source with auto-detection"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Load CSV with Auto-Detection")
    print("="*80)
    
    try:
        extractor = UniversalMovieExtractor(data_source='csv')
        # df = extractor.extract_data(filepath='mystery_movies.csv')
        print("(Data would be auto-detected and loaded with your file)")
    except Exception as e:
        print(f"Error: {e}")


def example_4_custom_mapping():
    """Load CSV with custom column mapping"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Load CSV with Custom Mapping")
    print("="*80)
    
    custom_map = {
        'Film Name': 'title',
        'Release Year': 'release_year',
        'IMDB Score': 'rating',
        'Genre': 'genres',
        'Runtime Min': 'runtime',
        'Votes': 'vote_count',
        'Movie ID': 'movie_id'
    }
    
    try:
        extractor = UniversalMovieExtractor(data_source='csv')
        # df = extractor.extract_data(filepath='my_movies.csv', custom_mapping=custom_map)
        print("(Data would be loaded here with custom mapping)")
    except Exception as e:
        print(f"Error: {e}")


def example_5_production_workflow():
    """Complete production workflow: Load real data → Transform → Load → Dashboard"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Production Workflow with Real Data")
    print("="*80)
    
    print("""
    Step 1: Load your data from any source
    ======================================
    
    from flexible_load_integration import UniversalMovieExtractor
    
    # Load IMDb data
    extractor = UniversalMovieExtractor(data_source='csv')
    df = extractor.extract_data(filepath='imdb_titles.csv', source_type='imdb')
    
    # Or load from unknown source with auto-detection
    df = extractor.extract_data(filepath='my_movies.csv')
    
    # Or load with custom mapping
    custom_map = {'name': 'title', 'year': 'release_year', ...}
    df = extractor.extract_data(filepath='custom.csv', custom_mapping=custom_map)
    
    
    Step 2: Save standardized data
    ==============================
    
    extractor.save_data(df, filename='standardized_movies.csv')
    
    
    Step 3: Run through existing pipeline
    =====================================
    
    # Modify extract.py to load from the standardized CSV
    # Then run: python pipeline.py
    # The dashboard will work with your data!
    """)


# ==============================================================================
# INTEGRATION GUIDE
# ==============================================================================

INTEGRATION_GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║           INTEGRATION WITH EXISTING PIPELINE                              ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: PREPARE YOUR DATA FILE
──────────────────────────────
Place your movie data file (CSV or JSON) in project directory:
  - my_movies.csv
  - imdb_data.csv
  - rotten_tomatoes.json
  - Any format from TMDB, IMDb, MovieLens, etc.


STEP 2: LOAD AND STANDARDIZE
─────────────────────────────
Run one of these (create a script or use interactive Python):

    from flexible_load_integration import UniversalMovieExtractor
    
    extractor = UniversalMovieExtractor(data_source='csv')
    df = extractor.extract_data(filepath='your_data.csv')
    extractor.save_data(df, filename='standardized_movies.csv')


STEP 3: PREVIEW MAPPING (OPTIONAL BUT RECOMMENDED)
───────────────────────────────────────────────────
Before committing, verify the column detection:

    from flexible_loader import FlexibleDataLoader
    loader = FlexibleDataLoader()
    loader.show_mapping_report('your_data.csv')


STEP 4: MODIFY extract.py
──────────────────────────
Edit extract.py to load your standardized CSV:

    def main():
        df = pd.read_csv('extracted_data/standardized_movies.csv')
        return df


STEP 5: RUN PIPELINE
────────────────────
    python pipeline.py

This will:
  1. Load your data (already standardized)
  2. Transform it (cleaning, feature engineering)
  3. Load to database
  4. Generate EDA
  5. Dashboard works with your data!


SUPPORTED SOURCES
──────────────────
✓ TMDB (The Movie Database)
✓ IMDb (Internet Movie Database)
✓ MovieLens (GroupLens datasets)
✓ Rotten Tomatoes
✓ Letterboxd
✓ Kaggle movie datasets
✓ Custom/Unknown sources (auto-detected)


TROUBLESHOOTING
────────────────
1. Missing columns?
   → Use show_mapping_report() to see what was detected
   → Provide custom_mapping parameter

2. Wrong source detection?
   → Explicitly set source_type parameter:
     df = extractor.extract_data(filepath='file.csv', source_type='imdb')

3. Data quality issues?
   → Loader automatically handles:
     • Missing values (filled with median/0)
     • Duplicates (removed)
     • Type conversion (numeric columns)
     • Genre formatting (pipe-separated)
"""

if __name__ == "__main__":
    print(INTEGRATION_GUIDE)
    
    print("\n\nRunning examples...\n")
    example_1_sample_data()
    example_2_load_csv_imdb()
    example_3_load_csv_auto_detect()
    example_4_custom_mapping()
    example_5_production_workflow()
