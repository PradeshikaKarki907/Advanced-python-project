"""
Interactive Movie Analytics Dashboard
Built with Streamlit for comprehensive data exploration
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Movie Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        color: #E50914;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #141414 0%, #1a1a1a 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #E50914;
        margin: 10px 0;
    }
    .kpi-value {
        font-size: 36px;
        font-weight: bold;
        color: #E50914;
    }
    .kpi-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load data from CSV"""
    # Try common locations for the processed CSV
    candidates = [
        os.path.join(os.getcwd(), 'processed_movies.csv'),
        os.path.join(os.getcwd(), 'data', 'processed', 'processed_movies.csv'),
        os.path.join(os.path.dirname(__file__), 'processed_movies.csv'),
        os.path.join(os.path.dirname(__file__), 'data', 'processed', 'processed_movies.csv'),
        '../data/processed/processed_movies.csv'
    ]

    for path in candidates:
        try:
            if os.path.exists(path):
                return pd.read_csv(path)
        except Exception:
            continue

    # Final fallback: attempt to read just the filename (may raise).
    return pd.read_csv('processed_movies.csv')


@st.cache_data
def load_from_database():
    """Load data from SQLite database"""
    conn = sqlite3.connect('../database/movies.db')
    df = pd.read_sql_query("SELECT * FROM movies", conn)
    conn.close()
    return df


def create_filters(df):
    """Create sidebar filters"""
    st.sidebar.header("🎯 Filters")
    
    # Year range filter
    min_year = int(df['release_year'].min())
    max_year = int(df['release_year'].max())
    year_range = st.sidebar.slider(
        "Release Year Range",
        min_year, max_year,
        (min_year, max_year)
    )
    
    # Genre filter
    all_genres = set()
    for genres_str in df['genres'].dropna():
        all_genres.update(genres_str.split('|'))
    
    selected_genres = st.sidebar.multiselect(
        "Select Genres",
        sorted(all_genres),
        default=[]
    )
    
    # Rating filter
    min_rating = st.sidebar.slider(
        "Minimum Rating",
        float(df['rating'].min()),
        float(df['rating'].max()),
        float(df['rating'].min()),
        0.1
    )
    
    # Rating category filter
    rating_categories = st.sidebar.multiselect(
        "Rating Category",
        df['rating_category'].unique(),
        default=df['rating_category'].unique()
    )
    
    # Runtime filter
    runtime_categories = st.sidebar.multiselect(
        "Runtime Category",
        df['runtime_category'].unique(),
        default=df['runtime_category'].unique()
    )
    
    # Era filter
    eras = st.sidebar.multiselect(
        "Era",
        sorted(df['era'].unique()),
        default=sorted(df['era'].unique())
    )
    
    return {
        'year_range': year_range,
        'genres': selected_genres,
        'min_rating': min_rating,
        'rating_categories': rating_categories,
        'runtime_categories': runtime_categories,
        'eras': eras
    }


def apply_filters(df, filters):
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    # Year range
    filtered_df = filtered_df[
        (filtered_df['release_year'] >= filters['year_range'][0]) &
        (filtered_df['release_year'] <= filters['year_range'][1])
    ]
    
    # Genres
    if filters['genres']:
        mask = filtered_df['genres'].apply(
            lambda x: any(genre in x for genre in filters['genres'])
        )
        filtered_df = filtered_df[mask]
    
    # Rating
    filtered_df = filtered_df[filtered_df['rating'] >= filters['min_rating']]
    
    # Rating category
    filtered_df = filtered_df[filtered_df['rating_category'].isin(filters['rating_categories'])]
    
    # Runtime category
    filtered_df = filtered_df[filtered_df['runtime_category'].isin(filters['runtime_categories'])]
    
    # Era
    filtered_df = filtered_df[filtered_df['era'].isin(filters['eras'])]
    
    return filtered_df


