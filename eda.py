"""
Exploratory Data Analysis Module
Comprehensive analysis and visualization of movie data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

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

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class MovieEDA:
    """Perform exploratory data analysis on movie dataset"""
    
    def __init__(self):
        self.df = None
        logger.info("MovieEDA initialized")
    
    def load_data(self, filepath='../data/processed/processed_movies.csv'):
        """Load processed data"""
        try:
            self.df = pd.read_csv(filepath)
            logger.info(f"Loaded data: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return self.df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def basic_statistics(self):
        """Generate basic statistical summary"""
        logger.info("Generating basic statistics...")
        
        stats = {
            'Total Movies': len(self.df),
            'Average Rating': self.df['rating'].mean(),
            'Median Rating': self.df['rating'].median(),
            'Average Runtime': self.df['runtime'].mean(),
            'Average Popularity': self.df['popularity'].mean(),
            'Year Range': f"{self.df['release_year'].min()} - {self.df['release_year'].max()}",
            'Total Genres': len(set('|'.join(self.df['genres']).split('|')))
        }
        
        logger.info("Basic Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        return stats
    
    def plot_movies_per_year(self):
        """Plot number of movies released per year"""
        logger.info("Creating movies per year plot...")
        
        plt.figure(figsize=(14, 6))
        
        year_counts = self.df['release_year'].value_counts().sort_index()
        
        plt.subplot(1, 2, 1)
        year_counts.plot(kind='bar', color='steelblue', alpha=0.7)
        plt.title('Movies Released Per Year', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Number of Movies', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        
        plt.subplot(1, 2, 2)
        year_counts.plot(kind='line', marker='o', color='darkblue', linewidth=2)
        plt.title('Movie Release Trend Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Number of Movies', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../visualizations/movies_per_year.png', dpi=300, bbox_inches='tight')
        logger.info("Movies per year plot saved")
        plt.close()
    
    def plot_genre_distribution(self):
        """Plot genre distribution"""
        logger.info("Creating genre distribution plot...")
        
        # Extract all genres
        all_genres = []
        for genres_str in self.df['genres']:
            all_genres.extend(genres_str.split('|'))
        
        genre_counts = pd.Series(all_genres).value_counts()
        
        plt.figure(figsize=(12, 8))
        
        colors = plt.cm.Set3(range(len(genre_counts)))
        genre_counts.plot(kind='barh', color=colors, alpha=0.8)
        plt.title('Genre Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Number of Movies', fontsize=12)
        plt.ylabel('Genre', fontsize=12)
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(genre_counts.values):
            plt.text(v + 2, i, str(v), va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('../visualizations/genre_distribution.png', dpi=300, bbox_inches='tight')
        logger.info("Genre distribution plot saved")
        plt.close()
    
    def plot_rating_distribution(self):
        """Plot rating distribution"""
        logger.info("Creating rating distribution plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Histogram
        axes[0, 0].hist(self.df['rating'], bins=30, color='coral', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Rating Distribution (Histogram)', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Rating')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(self.df['rating'].mean(), color='red', linestyle='--', label=f"Mean: {self.df['rating'].mean():.2f}")
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)
        
        # Box plot
        axes[0, 1].boxplot(self.df['rating'], vert=True, patch_artist=True,
                          boxprops=dict(facecolor='lightblue', alpha=0.7))
        axes[0, 1].set_title('Rating Box Plot', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Rating')
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # Rating by category
        category_order = ['Poor', 'Average', 'Good', 'Excellent']
        category_counts = self.df['rating_category'].value_counts().reindex(category_order, fill_value=0)
        colors_cat = ['#ff6b6b', '#ffd93d', '#6bcf7f', '#4ecdc4']
        axes[1, 0].bar(category_counts.index, category_counts.values, color=colors_cat, alpha=0.8)
        axes[1, 0].set_title('Movies by Rating Category', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Rating Category')
        axes[1, 0].set_ylabel('Number of Movies')
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(category_counts.values):
            axes[1, 0].text(i, v + 2, str(v), ha='center', fontsize=10)
        
        # Density plot
        self.df['rating'].plot(kind='density', ax=axes[1, 1], color='purple', linewidth=2)
        axes[1, 1].set_title('Rating Density Plot', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Rating')
        axes[1, 1].set_ylabel('Density')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../visualizations/rating_distribution.png', dpi=300, bbox_inches='tight')
        logger.info("Rating distribution plots saved")
        plt.close()
    
    def plot_popularity_vs_rating(self):
        """Plot popularity vs rating analysis"""
        logger.info("Creating popularity vs rating analysis...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Scatter plot
        scatter = axes[0].scatter(self.df['rating'], self.df['popularity'], 
                                 c=self.df['vote_count'], cmap='viridis', 
                                 alpha=0.6, s=50)
        axes[0].set_title('Popularity vs Rating', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Rating', fontsize=12)
        axes[0].set_ylabel('Popularity', fontsize=12)
        axes[0].grid(alpha=0.3)
        plt.colorbar(scatter, ax=axes[0], label='Vote Count')
        
        # Add trend line
        z = np.polyfit(self.df['rating'], self.df['popularity'], 1)
        p = np.poly1d(z)
        axes[0].plot(self.df['rating'], p(self.df['rating']), "r--", alpha=0.8, linewidth=2)
        
        # Correlation analysis
        correlation_data = self.df[['rating', 'popularity', 'vote_count', 'runtime']].corr()
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0, 
                   ax=axes[1], square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        axes[1].set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('../visualizations/popularity_vs_rating.png', dpi=300, bbox_inches='tight')
        logger.info("Popularity vs rating analysis saved")
        plt.close()
    
    def plot_runtime_analysis(self):
        """Plot runtime analysis"""
        logger.info("Creating runtime analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Runtime distribution
        axes[0, 0].hist(self.df['runtime'], bins=30, color='teal', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Runtime Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Runtime (minutes)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(self.df['runtime'].mean(), color='red', linestyle='--', 
                          label=f"Mean: {self.df['runtime'].mean():.0f} min")
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)
        
        # Runtime by category
        runtime_cat_counts = self.df['runtime_category'].value_counts()
        colors_rt = ['#3498db', '#e74c3c', '#2ecc71']
        axes[0, 1].pie(runtime_cat_counts.values, labels=runtime_cat_counts.index, 
                      autopct='%1.1f%%', colors=colors_rt, startangle=90)
        axes[0, 1].set_title('Movies by Runtime Category', fontsize=12, fontweight='bold')
        
        # Runtime vs Rating
        axes[1, 0].scatter(self.df['runtime'], self.df['rating'], alpha=0.5, color='darkgreen')
        axes[1, 0].set_title('Runtime vs Rating', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Runtime (minutes)')
        axes[1, 0].set_ylabel('Rating')
        axes[1, 0].grid(alpha=0.3)
        
        # Average rating by runtime category
        avg_rating_by_runtime = self.df.groupby('runtime_category')['rating'].mean().sort_values()
        avg_rating_by_runtime.plot(kind='barh', ax=axes[1, 1], color='orange', alpha=0.8)
        axes[1, 1].set_title('Average Rating by Runtime Category', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Average Rating')
        axes[1, 1].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../visualizations/runtime_analysis.png', dpi=300, bbox_inches='tight')
        logger.info("Runtime analysis saved")
        plt.close()
    
    def plot_top_movies(self):
        """Plot top-rated and most popular movies"""
        logger.info("Creating top movies analysis...")
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Top 15 rated movies (by weighted score)
        top_rated = self.df.nlargest(15, 'weighted_score')[['title', 'weighted_score', 'rating']]
        top_rated = top_rated.sort_values('weighted_score')
        
        y_pos = np.arange(len(top_rated))
        axes[0].barh(y_pos, top_rated['weighted_score'], color='gold', alpha=0.8)
        axes[0].set_yticks(y_pos)
        axes[0].set_yticklabels(top_rated['title'], fontsize=9)
        axes[0].set_xlabel('Weighted Score', fontsize=12)
        axes[0].set_title('Top 15 Movies (Weighted Score)', fontsize=14, fontweight='bold')
        axes[0].grid(axis='x', alpha=0.3)
        
        # Top 15 most popular movies
        top_popular = self.df.nlargest(15, 'popularity')[['title', 'popularity', 'rating']]
        top_popular = top_popular.sort_values('popularity')
        
        y_pos = np.arange(len(top_popular))
        axes[1].barh(y_pos, top_popular['popularity'], color='crimson', alpha=0.8)
        axes[1].set_yticks(y_pos)
        axes[1].set_yticklabels(top_popular['title'], fontsize=9)
        axes[1].set_xlabel('Popularity Score', fontsize=12)
        axes[1].set_title('Top 15 Most Popular Movies', fontsize=14, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../visualizations/top_movies.png', dpi=300, bbox_inches='tight')
        logger.info("Top movies analysis saved")
        plt.close()
    
    def plot_era_analysis(self):
        """Plot analysis by era"""
        logger.info("Creating era analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Movies per era
        era_counts = self.df['era'].value_counts().sort_index()
        axes[0, 0].bar(era_counts.index, era_counts.values, color='mediumpurple', alpha=0.8)
        axes[0, 0].set_title('Movies by Era', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Era')
        axes[0, 0].set_ylabel('Number of Movies')
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(era_counts.values):
            axes[0, 0].text(i, v + 2, str(v), ha='center', fontsize=10)
        
        # Average rating by era
        avg_rating_era = self.df.groupby('era')['rating'].mean().sort_index()
        avg_rating_era.plot(kind='line', marker='o', ax=axes[0, 1], color='darkred', linewidth=2)
        axes[0, 1].set_title('Average Rating by Era', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Era')
        axes[0, 1].set_ylabel('Average Rating')
        axes[0, 1].grid(alpha=0.3)
        
        # Rating distribution by era (violin plot)
        era_order = sorted(self.df['era'].unique())
        data_for_violin = [self.df[self.df['era'] == era]['rating'].values for era in era_order]
        parts = axes[1, 0].violinplot(data_for_violin, positions=range(len(era_order)), 
                                     showmeans=True, showmedians=True)
        axes[1, 0].set_xticks(range(len(era_order)))
        axes[1, 0].set_xticklabels(era_order)
        axes[1, 0].set_title('Rating Distribution by Era', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Era')
        axes[1, 0].set_ylabel('Rating')
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # Popularity by era
        avg_pop_era = self.df.groupby('era')['popularity'].mean().sort_index()
        avg_pop_era.plot(kind='bar', ax=axes[1, 1], color='darkorange', alpha=0.8)
        axes[1, 1].set_title('Average Popularity by Era', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Era')
        axes[1, 1].set_ylabel('Average Popularity')
        axes[1, 1].tick_params(axis='x', rotation=0)
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../visualizations/era_analysis.png', dpi=300, bbox_inches='tight')
        logger.info("Era analysis saved")
        plt.close()
    
    def generate_report(self):
        """Generate comprehensive EDA report"""
        logger.info("Generating comprehensive EDA report...")
        
        report_path = '../visualizations/eda_report.txt'
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MOVIE DATASET - EXPLORATORY DATA ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Basic statistics
            f.write("1. BASIC STATISTICS\n")
            f.write("-" * 80 + "\n")
            stats = self.basic_statistics()
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Data quality
            f.write("2. DATA QUALITY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Records: {len(self.df)}\n")
            f.write(f"Missing Values: {self.df.isnull().sum().sum()}\n")
            f.write(f"Duplicate Titles: {self.df['title'].duplicated().sum()}\n\n")
            
            # Rating insights
            f.write("3. RATING INSIGHTS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Mean Rating: {self.df['rating'].mean():.2f}\n")
            f.write(f"Median Rating: {self.df['rating'].median():.2f}\n")
            f.write(f"Std Dev: {self.df['rating'].std():.2f}\n")
            f.write(f"Rating Range: {self.df['rating'].min():.1f} - {self.df['rating'].max():.1f}\n\n")
            
            f.write("Rating Categories:\n")
            for cat, count in self.df['rating_category'].value_counts().items():
                pct = (count / len(self.df)) * 100
                f.write(f"  {cat}: {count} ({pct:.1f}%)\n")
            f.write("\n")
            
            # Genre insights
            f.write("4. GENRE INSIGHTS\n")
            f.write("-" * 80 + "\n")
            all_genres = []
            for genres_str in self.df['genres']:
                all_genres.extend(genres_str.split('|'))
            genre_counts = pd.Series(all_genres).value_counts()
            
            f.write(f"Total Unique Genres: {len(genre_counts)}\n")
            f.write(f"Average Genres per Movie: {self.df['genre_count'].mean():.2f}\n\n")
            f.write("Top 10 Genres:\n")
            for genre, count in genre_counts.head(10).items():
                pct = (count / len(all_genres)) * 100
                f.write(f"  {genre}: {count} ({pct:.1f}%)\n")
            f.write("\n")
            
            # Runtime insights
            f.write("5. RUNTIME INSIGHTS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Average Runtime: {self.df['runtime'].mean():.0f} minutes\n")
            f.write(f"Median Runtime: {self.df['runtime'].median():.0f} minutes\n")
            f.write(f"Runtime Range: {self.df['runtime'].min()} - {self.df['runtime'].max()} minutes\n\n")
            
            for cat, count in self.df['runtime_category'].value_counts().items():
                pct = (count / len(self.df)) * 100
                f.write(f"  {cat}: {count} ({pct:.1f}%)\n")
            f.write("\n")
            
            # Top movies
            f.write("6. TOP MOVIES\n")
            f.write("-" * 80 + "\n")
            f.write("Top 10 by Weighted Score:\n")
            top_weighted = self.df.nlargest(10, 'weighted_score')[['title', 'rating', 'weighted_score']]
            for idx, row in top_weighted.iterrows():
                f.write(f"  {row['title']}: {row['weighted_score']:.2f} (Rating: {row['rating']})\n")
            f.write("\n")
            
            # Correlations
            f.write("7. FEATURE CORRELATIONS\n")
            f.write("-" * 80 + "\n")
            corr_matrix = self.df[['rating', 'popularity', 'vote_count', 'runtime']].corr()
            f.write(str(corr_matrix))
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"EDA report saved to {report_path}")


def main():
    """Main EDA workflow"""
    logger.info("=" * 80)
    logger.info("PHASE 5: EXPLORATORY DATA ANALYSIS STARTED")
    logger.info("=" * 80)
    
    try:
        eda = MovieEDA()
        
        # Load data
        eda.load_data()
        
        # Generate statistics
        eda.basic_statistics()
        
        # Create all visualizations
        eda.plot_movies_per_year()
        eda.plot_genre_distribution()
        eda.plot_rating_distribution()
        eda.plot_popularity_vs_rating()
        eda.plot_runtime_analysis()
        eda.plot_top_movies()
        eda.plot_era_analysis()
        
        # Generate comprehensive report
        eda.generate_report()
        
        logger.info("Exploratory Data Analysis completed successfully!")
        logger.info("All visualizations saved to ../visualizations/")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"EDA failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
