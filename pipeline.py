"""
Master ETL Pipeline Orchestrator
Coordinates all phases of the movie analytics pipeline
"""

import sys
import logging
from datetime import datetime
import time

# Add src directory to path
sys.path.append('../src')

from extract import MovieDataExtractor
from transform import MovieDataTransformer
from load import MovieDatabaseLoader

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


class ETLPipeline:
    """Orchestrate complete ETL pipeline"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        logger.info("ETL Pipeline initialized")
    
    def log_phase_start(self, phase_name):
        """Log start of pipeline phase"""
        logger.info("=" * 80)
        logger.info(f"{phase_name} - STARTED")
        logger.info("=" * 80)
    
    def log_phase_end(self, phase_name, success=True):
        """Log end of pipeline phase"""
        status = "COMPLETED SUCCESSFULLY" if success else "FAILED"
        logger.info("=" * 80)
        logger.info(f"{phase_name} - {status}")
        logger.info("=" * 80)
    
    def extract_phase(self, num_movies=500):
        """Execute extraction phase"""
        self.log_phase_start("PHASE 1: EXTRACTION")
        
        try:
            extractor = MovieDataExtractor()
            movies_data = extractor.generate_sample_data(num_movies=num_movies)
            df = extractor.save_raw_data(movies_data)
            
            self.log_phase_end("PHASE 1: EXTRACTION", success=True)
            return df
            
        except Exception as e:
            logger.error(f"Extraction phase failed: {str(e)}")
            self.log_phase_end("PHASE 1: EXTRACTION", success=False)
            raise
    
    def transform_phase(self):
        """Execute transformation phase"""
        self.log_phase_start("PHASE 2: TRANSFORMATION")
        
        try:
            transformer = MovieDataTransformer()
            df_raw = transformer.load_raw_data()
            df_processed = transformer.transform(df_raw)
            transformer.save_processed_data(df_processed)
            
            self.log_phase_end("PHASE 2: TRANSFORMATION", success=True)
            return df_processed
            
        except Exception as e:
            logger.error(f"Transformation phase failed: {str(e)}")
            self.log_phase_end("PHASE 2: TRANSFORMATION", success=False)
            raise
    
    def load_phase(self):
        """Execute loading phase"""
        self.log_phase_start("PHASE 3: LOADING")
        
        loader = None
        
        try:
            import pandas as pd
            df = pd.read_csv('../data/processed/processed_movies.csv')
            
            loader = MovieDatabaseLoader()
            loader.connect()
            loader.create_schema()
            loader.load_genres(df)
            loader.load_movies(df)
            loader.load_movie_genres(df)
            loader.create_aggregations()
            loader.verify_load()
            
            self.log_phase_end("PHASE 3: LOADING", success=True)
            
        except Exception as e:
            logger.error(f"Loading phase failed: {str(e)}")
            self.log_phase_end("PHASE 3: LOADING", success=False)
            raise
        
        finally:
            if loader:
                loader.close()
    
    def run_eda(self):
        """Execute EDA phase"""
        self.log_phase_start("PHASE 4: EDA")
        
        try:
            # Import and run EDA
            from eda import MovieEDA
            
            eda = MovieEDA()
            eda.load_data()
            eda.basic_statistics()
            eda.plot_movies_per_year()
            eda.plot_genre_distribution()
            eda.plot_rating_distribution()
            eda.plot_popularity_vs_rating()
            eda.plot_runtime_analysis()
            eda.plot_top_movies()
            eda.plot_era_analysis()
            eda.generate_report()
            
            self.log_phase_end("PHASE 4: EDA", success=True)
            
        except Exception as e:
            logger.error(f"EDA phase failed: {str(e)}")
            self.log_phase_end("PHASE 4: EDA", success=False)
            raise
    
    def run_pipeline(self, num_movies=500, include_eda=True):
        """Run complete ETL pipeline"""
        self.start_time = time.time()
        
        logger.info("\n" + "=" * 80)
        logger.info("MOVIE ANALYTICS ETL PIPELINE - EXECUTION STARTED")
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80 + "\n")
        
        try:
            # Phase 1: Extract
            self.extract_phase(num_movies=num_movies)
            
            # Phase 2: Transform
            self.transform_phase()
            
            # Phase 3: Load
            self.load_phase()
            
            # Phase 4: EDA (optional)
            if include_eda:
                self.run_eda()
            
            self.end_time = time.time()
            duration = self.end_time - self.start_time
            
            logger.info("\n" + "=" * 80)
            logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
            logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Total Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            logger.info("=" * 80 + "\n")
            
            self.generate_summary_report(duration)
            
            return True
            
        except Exception as e:
            self.end_time = time.time()
            duration = self.end_time - self.start_time if self.start_time else 0
            
            logger.error("\n" + "=" * 80)
            logger.error("PIPELINE EXECUTION FAILED!")
            logger.error(f"Error: {str(e)}")
            logger.error(f"Duration before failure: {duration:.2f} seconds")
            logger.error("=" * 80 + "\n")
            
            return False
    
    def generate_summary_report(self, duration):
        """Generate pipeline execution summary"""
        report_path = '../data/logs/pipeline_summary.txt'
        
        try:
            import pandas as pd
            df = pd.read_csv('../data/processed/processed_movies.csv')
            
            with open(report_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("ETL PIPELINE EXECUTION SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)\n\n")
                
                f.write("PIPELINE PHASES:\n")
                f.write("  ✓ Phase 1: Data Extraction\n")
                f.write("  ✓ Phase 2: Data Transformation\n")
                f.write("  ✓ Phase 3: Data Loading\n")
                f.write("  ✓ Phase 4: Exploratory Data Analysis\n\n")
                
                f.write("DATA SUMMARY:\n")
                f.write(f"  Total Movies Processed: {len(df):,}\n")
                f.write(f"  Total Features: {df.shape[1]}\n")
                f.write(f"  Data Quality: {((1 - df.isnull().sum().sum() / df.size) * 100):.2f}% complete\n\n")
                
                f.write("OUTPUT FILES:\n")
                f.write("  - Raw Data: data/raw/raw_movies.csv\n")
                f.write("  - Processed Data: data/processed/processed_movies.csv\n")
                f.write("  - Database: database/movies.db\n")
                f.write("  - Visualizations: visualizations/*.png\n")
                f.write("  - EDA Report: visualizations/eda_report.txt\n")
                f.write("  - Logs: data/logs/pipeline.log\n\n")
                
                f.write("NEXT STEPS:\n")
                f.write("  1. Review EDA visualizations\n")
                f.write("  2. Launch dashboard: streamlit run dashboard/app.py\n")
                f.write("  3. Query database for custom analysis\n")
                f.write("  4. Schedule automated runs\n\n")
                
                f.write("=" * 80 + "\n")
            
            logger.info(f"Pipeline summary saved to {report_path}")
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")


def main():
    """Main pipeline execution"""
    pipeline = ETLPipeline()
    
    # Run complete pipeline
    success = pipeline.run_pipeline(
        num_movies=500,  # Number of movies to extract
        include_eda=True  # Include EDA phase
    )
    
    if success:
        logger.info("✓ Pipeline completed successfully!")
        logger.info("To view the dashboard, run: streamlit run dashboard/app.py")
    else:
        logger.error("✗ Pipeline failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
