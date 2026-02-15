# Flexible Data Loader - Quick Start Guide

## Overview

The **Flexible Data Loader** allows you to load movie data from **ANY source** (TMDB, IMDb, Rotten Tomatoes, MovieLens, Letterboxd, Kaggle, custom sources) and automatically map it to the standardized schema used by the dashboard.

---

## Supported Data Sources

| Source | File Type | Auto-Detection | Notes |
|--------|-----------|-----------------|-------|
| **TMDB** | CSV/JSON | ✅ Yes | vote_average, vote_count columns |
| **IMDb** | TSV/CSV | ✅ Yes | tconst, primary_title columns |
| **MovieLens** | CSV | ✅ Yes | movieid, rating columns |
| **Rotten Tomatoes** | CSV/JSON | ✅ Yes | audience_score, critics_score |
| **Letterboxd** | CSV | ✅ Yes | imdb_id, genre columns |
| **Kaggle Datasets** | CSV | ✅ Yes | Various dataset formats |
| **Custom/Unknown** | CSV/JSON | ✅ Yes | Fuzzy matching on column names |

---

## Quick Start

### 1. Check Your Data Format

First, understand what columns your data has:

```python
import pandas as pd

df = pd.read_csv('your_data.csv')
print(df.columns)
print(df.head())
```

### 2. Preview the Mapping (Recommended)

Before loading, verify what columns will be detected:

```python
from flexible_loader import FlexibleDataLoader

loader = FlexibleDataLoader()
loader.show_mapping_report('your_data.csv')
```

**Output example:**
```
Column Mappings:
  id                         → movie_id           (sample: TM001)
  primaryTitle               → title              (sample: The Shawshank Redemption)
  startYear                  → release_year       (sample: 1994)
  runtimeMinutes             → runtime            (sample: 142)
  averageRating              → rating             (sample: 9.3)
  numVotes                   → vote_count         (sample: 2000000)
```

### 3. Load Your Data

**Option A: Auto-detect source**
```python
from flexible_load_integration import UniversalMovieExtractor

extractor = UniversalMovieExtractor(data_source='csv')
df = extractor.extract_data(filepath='your_data.csv')
```

**Option B: Specify source type**
```python
df = extractor.extract_data(filepath='imdb_data.csv', source_type='imdb')
```

**Option C: Custom mapping**
```python
custom_map = {
    'Film Name': 'title',
    'Release Year': 'release_year',
    'IMDB Score': 'rating',
    'Genre': 'genres',
    'Runtime': 'runtime'
}

df = extractor.extract_data(
    filepath='my_movies.csv', 
    custom_mapping=custom_map
)
```

### 4. Save Standardized Data

```python
extractor.save_data(df, filename='standardized_movies.csv')
# Saves to: extracted_data/standardized_movies.csv
```

### 5. Use with Pipeline

```python
# Modify extract.py line where data is loaded:
df = pd.read_csv('extracted_data/standardized_movies.csv')

# Then run:
# python pipeline.py
```

---

## Full Workflow Example

### Scenario: Load IMDb Data

```python
from flexible_load_integration import UniversalMovieExtractor
from flexible_loader import FlexibleDataLoader

# Step 1: Preview mapping
loader = FlexibleDataLoader()
loader.show_mapping_report('imdb_title_basics.tsv', source='imdb')

# Step 2: Load data
extractor = UniversalMovieExtractor(data_source='csv')
df = extractor.extract_data(
    filepath='imdb_title_basics.tsv', 
    source_type='imdb'
)

# Step 3: Check what we loaded
print(f"Loaded {len(df)} movies")
print(f"Columns: {df.columns}")
print(df.head())

# Step 4: Save for pipeline
extractor.save_data(df, filename='imdb_movies_standardized.csv')

print("✅ Ready! Now run: python pipeline.py")
```

---

## Column Mappings Reference

### Standard Schema (Pipeline Expects)

```python
{
    'movie_id': str,           # Unique identifier
    'title': str,              # Movie title
    'genres': str,             # Pipe-separated: 'Action|Drama|Sci-Fi'
    'release_year': int,       # Year released
    'runtime': int,            # Minutes
    'rating': float,           # 0-10 scale
    'vote_count': int,         # Number of votes/ratings
    'popularity': float,       # Popularity score
    'overview': str            # Plot description (optional)
}
```