def display_kpis(df):
    """Display key performance indicators"""
    st.markdown("### 📊 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Movies</div>
                <div class="kpi-value">{len(df):,}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_rating = df['rating'].mean()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Avg Rating</div>
                <div class="kpi-value">{avg_rating:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_popularity = df['popularity'].mean()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Avg Popularity</div>
                <div class="kpi-value">{avg_popularity:.1f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_votes = df['vote_count'].sum()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Votes</div>
                <div class="kpi-value">{total_votes:,}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        all_genres = set()
        for genres_str in df['genres'].dropna():
            all_genres.update(genres_str.split('|'))
        
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Unique Genres</div>
                <div class="kpi-value">{len(all_genres)}</div>
            </div>
        """, unsafe_allow_html=True)


def plot_genre_distribution(df):
    """Plot genre distribution"""
    all_genres = []
    for genres_str in df['genres']:
        all_genres.extend(genres_str.split('|'))
    
    genre_counts = pd.Series(all_genres).value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    genre_counts.plot(kind='barh', ax=ax, color='#E50914', alpha=0.8)
    ax.set_title('Top 10 Genres', fontsize=16, fontweight='bold')
    ax.set_xlabel('Number of Movies')
    ax.set_ylabel('Genre')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(genre_counts.values):
        ax.text(v + 1, i, str(v), va='center')
    
    return fig


def plot_rating_distribution(df):
    """Plot rating distribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(df['rating'], bins=30, color='#564d4d', alpha=0.7, edgecolor='black')
    ax.axvline(df['rating'].mean(), color='#E50914', linestyle='--', linewidth=2,
               label=f"Mean: {df['rating'].mean():.2f}")
    ax.axvline(df['rating'].median(), color='#0080ff', linestyle='--', linewidth=2,
               label=f"Median: {df['rating'].median():.2f}")
    
    ax.set_title('Rating Distribution', fontsize=16, fontweight='bold')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(alpha=0.3)
    
    return fig


def plot_movies_per_year(df):
    """Plot movies per year"""
    year_counts = df['release_year'].value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    year_counts.plot(kind='line', marker='o', ax=ax, color='#E50914', linewidth=2, markersize=6)
    
    ax.set_title('Movies Released Per Year', fontsize=16, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Movies')
    ax.grid(alpha=0.3)
    
    return fig


def plot_popularity_vs_rating(df):
    """Plot popularity vs rating scatter"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(df['rating'], df['popularity'], 
                        c=df['vote_count'], cmap='RdYlGn',
                        alpha=0.6, s=50)
    
    ax.set_title('Popularity vs Rating', fontsize=16, fontweight='bold')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Popularity')
    ax.grid(alpha=0.3)
    
    plt.colorbar(scatter, ax=ax, label='Vote Count')
    
    return fig


def plot_vote_count_distribution(df):
    """Plot vote count distribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(df['vote_count'], bins=40, color='#E50914', alpha=0.7, edgecolor='black')
    ax.axvline(df['vote_count'].mean(), color='#0080ff', linestyle='--', linewidth=2,
               label=f"Mean: {df['vote_count'].mean():,.0f}")
    ax.axvline(df['vote_count'].median(), color='#00ff00', linestyle='--', linewidth=2,
               label=f"Median: {df['vote_count'].median():,.0f}")
    
    ax.set_title('Vote Count Distribution', fontsize=16, fontweight='bold')
    ax.set_xlabel('Vote Count')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(alpha=0.3)
    
    return fig


def plot_runtime_distribution(df):
    """Plot runtime distribution with box plot"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(df['runtime'].dropna(), bins=30, color='#564d4d', alpha=0.7, edgecolor='black', label='Distribution')
    ax.axvline(df['runtime'].mean(), color='#E50914', linestyle='--', linewidth=2,
               label=f"Mean: {df['runtime'].mean():.0f} min")
    ax.axvline(df['runtime'].median(), color='#0080ff', linestyle='--', linewidth=2,
               label=f"Median: {df['runtime'].median():.0f} min")
    
    ax.set_title('Runtime Distribution', fontsize=16, fontweight='bold')
    ax.set_xlabel('Runtime (minutes)')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(alpha=0.3)
    
    return fig


def plot_runtime_vs_rating(df):
    """Plot runtime vs rating scatter"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(df['runtime'].dropna(), df['rating'].dropna(), 
                        c=df['popularity'].dropna(), cmap='viridis',
                        alpha=0.6, s=50)
    
    # Add trend line
    z = np.polyfit(df['runtime'].dropna(), df['rating'].dropna(), 1)
    p = np.poly1d(z)
    ax.plot(df['runtime'].dropna().sort_values(), p(df['runtime'].dropna().sort_values()), 
            "r--", alpha=0.8, linewidth=2, label='Trend')
    
    ax.set_title('Runtime vs Rating', fontsize=16, fontweight='bold')
    ax.set_xlabel('Runtime (minutes)')
    ax.set_ylabel('Rating')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='Popularity')
    
    return fig


def plot_correlation_heatmap(df):
    """Plot correlation heatmap of numeric columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, ax=ax, cbar_kws={'label': 'Correlation'})
    ax.set_title('Correlation Matrix - Numeric Columns', fontsize=16, fontweight='bold')
    
    return fig


def plot_top_genres_by_rating(df):
    """Plot top genres by average rating"""
    all_genres_with_ratings = []
    for idx, row in df.iterrows():
        if pd.notna(row['genres']):
            for genre in row['genres'].split('|'):
                all_genres_with_ratings.append({'genre': genre, 'rating': row['rating']})
    
    if all_genres_with_ratings:
        genre_df = pd.DataFrame(all_genres_with_ratings)
        avg_rating_by_genre = genre_df.groupby('genre')['rating'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.RdYlGn(avg_rating_by_genre['mean'] / avg_rating_by_genre['mean'].max())
        avg_rating_by_genre['mean'].plot(kind='barh', ax=ax, color=colors)
        ax.set_title('Top 10 Genres by Average Rating', fontsize=16, fontweight='bold')
        ax.set_xlabel('Average Rating')
        ax.set_ylabel('Genre')
        ax.grid(axis='x', alpha=0.3)
        
        # Add count labels
        for i, (genre, row) in enumerate(avg_rating_by_genre.iterrows()):
            ax.text(row['mean'] + 0.05, i, f"(n={int(row['count'])})", va='center')
        
        return fig
    return None


def plot_movie_age_vs_rating(df):
    """Plot movie age vs rating"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(df['movie_age'], df['rating'], 
                        c=df['popularity'], cmap='plasma',
                        alpha=0.6, s=50)
    
    ax.set_title('Movie Age vs Rating', fontsize=16, fontweight='bold')
    ax.set_xlabel('Movie Age (years)')
    ax.set_ylabel('Rating')
    ax.grid(alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='Popularity')
    
    return fig


def plot_popularity_bucket_dist(df):
    """Plot popularity bucket distribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    popularity_order = ['Low', 'Medium', 'High', 'Very High']
    pop_counts = df['popularity_bucket'].value_counts().reindex(popularity_order, fill_value=0)
    
    colors = ['#FF6B6B', '#FFA500', '#4ECDC4', '#E50914']
    wedges, texts, autotexts = ax.pie(pop_counts, labels=pop_counts.index, autopct='%1.1f%%',
                                       colors=colors, startangle=90, textprops={'fontsize': 11})
    ax.set_title('Movies by Popularity Bucket', fontsize=16, fontweight='bold')
    
    # Add counts in legend
    legend_labels = [f'{cat}: {count} movies' for cat, count in pop_counts.items()]
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 0, 0.5, 1))
    
    return fig


def display_top_movies(df):
    """Display top movies table"""
    st.markdown("### 🏆 Top Movies by Weighted Score")
    
    top_movies = df.nlargest(20, 'weighted_score')[
        ['title', 'release_year', 'genres', 'rating', 'popularity', 'weighted_score']
    ].copy()
    
    top_movies['weighted_score'] = top_movies['weighted_score'].round(2)
    top_movies['rating'] = top_movies['rating'].round(1)
    top_movies['popularity'] = top_movies['popularity'].round(1)
    
    # Add ranking
    top_movies.insert(0, 'Rank', range(1, len(top_movies) + 1))
    
    st.dataframe(
        top_movies,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "title": st.column_config.TextColumn("Movie Title", width="large"),
            "release_year": st.column_config.NumberColumn("Year", width="small"),
            "genres": st.column_config.TextColumn("Genres", width="medium"),
            "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
            "popularity": st.column_config.NumberColumn("Popularity", format="%.1f"),
            "weighted_score": st.column_config.NumberColumn("Score", format="%.2f"),
        }
    )


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<div class="main-header">🎬 Movie Analytics Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        df = load_data()
    
    # Sidebar
    st.sidebar.title("🎬 Movie Analytics")
    st.sidebar.markdown("---")
    
    # Data source selector
    data_source = st.sidebar.radio(
        "Data Source",
        ["CSV File", "SQLite Database"]
    )
    
    if data_source == "SQLite Database":
        try:
            df = load_from_database()
            st.sidebar.success("✅ Loaded from database")
        except:
            st.sidebar.warning("⚠️ Database not available, using CSV")
    
    st.sidebar.markdown("---")
    
    # Filters
    filters = create_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 Showing {len(filtered_df):,} of {len(df):,} movies")
    
    # Main content
    if len(filtered_df) == 0:
        st.warning("⚠️ No movies match the selected filters. Please adjust your criteria.")
        return
    
    # KPIs
    display_kpis(filtered_df)
    
    st.markdown("---")
    
    # Visualizations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Overview", "📈 Trends", "🎭 Genres", "🏆 Top Movies", "⏱️ Runtime", "🔗 Relationships"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.pyplot(plot_rating_distribution(filtered_df))
        
        with col2:
            st.pyplot(plot_vote_count_distribution(filtered_df))
        
        # Era analysis
        st.markdown("### 🕐 Movies by Era")
        era_counts = filtered_df['era'].value_counts().sort_index()
        st.bar_chart(era_counts)
        
        st.markdown("### 🎯 Popularity Bucket Distribution")
        fig = plot_popularity_bucket_dist(filtered_df)
        if fig:
            st.pyplot(fig)
        
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.pyplot(plot_movies_per_year(filtered_df))
        
        with col2:
            st.pyplot(plot_movie_age_vs_rating(filtered_df))
        
        # Rating trend over time
        st.markdown("### 📈 Average Rating Trend")
        avg_rating_by_year = filtered_df.groupby('release_year')['rating'].mean().sort_index()
        st.line_chart(avg_rating_by_year)
        
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.pyplot(plot_genre_distribution(filtered_df))
        
        with col2:
            fig = plot_top_genres_by_rating(filtered_df)
            if fig:
                st.pyplot(fig)
        
        # Genre statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Rating Category Distribution")
            rating_cat_counts = filtered_df['rating_category'].value_counts()
            st.bar_chart(rating_cat_counts)
        
        with col2:
            st.markdown("### ⏱️ Runtime Category Distribution")
            runtime_cat_counts = filtered_df['runtime_category'].value_counts()
            st.bar_chart(runtime_cat_counts)
    
    with tab4:
        display_top_movies(filtered_df)
        
        # Additional stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌟 Highest Rated Movies")
            top_rated = filtered_df.nlargest(10, 'rating')[['title', 'rating', 'release_year']]
            st.dataframe(top_rated, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("### 🔥 Most Popular Movies")
            most_popular = filtered_df.nlargest(10, 'popularity')[['title', 'popularity', 'release_year']]
            st.dataframe(most_popular, hide_index=True, use_container_width=True)
    
    with tab5:
        col1, col2 = st.columns(2)
        
        with col1:
            st.pyplot(plot_runtime_distribution(filtered_df))
        
        with col2:
            st.pyplot(plot_runtime_vs_rating(filtered_df))
        
        st.markdown("### 🎬 Runtime Category Breakdown")
        runtime_cat = filtered_df['runtime_category'].value_counts()
        st.bar_chart(runtime_cat)
    
    with tab6:
        col1, col2 = st.columns(2)
        
        with col1:
            st.pyplot(plot_popularity_vs_rating(filtered_df))
        
        with col2:
            st.pyplot(plot_correlation_heatmap(filtered_df))
        
        st.markdown("### 📊 Statistical Summary")
        st.dataframe(
            filtered_df[['rating', 'popularity', 'vote_count', 'runtime', 'movie_age']].describe().T,
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Total movies in database: {len(df):,}"
        f"</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
