import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

from scraper import MovieDataScraper  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "extracted_data" / "scrape.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("scheduled_scrape")

TASK_NAME = "MovieDataScraper_Daily"
CSV_FILE = "real_movie_data.csv"


def run_scrape():
    """Execute a scrape job: recent years + popular + top-rated → merge & save."""
    log.info("=" * 60)
    log.info("Scheduled scrape started")
    start = datetime.now()

    scraper = MovieDataScraper()

    current_year = datetime.now().year

    # Fetch recent 2 years (likely to have new releases)
    df_recent = scraper.tmdb.discover_movies(
        start_year=current_year - 1,
        end_year=current_year,
        pages_per_decade=10,
        min_votes=50,
    )

    # Also grab current popular & top-rated for freshness
    df_pop = scraper.tmdb.search_popular_movies(num_pages=5)
    df_top = scraper.tmdb.search_top_rated_movies(num_pages=5)
    df_now = scraper.tmdb.search_now_playing(num_pages=3)

    import pandas as pd
    combined = pd.concat([df_recent, df_pop, df_top, df_now], ignore_index=True)
    combined.drop_duplicates(subset="movie_id", keep="first", inplace=True)

    log.info(f"Fetched {len(combined)} movies in this run")

    # save_scraped_data merges with existing CSV automatically
    path = scraper.save_scraped_data(combined, filename=CSV_FILE)

    elapsed = (datetime.now() - start).total_seconds()
    log.info(f"Scrape complete in {elapsed:.1f}s → {path}")
    log.info("=" * 60)


def install_task():
    """Register a Windows Task Scheduler job to run this script daily at 03:00."""
    python_exe = sys.executable
    script_path = str(Path(__file__).resolve())

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{python_exe}" "{script_path}"',
        "/SC", "DAILY",
        "/ST", "03:00",
        "/F",  # force overwrite if exists
    ]

    log.info(f"Creating scheduled task: {TASK_NAME}")
    log.info(f"  Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log.info(f"Task '{TASK_NAME}' created successfully (daily at 03:00)")
        log.info("  View it:   schtasks /Query /TN MovieDataScraper_Daily")
        log.info("  Run now:   schtasks /Run   /TN MovieDataScraper_Daily")
        log.info("  Delete it: python scheduled_scrape.py --uninstall")
    else:
        log.error(f"Failed to create task: {result.stderr.strip()}")
        log.info("You may need to run this as Administrator.")


def uninstall_task():
    """Remove the scheduled task."""
    cmd = ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log.info(f"Task '{TASK_NAME}' removed.")
    else:
        log.error(f"Failed to remove task: {result.stderr.strip()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduled movie data scraper")
    parser.add_argument("--install", action="store_true", help="Register Windows Scheduled Task (daily 03:00)")
    parser.add_argument("--uninstall", action="store_true", help="Remove Windows Scheduled Task")
    args = parser.parse_args()

    if args.install:
        install_task()
    elif args.uninstall:
        uninstall_task()
    else:
        run_scrape()
