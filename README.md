# Movie Analytics Dashboard

An end-to-end data engineering and analysis project featuring a complete ETL pipeline, live web scraping, exploratory data analysis, and an interactive Streamlit dashboard for movie data insights.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Pipeline](#data-pipeline)
- [Dashboard](#dashboard)
- [Dataset](#dataset)
- [Key Insights](#key-insights)

---

## Overview

This project demonstrates a professional-grade data pipeline that:

- **Extracts** movie data from multiple live sources (Wikipedia, TMDB API)
- **Transforms** raw data through cleaning, validation, and feature engineering
- **Loads** normalized data into an SQLite database with a proper relational schema
- **Analyzes** data through exploratory data analysis and statistical methods
- **Visualizes** insights via an interactive Streamlit dashboard with real-time filtering

**Dataset**: 3,500+ movies spanning 1990–2026 with 16+ genres, sourced from the TMDB API.

---

## Features

### Data Pipeline
- Multi-source data extraction with automatic fallback (TMDB -> Wikipedia -> embedded data)
- Year-by-year TMDB Discover queries for balanced temporal coverage
- Comprehensive data cleaning and validation
- Feature engineering (6 derived columns)
- Normalized SQLite database (4 tables with indexes)
- Rate-limited API access compliant with TMDB free-tier limits
- Scheduled daily scraping via Windows Task Scheduler

### Interactive Dashboard
- **6 Analysis Tabs**: Overview, Trends, Genres, Top Movies, Relationships, Insights
- **Browse Movies** page with TMDB poster images, search, and pagination
- **Dynamic Filtering**: Year range, genres, ratings, era, rating categories
- **15+ Visualizations**: Histograms, scatter plots, bar charts, heatmaps, trend lines
- **Insight Reports**: Auto-generated analysis with IQR-based outlier detection, downloadable as .txt
- **KPI Bar**: Total movies, average rating, average popularity, total votes, unique genres

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.13 |
| **Data Processing** | pandas, numpy |
| **Database** | SQLite 3 |
| **Visualization** | matplotlib, seaborn, plotly |
| **Web Framework** | Streamlit |
| **Web Scraping** | requests, BeautifulSoup4 |
| **API** | TMDB REST API v3 (Bearer token auth) |
| **Automation** | Windows Task Scheduler |

---

## Project Structure

```
Advanced-python-project/
│
├── app.py                       # Streamlit dashboard (main UI)
├── pipeline.py                  # ETL pipeline orchestrator
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── PROJECT_REPORT.txt           # Comprehensive project report
│
├── extraction/                  # Extraction package
│   ├── __init__.py
│   ├── scraper.py               # Live web scraper (Wikipedia + TMDB)
│   ├── extract.py               # Data extraction module
│   └── scheduled_scrape.py      # Automated daily scrape utility
│
├── transformation/              # Transformation package
│   ├── __init__.py
│   └── transform.py             # Data cleaning & feature engineering
│
├── loading/                     # Loading package
│   ├── __init__.py
│   └── load.py                  # SQLite database loader
│
├── analysis/                    # Analysis package
│   ├── __init__.py
│   ├── eda.py                   # EDA & batch visualization
│   └── insights_report.py       # Standalone report generator
│
├── extracted_data/
│   └── real_movie_data.csv      # Primary dataset (3,500+ movies)
│
└── img/                         # EDA output images
    ├── era_analysis.png
    ├── genre_distribution.png
    ├── movies_per_year.png
    ├── popularity_vs_rating.png
    ├── rating_distribution.png
    └── top_movies.png
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd Advanced-python-project

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
requests==2.31.0
pandas==2.1.4
numpy==1.26.2
matplotlib==3.8.2
seaborn==0.13.0
streamlit==1.29.0
plotly==5.18.0
beautifulsoup4 (via requests)
sqlite3 (built-in)
```

---

## Usage

### Launch the Dashboard
```bash
python -m streamlit run app.py
```
Opens at `http://localhost:8501`.

### Run the ETL Pipeline
```bash
python pipeline.py
```

### Scrape Fresh Data
```python
from extraction.scraper import MovieDataScraper

scraper = MovieDataScraper()
df = scraper.scrape_all_eras()
scraper.save_scraped_data(df, 'real_movie_data.csv')
```

### Schedule Daily Scrapes
```bash
# Register a daily task at 03:00 AM
python extraction/scheduled_scrape.py --install

# Remove the scheduled task
python extraction/scheduled_scrape.py --uninstall
```

---

## Data Pipeline

### Phase 1: Extraction
- **Sources**: TMDB REST API (primary), Wikipedia HTML tables (fallback)
- **Method**: Year-by-year `/discover/movie` queries from 1990 to present
- **Rate Limiting**: 0.3s between requests (TMDB free-tier compliant)
- **Output**: `extracted_data/real_movie_data.csv`

### Phase 2: Transformation
- **Cleaning**: Handle missing values, remove duplicates, normalize types
- **Feature Engineering**:
  - `movie_age` — Years since release
  - `rating_category` — Excellent / Good / Average / Poor
  - `popularity_bucket` — Low / Medium / High / Very High
  - `era` — Decade label (1990s, 2000s, 2010s, 2020s)
  - `genre_count` — Number of genres per movie
  - `weighted_score` — Composite metric (50% rating + 30% votes + 20% popularity)

### Phase 3: Loading
- **Database**: SQLite with normalized schema (3NF)
- **Tables**: `movies`, `genres`, `movie_genres` (junction), `ratings_summary` (aggregation)
- **Indexes**: On release_year, rating, popularity, era

### Phase 4: Analysis
- Batch EDA with publication-quality PNG visualizations
- Statistical summaries and correlation analysis
- IQR-based outlier detection

---

## Dashboard

### Pages

**Dashboard** — Main analytics view with 6 tabs:

| Tab | Content |
|-----|---------|
| Overview | Rating distribution, vote count histogram, era bar chart, popularity buckets |
| Trends | Movies per year, movie age vs rating scatter, average rating trend line |
| Genres | Genre frequency, top genres by rating, rating category distribution |
| Top Movies | Top 20 by weighted score, highest rated, most popular |
| Relationships | Popularity vs rating scatter, correlation heatmap, statistical summary |
| Insights | Auto-generated report with outlier analysis, downloadable as .txt |

**Browse Movies** — Card-based movie browser with TMDB poster images, search, genre filters, sort options, and pagination (12 per page).

### Sidebar Filters
- Year range slider
- Genre multi-select
- Minimum rating slider
- Rating category checkboxes
- Era selection checkboxes

---

## Dataset

The primary dataset (`extracted_data/real_movie_data.csv`) contains 3,500+ movies scraped from the TMDB API.

**Raw Columns (17)**: movie_id, title, genres, genre_ids, release_year, release_date, runtime, rating, vote_count, popularity, overview, poster_path, backdrop_path, original_language, original_title, adult, video

**Era Distribution**:
| Era | Count |
|-----|-------|
| 1990s | ~900 |
| 2000s | ~1,000 |
| 2010s | ~1,000 |
| 2020s | ~650 |

---

## Key Insights

- **Average Rating**: ~6.5/10 across all movies
- **Genre Leader**: Drama is the most common genre; top-rated genres include Documentary and History
- **Era Trends**: 2000s and 2010s have the most films; recent movies (2020s) show slightly higher average ratings
- **Weighted Score**: Combines rating quality with audience engagement for a balanced ranking metric
- **Outlier Detection**: IQR method identifies rating outliers, popularity anomalies, and age-popularity anomalies

---

