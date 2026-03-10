# 🎬 Movie Analytics Dashboard

An end-to-end **data engineering and analysis** project featuring a complete ETL pipeline, exploratory data analysis, and interactive dashboard for movie data insights.

> **Production-Ready** | **Full Stack Data Science** | **Professional Architecture**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Dashboard Features](#dashboard-features)
- [Key Insights](#key-insights)
- [Contributing](#contributing)

---

## 🎯 Overview

This project demonstrates a **professional-grade data pipeline** that:
- **Extracts** movie data from multiple public sources (Wikipedia, TMDB API)
- **Transforms** raw data through cleaning, validation, and feature engineering
- **Loads** normalized data into an SQLite database with proper schema
- **Analyzes** data through exploratory data analysis and statistical modeling
- **Visualizes** insights via an interactive Streamlit dashboard with real-time filtering

**Dataset**: 488+ movies spanning 1990-2024 with 16+ genres and comprehensive metadata

---

## ✨ Features

### Data Pipeline
- ✅ Multi-source data extraction with automatic fallback
- ✅ Comprehensive data cleaning and validation
- ✅ Advanced feature engineering (7+ engineered features)
- ✅ Normalized SQLite database with proper foreign keys
- ✅ Complete logging and error handling
- ✅ Automated data quality checks

### Interactive Dashboard
- 📊 **7 Analysis Tabs**: Overview, Trends, Genres, Top Movies, Runtime, Relationships, Insights
- 🎯 **Dynamic Filtering**: Year range, genres, ratings, era, runtime categories
- 📈 **Visualizations**: 15+ interactive charts and plots
- 📋 **Reports**: Generate and download detailed insights reports
- 🗄️ **Multi-Source**: Load from CSV or SQLite database
- ⚡ **Performance**: Optimized queries with caching

### Analytics
- Genre distribution and correlations
- Rating trends across decades
- Runtime analysis and optimization
- Popularity vs quality metrics
- Movie age vs rating relationships
- Era-based clustering and analysis

---

## 🏗️ Architecture

```
Movie Analytics Pipeline
├── Data Sources
│   ├── Wikipedia (public, no API key)
│   └── TMDB API (free tier)
├── ETL Pipeline
│   ├── Extract (scraper.py)
│   ├── Transform (transform logic)
│   ├── Load (load logic)
│   └── EDA (analysis)
├── Database Layer
│   ├── SQLite with normalized schema
│   ├── 4 main tables
│   └── Optimized indexes
└── Presentation Layer
    ├── Streamlit Dashboard (app.py)
    ├── Real-time Visualizations
    └── Insights Reports
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.8+ |
| **Data Processing** | pandas, numpy |
| **Database** | SQLite 3 |
| **Visualization** | matplotlib, seaborn |
| **Web Framework** | Streamlit |
| **Web Scraping** | requests, BeautifulSoup4 |
| **Logging** | Python logging |
| **Environment** | Virtual environment (venv) |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip or conda package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/PradeshikaKarki907/Advanced-python-project.git
cd "advance py"

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
```
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
streamlit>=1.0.0
requests>=2.26.0
beautifulsoup4>=4.9.0
sqlite3 (built-in)
```

---

## 🚀 Usage

### Run the Complete Pipeline
```bash
# Execute entire ETL and EDA process
python pipeline.py
```

**Output:**
- Raw data: `../data/raw/raw_movies.csv`
- Processed data: `../data/processed/processed_movies.csv`
- Database: `../database/movies.db`
- Visualizations: `../visualizations/*.png`
- Report: `../data/processed/data_summary.txt`

### Launch the Dashboard
```bash
# Start interactive Streamlit app
python -m streamlit run app.py
```

**Access:** Open browser to `http://localhost:8501`

### Scrape Data
```bash
# Scrape from Wikipedia
python scraper.py
```

---

## 📁 Project Structure

```
advanced-python-project/
├── app.py                      # Streamlit dashboard (7 tabs)
├── pipeline.py                 # Complete ETL orchestration
├── scraper.py                  # Data extraction from multiple sources
├── insights_report.py          # Report generation utility
│
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── CLEANUP_SUMMARY.md          # Project cleanup documentation
│
├── .git/                       # Git repository
│   ├── main branch             # Production branch
│   └── skeleton branch         # Backup/template branch
│
└── README_DEPLOYMENT.md        # Deployment guide (optional)
```

### Data Directories (Auto-Generated)
```
../data/
├── raw/                        # Raw extracted data
│   ├── raw_movies.csv
│   ├── raw_movies.json
│   └── logs/
├── processed/                  # Cleaned and transformed data
│   ├── processed_movies.csv
│   └── data_summary.txt
└── output/                     # Analysis outputs

../database/
└── movies.db                   # SQLite database (normalized)

../visualizations/
├── genre_distribution.png
├── rating_distribution.png
├── movies_per_year.png
├── runtime_analysis.png
├── popularity_vs_rating.png
├── top_movies.png
├── era_analysis.png
└── eda_report.txt
```

---

## 🔄 Data Pipeline

### Phase 1: Extraction
- Sources: Wikipedia, TMDB API
- Format: CSV/JSON
- Records: 500+ movies
- Fallback: Automatic source rotation

### Phase 2: Transformation
- **Cleaning**: Handle missing values, remove duplicates
- **Normalization**: Standardize field formats
- **Validation**: Data quality checks
- **Feature Engineering**:
  - `movie_age`: Years since release
  - `rating_category`: Excellent/Good/Average/Poor
  - `popularity_bucket`: Low/Medium/High/Very High
  - `runtime_category`: Short/Standard/Long/Extended
  - `era`: Decade grouping
  - `genre_count`: Number of genres per movie
  - `weighted_score`: Composite quality score

### Phase 3: Loading
- **Database**: SQLite with normalized schema
- **Tables**:
  - `movies` (core movie data)
  - `genres` (unique genres)
  - `movie_genres` (many-to-many relationships)
  - `ratings_summary` (aggregated metrics)
- **Indexes**: Optimized for query performance

### Phase 4: Analysis
- Statistical summaries
- Trend analysis
- Correlation analysis
- Visualization generation

---

## 📊 Dashboard Features

### Overview Tab
- **KPIs**: Total movies, avg rating, popularity, votes, unique genres
- **Distributions**: Rating, vote count histograms
- **Era Analysis**: Movies by decade and era

### Trends Tab
- Movies released per year (line chart)
- Movie age vs rating (scatter plot)

### Genres Tab
- Top 10 genres (horizontal bar)
- Genre performance metrics
- Top genres by rating

### Top Movies Tab
- Top 20 movies by weighted score
- Detailed metrics table

### Runtime Tab
- Runtime distribution
- Runtime vs rating correlation
- Runtime categories breakdown

### Relationships Tab
- Correlation heatmap
- Statistical summary (describe)

### Insights Tab
- **Generate Report**: Create detailed analysis
- **Download**: Export as timestamped TXT file
- Includes all key metrics and findings

---

## 📈 Key Insights

### Dataset Overview
- **Total Movies**: 488
- **Time Span**: 1990-2024 (34 years)
- **Avg Rating**: 6.81/10 (median: 6.70)
- **Avg Runtime**: 132 minutes
- **Total Genres**: 16

### Quality Distribution
- **Excellent (8.0+)**: 31%
- **Good (7.0-7.9)**: 16%
- **Average (6.0-6.9)**: 20%
- **Below Average (<6.0)**: 33%

### Top Performing Genres
1. Mystery: 7.04/10
2. Fantasy: 6.99/10
3. Adventure: 6.99/10

### Production Trends
- Peak production: 1990s-2000s
- Recent movies (2020s): Higher avg rating (6.95/10)
- Overall consistency: Ratings stable across decades

---

## 🔧 Configuration

### Database
- **Type**: SQLite 3
- **Location**: `../database/movies.db`
- **Schema**: Normalized (3NF)
- **Optimization**: Strategic indexes on foreign keys

### Logging
- **Level**: INFO
- **Format**: Timestamp | Module | Level | Message
- **Output**: Console + File logs

### Dashboard
- **Framework**: Streamlit
- **Port**: 8501 (default)
- **Caching**: Automatic data caching for performance

---

## 🔐 Data Sources

### Wikipedia
- **URL**: https://en.wikipedia.org/wiki/IMDb_Top_250
- **API Key**: None required
- **Rate Limit**: Standard HTTP limits
- **License**: CC by-sa

### TMDB API
- **URL**: https://www.themoviedb.org/3
- **Setup**: https://www.themoviedb.org/settings/api
- **Rate Limit**: 40 requests/10 seconds
- **License**: Terms of Service

---

## 📋 Requirements

```
pandas>=1.3.0          # Data manipulation
numpy>=1.21.0          # Numerical computing
matplotlib>=3.4.0      # Plotting
seaborn>=0.11.0        # Statistical visualization
streamlit>=1.0.0       # Web dashboard
requests>=2.26.0       # HTTP requests
beautifulsoup4>=4.9.0  # HTML parsing
```

Install all: `pip install -r requirements.txt`

---

## 🚀 Deployment

### Local Development
```bash
python -m streamlit run app.py
```

### Production Considerations
- Use environment variables for API keys
- Implement caching for large datasets
- Set up automated pipeline scheduling
- Monitor database size and performance
- Implement authentication if needed

---

## 📝 Code Quality

- **Type Hints**: Full type annotations throughout
- **Docstrings**: Comprehensive function documentation
- **Error Handling**: Try-except blocks with logging
- **Logging**: Structured logging across all modules
- **Comments**: Inline comments for complex logic
- **PEP 8**: Code formatted to Python standards

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `KeyError: 'genres'`
- **Solution**: Run `pipeline.py` to regenerate database with genres

**Issue**: Database file not found
- **Solution**: Create `../database/` directory and run pipeline

**Issue**: Streamlit connection error
- **Solution**: Ensure relative paths are correct from script location

**Issue**: TMDB API key not working
- **Solution**: Save key to `tmdb_api_key.txt` in project root

---

## 📌 Branch Management

- **main**: Production-ready code with all enhancements
- **skeleton**: Backup template branch with complete project structure

Switch branches:
```bash
git checkout skeleton
git checkout main
```

---

## 📞 Support

For issues or questions:
1. Check existing GitHub issues
2. Review CLEANUP_SUMMARY.md for recent changes
3. Verify all requirements are installed
4. Check logs in `../data/logs/pipeline.log`

---

## 📄 License

This project uses publicly available data and follows the terms of service for all data sources.

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ End-to-end data engineering
- ✅ ETL pipeline design and implementation
- ✅ Database normalization and optimization
- ✅ Data cleaning and quality assurance
- ✅ Feature engineering
- ✅ Interactive data visualization
- ✅ Professional Python development practices
- ✅ Git version control and branching
- ✅ Software architecture principles

---

## 📊 Performance Metrics

- **Pipeline Execution**: ~6 seconds
- **Dashboard Load**: <2 seconds (with caching)
- **Database Queries**: <100ms
- **Report Generation**: <1 second

---

**Last Updated**: March 10, 2026  
**Project Status**: ✅ Production Ready  
**Version**: 1.0.0

---
