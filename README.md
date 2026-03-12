# Movie Analytics Dashboard

A full-stack data engineering project with an ETL pipeline, web scraping, exploratory data analysis, a recommendation engine, and an interactive Streamlit dashboard — built on 3,500+ movies from the TMDB API.

## Features

- **ETL Pipeline** — Extract from TMDB API, clean & engineer features, load into SQLite
- **Web Scraping** — Year-by-year TMDB Discover queries with rate limiting and scheduled daily scrapes
- **Interactive Dashboard** — 6 analysis tabs (Overview, Trends, Genres, Top Movies, Relationships, Insights) with dynamic filtering
- **Browse Movies** — Card-based browser with posters, search, genre filters, sort, and pagination
- **Recommendation Engine** — Three algorithms:
  - **Content-Based Filtering** — Cosine similarity on BoW-vectorized overview + genres
  - **Collaborative Filtering** — Truncated SVD on a synthetic user–movie ratings matrix
  - **Hybrid** — Weighted blend (60% content / 40% collaborative)

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Data | pandas, numpy, scikit-learn |
| Database | SQLite 3 |
| Visualization | plotly, matplotlib, seaborn |
| Web Framework | Streamlit |
| Scraping | requests, BeautifulSoup4 |

## Project Structure

```
├── app.py                        # Streamlit dashboard entry point
├── pipeline.py                   # ETL pipeline orchestrator
├── requirements.txt
├── extraction/                   # Scraper & scheduled scrape
├── transformation/               # Cleaning & feature engineering
├── loading/                      # SQLite loader
├── analysis/                     # EDA & insight reports
├── recommendation/               # Recommendation engine (CB, CF, Hybrid)
├── components/                   # Streamlit UI components
├── extracted_data/               # Movie CSV dataset
└── img/                          # EDA output images
```

## Setup

```bash
git clone <repository-url>
cd Advanced-python-project
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
```

## Usage

```bash
# Launch the dashboard
streamlit run app.py

# Run the ETL pipeline
python pipeline.py

# Scrape fresh data
python -c "from extraction.scraper import MovieDataScraper; s = MovieDataScraper(); s.save_scraped_data(s.scrape_all_eras(), 'real_movie_data.csv')"
```

## Data Pipeline

1. **Extract** — TMDB API year-by-year queries (1990–present), Wikipedia fallback
2. **Transform** — Clean, deduplicate, engineer 6 features (movie_age, rating_category, popularity_bucket, era, genre_count, weighted_score)
3. **Load** — Normalized SQLite schema (movies, genres, movie_genres, ratings_summary)
4. **Analyze** — Statistical summaries, correlation analysis, IQR outlier detection

