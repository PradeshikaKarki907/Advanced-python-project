"""
Quick Start Script: Scrape Real Data and Load Dashboard
Complete end-to-end workflow in one script
"""

import pandas as pd
import logging
from scraper import MovieDataScraper
from flexible_load_integration import UniversalMovieExtractor
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_and_load_data(source='auto', num_movies=100, save_intermediate=True):
    """
    Complete workflow: Scrape → Standardize → Save → Ready for pipeline
    
    Parameters:
    -----------
    source : str
        'auto' (TMDB→Wikipedia), 'tmdb', or 'wikipedia'
    num_movies : int
        Approximate number of movies to scrape
    save_intermediate : bool
        Save intermediate files for inspection
    
    Returns:
    --------
    str
        Path to final standardized CSV file
    """
    
    print("\n" + "="*80)
    print("🎬 MOVIE DATA SCRAPER & LOADER")
    print("="*80)
    
    # Step 1: Scrape
    print(f"\n📥 Step 1: Scraping {num_movies} movies from {source.upper()}...")
    scraper = MovieDataScraper()
    df_scraped = scraper.scrape_real_data(source=source, num_movies=num_movies)
    
    if len(df_scraped) == 0:
        print("❌ Failed to scrape data!")
        print("   Try installing: pip install requests beautifulsoup4")
        return None
    
    print(f"✅ Scraped {len(df_scraped)} movies")
    print(f"   Columns: {', '.join(df_scraped.columns)}")
    
    if save_intermediate:
        scraper.save_scraped_data(df_scraped, 'scraped_raw.csv')
        print(f"   Saved raw data to: extracted_data/scraped_raw.csv")
    
    # Step 2: Standardize with Flexible Loader
    print(f"\n🔄 Step 2: Standardizing column names...")
    extractor = UniversalMovieExtractor(data_source='csv')
    
    # For scraped data, use auto-detection
    if save_intermediate:
        scraper.save_scraped_data(df_scraped, 'scraped_raw.csv')
        df_standardized = extractor.extract_data(
            filepath='extracted_data/scraped_raw.csv'
        )
    else:
        # Skip file and load directly
        from flexible_loader import FlexibleDataLoader
        loader = FlexibleDataLoader()
        mapping = loader._get_column_mapping(df_scraped, 'tmdb')
        df_standardized = loader._apply_mapping(df_scraped, mapping)
        df_standardized = loader._validate_and_clean(df_standardized)
    
    print(f"✅ Standardized {len(df_standardized)} movies")
    print(f"   Final columns: {', '.join(df_standardized.columns)}")
    
    # Step 3: Save final data
    print(f"\n💾 Step 3: Saving standardized data...")
    final_path = extractor.save_data(df_standardized, 'real_movie_data.csv')
    print(f"✅ Saved to: {final_path}")
    
    # Step 4: Show summary
    print(f"\n📊 Step 4: Data Summary")
    print(f"   Total movies: {len(df_standardized)}")
    print(f"   Years: {int(df_standardized['release_year'].min())} - {int(df_standardized['release_year'].max())}")
    print(f"   Rating range: {df_standardized['rating'].min():.1f} - {df_standardized['rating'].max():.1f}")
    
    print(f"\n" + "="*80)
    print("✅ READY TO USE!")
    print("="*80)
    print("""
Next steps:

1. UPDATE extract.py:
   ─────────────────
   Open extract.py and replace the main() function with:
   
   def main():
       df = pd.read_csv('extracted_data/real_movie_data.csv')
       return df

2. RUN PIPELINE:
   ─────────────
   python pipeline.py

3. LAUNCH DASHBOARD:
   ──────────────────
   python -m streamlit run app.py

Your dashboard will now display REAL movie data! 🎬
    """)
    
    return final_path


if __name__ == "__main__":
    # ========================================================================
    # QUICK START OPTIONS
    # ========================================================================
    
    # Option 1: Scrape from Wikipedia (easiest, no API key, ~50 movies)
    print("\n🌐 Scraping from Wikipedia (no API key needed)...")
    scrape_and_load_data(source='wikipedia', num_movies=50)
    
    
    # Option 2: Scrape from TMDB (requires free API key, better data)
    # Uncomment below and add your TMDB API key to tmdb_api_key.txt
    # print("\n🌐 Scraping from TMDB...")
    # scrape_and_load_data(source='tmdb', num_movies=100)
    
    
    # Option 3: Auto-detect best source
    # Uncomment below
    # print("\n🌐 Auto-detecting best source...")
    # scrape_and_load_data(source='auto', num_movies=100)
