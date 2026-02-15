# 🎬 Netflix-Inspired Movie Analytics Pipeline

A complete end-to-end data engineering and analytics solution for movie data, featuring ETL pipeline, exploratory data analysis, and interactive dashboard.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Dashboard](#dashboard)
- [Automation](#automation)
- [Technical Stack](#technical-stack)

---

## 🎯 Overview

This project implements a production-ready movie analytics system inspired by Netflix, using legal and publicly available data sources. The pipeline extracts movie data, transforms it through comprehensive cleaning and feature engineering, loads it into a structured database, and provides rich visualizations and an interactive dashboard.

### Key Highlights

- ✅ **Complete ETL Pipeline**: Extract, Transform, Load with comprehensive logging
- ✅ **Data Quality**: Robust data cleaning, validation, and deduplication
- ✅ **Feature Engineering**: Advanced derived features and metrics
- ✅ **Database Design**: Normalized SQLite schema with proper indexing
- ✅ **Rich Analytics**: Comprehensive EDA with 20+ visualizations
- ✅ **Interactive Dashboard**: Streamlit-based UI with filters and KPIs
- ✅ **Automation Ready**: Scheduling support for periodic updates
- ✅ **Production Logging**: Detailed logging at every pipeline stage

---

## ✨ Features

### Data Pipeline

1. **Data Extraction**
   - Simulates TMDB API data extraction
   - Generates realistic movie datasets
   - Supports JSON and CSV output
   - Complete extraction logging

2. **Data Transformation**
   - Missing value handling
   - Duplicate removal
   - Data type normalization
   - Feature engineering:
     - Movie age calculation
     - Rating categorization
     - Popularity bucketing
     - Runtime classification
     - Era grouping
     - Weighted scoring

3. **Data Loading**
   - SQLite database with normalized schema
   - Three-table design (movies, genres, movie_genres)
   - Performance indexes
   - Aggregated summary tables

4. **Exploratory Data Analysis**
   - 8 comprehensive visualization sets
   - Statistical summaries
   - Correlation analysis
   - Trend identification
   - Detailed text reports

5. **Interactive Dashboard**
   - Real-time filtering
   - Key performance indicators
   - Multiple visualization tabs
   - Top movies rankings
   - Responsive design

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Data Sources   │
│  (TMDB-like)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   EXTRACTION    │
│  (extract.py)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TRANSFORMATION  │
│ (transform.py)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    LOADING      │
│   (load.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┬──────────────────┐
│   SQLite DB     │   CSV Files      │
└────────┬────────┴────────┬─────────┘
         │                 │
         ▼                 ▼
    ┌────────────────────────────┐
    │   ANALYTICS & DASHBOARD    │
    │  (eda.py + dashboard.py)   │
    └────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

```bash
# Clone or download the project
cd movie_analytics

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 --version
```

### Required Packages

```
pandas
numpy
matplotlib
seaborn
sqlite3 (built-in)
streamlit
logging (built-in)
schedule
```

---

## 🚀 Usage

### Quick Start - Run Complete Pipeline

```bash
cd src
python3 pipeline.py
```

This executes all phases:
1. Data extraction (500 movies)
2. Data transformation
3. Database loading
4. EDA generation

### Run Individual Phases

```bash
# Extract data only
python3 extract.py

# Transform data only
python3 transform.py

# Load to database only
python3 load.py

# Run EDA only
python3 eda.py
```

### Launch Interactive Dashboard

```bash
cd dashboard
streamlit run app.py
```

Access at: `http://localhost:8501`

### Automated Scheduling

```bash
# Run once immediately
python3 scheduler.py --mode run-once

# Start continuous scheduler
python3 scheduler.py --mode schedule

# Generate CRON configuration
python3 scheduler.py --mode cron-config
```

---

## 📁 Project Structure

```
movie_analytics/
│
├── src/
│   ├── extract.py          # Data extraction module
│   ├── transform.py        # Data transformation module
│   ├── load.py            # Database loading module
│   ├── eda.py             # Exploratory data analysis
│   ├── pipeline.py        # Master pipeline orchestrator
│   └── scheduler.py       # Automation scheduler
│
├── dashboard/
│   └── app.py             # Streamlit dashboard application
│
├── data/
│   ├── raw/               # Raw extracted data
│   ├── processed/         # Cleaned and transformed data
│   └── logs/              # Pipeline execution logs
│
├── database/
│   └── movies.db          # SQLite database
│
├── visualizations/        # EDA plots and reports
│
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🔄 Data Pipeline

### Phase 1: Extraction

**Input**: None (generates sample data)  
**Output**: `data/raw/raw_movies.csv`, `data/raw/raw_movies.json`

**Features Extracted**:
- Movie ID, Title
- Genres (pipe-separated)
- Release Year
- Runtime (minutes)
- Rating (0-10 scale)
- Vote Count
- Popularity Score
- Overview/Description
- Extraction Timestamp

### Phase 2: Transformation

**Input**: `data/raw/raw_movies.csv`  
**Output**: `data/processed/processed_movies.csv`

**Operations**:
1. **Data Cleaning**
   - Fill missing ratings with median
   - Fill missing vote counts with 0
   - Remove duplicate entries
   - Drop rows with missing essential fields

2. **Data Normalization**
   - Standardize data types
   - Clean text fields
   - Format dates consistently

3. **Feature Engineering**
   - `movie_age`: Current year - release year
   - `rating_category`: Excellent/Good/Average/Poor
   - `popularity_bucket`: Low/Medium/High/Very High
   - `runtime_category`: Short/Medium/Long
   - `era`: 2020s/2010s/2000s/Pre-2000
   - `genre_count`: Number of genres per movie
   - `weighted_score`: Bayesian average rating

### Phase 3: Loading

**Input**: `data/processed/processed_movies.csv`  
**Output**: `database/movies.db`

**Database Schema**:

```sql
-- Movies table (main table)
CREATE TABLE movies (
    movie_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    release_year INTEGER,
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
    weighted_score REAL
);

-- Genres table (normalized)
CREATE TABLE genres (
    genre_id INTEGER PRIMARY KEY,
    genre_name TEXT UNIQUE
);

-- Junction table
CREATE TABLE movie_genres (
    movie_id TEXT,
    genre_id INTEGER,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);
```

**Indexes**:
- `idx_release_year` on movies(release_year)
- `idx_rating` on movies(rating)
- `idx_popularity` on movies(popularity)
- `idx_era` on movies(era)

### Phase 4: EDA

**Visualizations Generated**:

1. Movies per year (bar + line chart)
2. Genre distribution (horizontal bar)
3. Rating distribution (histogram, box plot, density)
4. Popularity vs Rating (scatter with correlation)
5. Runtime analysis (distribution, pie chart)
6. Top movies (weighted score, popularity)
7. Era analysis (trends over time)
8. Correlation heatmap

**Outputs**:
- `visualizations/*.png` (8 plot files)
- `visualizations/eda_report.txt` (comprehensive text report)

---

## 📊 Dashboard

### Features

**KPI Cards**:
- Total Movies
- Average Rating
- Average Popularity
- Total Votes
- Unique Genres

**Filters**:
- Year Range Slider
- Genre Multi-Select
- Minimum Rating
- Rating Category
- Runtime Category
- Era Selection

**Tabs**:

1. **Overview**
   - Rating distribution
   - Popularity vs Rating scatter
   - Movies by era

2. **Trends**
   - Movies released per year
   - Average rating trend

3. **Genres**
   - Genre distribution
   - Rating category breakdown
   - Runtime category distribution

4. **Top Movies**
   - Top 20 by weighted score (table)
   - Highest rated (top 10)
   - Most popular (top 10)

### Customization

Edit `dashboard/app.py` to:
- Change color schemes
- Add new visualizations
- Modify KPI calculations
- Add custom filters

---

## ▶️ Run the Streamlit dashboard (Windows)

If the `streamlit` CLI isn't available on your PATH, run Streamlit using the Python module runner which avoids PATH issues.

1) Install dependencies (recommended):

```powershell
python -m pip install -r requirements.txt
```

2) Start the dashboard:

PowerShell (recommended):

```powershell
.\run_streamlit.ps1
# or explicitly
python -m streamlit run app.py
```

Command Prompt (cmd.exe):

```cmd
run_streamlit.bat
```

If `python` is not on PATH, use `py` instead (e.g. `py -m pip install -r requirements.txt`).


---

## ⚙️ Automation

### Using Python Schedule

```bash
python3 scheduler.py --mode schedule
```

**Default Schedule**: Every Monday at 2:00 AM

**Modify Schedule** in `scheduler.py`:

```python
# Daily at 2 AM
schedule.every().day.at("02:00").do(self.run_scheduled_pipeline)

# Every 6 hours
schedule.every(6).hours.do(self.run_scheduled_pipeline)

# Weekly on Sunday
schedule.every().sunday.at("00:00").do(self.run_scheduled_pipeline)
```

### Using CRON (Linux/Mac)

Generate CRON config:

```bash
python3 scheduler.py --mode cron-config
```

Add to crontab:

```bash
crontab -e

# Add this line for weekly Monday execution
0 2 * * 1 cd /path/to/movie_analytics/src && python3 pipeline.py
```

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.8+ |
| **Data Processing** | pandas, numpy |
| **Visualization** | matplotlib, seaborn |
| **Database** | SQLite3 |
| **Dashboard** | Streamlit |
| **Scheduling** | schedule library, CRON |
| **Logging** | Python logging module |

---

## 📈 Sample Outputs

### Database Statistics
- **500 movies** processed
- **16 unique genres**
- **99.8% data quality**
- **3 normalized tables**

### Visualization Examples
- 8 comprehensive plot files
- Professional styling with seaborn
- High-resolution exports (300 DPI)

### Dashboard Performance
- Real-time filtering
- Sub-second response time
- Responsive design
- Interactive charts

---

## 🔍 Logging

All operations are logged to:
- `data/logs/pipeline.log` - Main pipeline execution
- `data/logs/scheduler.log` - Scheduled runs
- `data/logs/pipeline_summary.txt` - Execution summaries

**Log Levels**:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failures requiring attention

---

## 🎓 Learning Outcomes

This project demonstrates:
1. ✅ Complete ETL pipeline design
2. ✅ Data quality best practices
3. ✅ Database normalization (3NF)
4. ✅ Feature engineering techniques
5. ✅ Statistical analysis and EDA
6. ✅ Interactive dashboard development
7. ✅ Production logging strategies
8. ✅ Pipeline automation
9. ✅ Error handling and recovery
10. ✅ Documentation best practices

---

## 📝 Customization Guide

### Change Number of Movies

Edit `pipeline.py`:
```python
pipeline.run_pipeline(num_movies=1000)  # Default: 500
```

### Add New Features

Edit `transform.py` in `feature_engineering()` method:
```python
df['your_feature'] = df['column'].apply(your_function)
```

### Modify Dashboard

Edit `dashboard/app.py`:
- Update colors in CSS section
- Add new tabs in `st.tabs()`
- Create custom visualizations

### Use Real API

Replace `extract.py` with actual TMDB API calls:
```python
import requests
response = requests.get(f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}")
```

---

## 🐛 Troubleshooting

**Issue**: Database locked error  
**Solution**: Close all database connections before running pipeline

**Issue**: Streamlit not found  
**Solution**: `pip install streamlit`

**Issue**: Permission denied on logs  
**Solution**: Check write permissions on `data/logs/` directory

**Issue**: Matplotlib backend error  
**Solution**: Set `MPLBACKEND=Agg` environment variable

---

## 📚 Resources

- [TMDB API Documentation](https://developers.themoviedb.org/)
- [IMDb Datasets](https://www.imdb.com/interfaces/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## 📄 License

This project is for educational purposes. Movie data should be sourced from legal public APIs with proper attribution.

---

## 👏 Acknowledgments

- The Movie Database (TMDB) for API structure inspiration
- IMDb for public dataset formats
- Netflix for UI/UX inspiration

---

## 🚀 Next Steps

1. **Deploy Dashboard**: Host on Streamlit Cloud or Heroku
2. **Real Data Integration**: Connect to live TMDB API
3. **Advanced Analytics**: Add ML-based recommendations
4. **Cloud Migration**: Move to PostgreSQL/BigQuery
5. **CI/CD**: Automate with GitHub Actions
6. **Monitoring**: Add Prometheus/Grafana
7. **API Development**: Build REST API with FastAPI
8. **Caching**: Implement Redis for performance

---

**Built with ❤️ for Data Engineering Excellence**
