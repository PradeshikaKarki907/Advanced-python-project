"""
Pipeline Automation & Scheduling
Automate ETL pipeline execution on a schedule
"""

import schedule
import time
import logging
from datetime import datetime
import sys

sys.path.append('../src')
from pipeline import ETLPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PipelineScheduler:
    """Automate and schedule pipeline execution"""
    
    def __init__(self):
        self.pipeline = ETLPipeline()
        logger.info("Pipeline Scheduler initialized")
    
    def run_scheduled_pipeline(self):
        """Run pipeline on schedule"""
        logger.info("\n" + "=" * 80)
        logger.info("SCHEDULED PIPELINE EXECUTION TRIGGERED")
        logger.info(f"Trigger Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        try:
            success = self.pipeline.run_pipeline(
                num_movies=500,
                include_eda=True
            )
            
            if success:
                logger.info("✓ Scheduled pipeline execution completed successfully")
            else:
                logger.error("✗ Scheduled pipeline execution failed")
            
        except Exception as e:
            logger.error(f"Error during scheduled execution: {str(e)}")
    
    def setup_schedule(self):
        """Configure pipeline schedule"""
        logger.info("Setting up pipeline schedule...")
        
        # Run every Monday at 2:00 AM
        schedule.every().monday.at("02:00").do(self.run_scheduled_pipeline)
        
        # Alternative schedules (commented out - uncomment as needed)
        # schedule.every().day.at("02:00").do(self.run_scheduled_pipeline)  # Daily
        # schedule.every(7).days.do(self.run_scheduled_pipeline)  # Weekly
        # schedule.every().hour.do(self.run_scheduled_pipeline)  # Hourly
        # schedule.every(30).minutes.do(self.run_scheduled_pipeline)  # Every 30 min
        
        logger.info("Schedule configured:")
        logger.info("  - Weekly execution: Every Monday at 02:00 AM")
        logger.info("\nScheduler is now running. Press Ctrl+C to stop.")
    
    def run(self):
        """Start the scheduler"""
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")


def create_cron_job():
    """Generate CRON job configuration for Linux"""
    cron_config = """
# Movie Analytics ETL Pipeline - CRON Configuration
# 
# Add this to your crontab with: crontab -e
# 
# Run every Monday at 2:00 AM
0 2 * * 1 cd /path/to/movie_analytics/src && /usr/bin/python3 pipeline.py >> /path/to/movie_analytics/data/logs/cron.log 2>&1
# 
# Run every day at 2:00 AM
# 0 2 * * * cd /path/to/movie_analytics/src && /usr/bin/python3 pipeline.py >> /path/to/movie_analytics/data/logs/cron.log 2>&1
# 
# Run every Sunday at midnight
# 0 0 * * 0 cd /path/to/movie_analytics/src && /usr/bin/python3 pipeline.py >> /path/to/movie_analytics/data/logs/cron.log 2>&1
"""
    
    with open('../scheduler_cron.txt', 'w') as f:
        f.write(cron_config)
    
    logger.info("CRON configuration saved to scheduler_cron.txt")
    logger.info("To use: crontab -e and add the appropriate line")


def main():
    """Main scheduler execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Movie Analytics Pipeline Scheduler')
    parser.add_argument(
        '--mode',
        choices=['schedule', 'run-once', 'cron-config'],
        default='run-once',
        help='Scheduler mode'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'schedule':
        # Run with Python schedule library
        scheduler = PipelineScheduler()
        scheduler.run()
        
    elif args.mode == 'run-once':
        # Run pipeline once immediately
        logger.info("Running pipeline once (immediate execution)")
        scheduler = PipelineScheduler()
        scheduler.run_scheduled_pipeline()
        
    elif args.mode == 'cron-config':
        # Generate CRON configuration
        create_cron_job()
        logger.info("CRON configuration generated")


if __name__ == "__main__":
    main()