### IMDb Column Mappings

```
IMDb Column          →  Standard Column
─────────────────────────────────────
tconst              →  movie_id
primary_title       →  title
start_year          →  release_year
runtime_minutes     →  runtime
average_rating      →  rating
num_votes           →  vote_count
genres              →  genres
```

### TMDB Column Mappings

```
TMDB Column         →  Standard Column
───────────────────────────────────
id                 →  movie_id
title              →  title
release_date       →  release_year
runtime            →  runtime
vote_average       →  rating
vote_count         →  vote_count
popularity         →  popularity
overview           →  overview
```

### Kaggle Column Mappings

```
Kaggle Column       →  Standard Column
──────────────────────────────────────
film_name          →  title
release_year       →  release_year
genre              →  genres
rating             →  rating
votes              →  vote_count
runtime            →  runtime
```

---

## Troubleshooting

### Problem: "No column mappings found!"

**Solution:** Use custom mapping or rename your columns:

```python
custom_map = {
    'your_col_1': 'title',
    'your_col_2': 'rating',
    # ... match all important columns
}

df = extractor.extract_data(
    filepath='file.csv', 
    custom_mapping=custom_map
)
```

### Problem: Wrong source detected

**Solution:** Explicitly specify the source:

```python
df = extractor.extract_data(
    filepath='file.csv', 
    source_type='imdb'  # or 'tmdb', 'movielens', etc.
)
```

### Problem: Data looks wrong after loading

**Solution:** Check the mapping report first:

```python
loader.show_mapping_report('file.csv')
# Review and verify columns before loading
```

### Problem: Genres aren't pipe-separated

**Solution:** The loader automatically formats genres as pipe-separated. You can also manually fix:

```python
df['genres'] = df['genres'].str.replace(',', '|').str.replace('[', '').str.replace(']', '')
```

---

## Advanced Usage

### Load Multiple Sources and Combine

```python
extractor = UniversalMovieExtractor(data_source='csv')

# Load from different sources
df_imdb = extractor.extract_data(filepath='imdb_data.csv', source_type='imdb')
df_tmdb = extractor.extract_data(filepath='tmdb_data.csv', source_type='tmdb')

# Combine (remove duplicates by title+year)
df_combined = pd.concat([df_imdb, df_tmdb], ignore_index=True)
df_combined = df_combined.drop_duplicates(subset=['title', 'release_year'], keep='first')

# Save combined dataset
extractor.save_data(df_combined, filename='combined_movies.csv')
```

### Validate Data Quality

```python
# Check for missing values
print(df.isnull().sum())

# Check data types
print(df.dtypes)

# Check ranges
print(f"Ratings: {df['rating'].min()} - {df['rating'].max()}")
print(f"Years: {df['release_year'].min()} - {df['release_year'].max()}")
```

---

## Dashboard Compatibility

**The dashboard AUTOMATICALLY works with any data loaded via the flexible loader!**

All visualizations, filters, and KPIs will work because:
- ✅ Column names are standardized
- ✅ Data types are validated
- ✅ Missing values are handled
- ✅ Duplicates are removed
- ✅ Genres are formatted consistently

---

## Files Included

| File | Purpose |
|------|---------|
| `flexible_loader.py` | Main loader class with auto-detection |
| `flexible_load_integration.py` | Integration with pipeline + examples |
| `flexible_loader_guide.md` | This file |

---

## Questions?

**Q: Can I use data from other websites not listed?**
A: Yes! The fuzzy matching will attempt to detect columns automatically. Use `custom_mapping` if needed.

**Q: What if my data has different column names?**
A: Use the `custom_mapping` parameter to specify exactly how columns map.

**Q: Will the dashboard work without modification?**
A: Yes! The dashboard is designed to work with the standardized schema. No code changes needed.

**Q: Can I combine data from multiple sources?**
A: Yes! Load each source separately, then combine DataFrames and deduplicate.

---

## Next Steps

1. **Prepare your data file** (CSV or JSON)
2. **Run** `loader.show_mapping_report('your_file.csv')` to preview
3. **Load** the data using `ExtractorUniversal`
4. **Save** the standardized CSV
5. **Run** the pipeline: `python pipeline.py`
6. **View the dashboard**: `python -m streamlit run app.py`

Enjoy your data with the movie analytics dashboard! 🎬
