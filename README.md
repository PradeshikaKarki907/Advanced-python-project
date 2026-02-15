# 🎬 Netflix-Inspired Movie Analytics Pipeline

**Overview**  
An end-to-end movie analytics project inspired by **:contentReference[oaicite:0]{index=0}**, built using **legal public datasets** (no Netflix scraping). It implements a complete **ETL pipeline**, **EDA**, **visualization**, **interactive dashboard**, **logging**, and **automation**.

**Key Features**  
- ETL: Extract → Transform → Load  
- Data cleaning & feature engineering  
- SQLite database (normalized schema)  
- Exploratory Data Analysis (EDA)  
- Streamlit dashboard with filters & KPIs  
- Logging and error handling  
- Automated scheduling (schedule / CRON)

**Architecture**  
Data Source → Extract → Transform → Load → Database → EDA & Dashboard

**Data Source**  
- Using Wikipedia
- Using TMDB API 
- Netflix website is **not scraped**

**Pipeline Summary**  
- **Extraction**: Title, genres, year, rating, popularity, runtime → CSV/JSON  
- **Transformation**: Missing values, deduplication, feature engineering (movie age, rating category, popularity bucket, runtime category, weighted score)  
- **Loading**: SQLite tables (`movies`, `genres`, `movie_genres`) with indexes  

**EDA & Visualization**  
Movies per year, genre distribution, rating & popularity analysis, runtime analysis, top movies, correlation heatmap (PNG plots + report).

**Dashboard (Streamlit)**  
KPIs: total movies, average rating, popularity, votes  
Filters: year, genre, rating, era  
Views: overview, trends, genres, top movies

**Automation**  
Weekly scheduled runs using Python `schedule`; CRON supported; execution logs maintained.

**Tech Stack**  
Python, pandas, numpy, matplotlib, seaborn, SQLite, Streamlit, schedule, logging

**Project Structure**  
movie_analytics/ ├─ src/ ├─ data/ ├─ database/ ├─ dashboard/ └─ README.md

**Note**  
Netflix data is not scraped due to legal restrictions.
All analysis uses public movie datasets.
