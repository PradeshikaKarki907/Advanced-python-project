import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ACCENT = "#E50914"
_TEMPLATE = "plotly_dark"
_BG = "rgba(0,0,0,0)"
_GRID = "rgba(255,255,255,0.07)"


def _layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#C9D1D9")),
        template=_TEMPLATE,
        font=dict(family="Inter, sans-serif", color="#8B949E"),
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=_GRID, linecolor="#21262D"),
        yaxis=dict(gridcolor=_GRID, linecolor="#21262D"),
        hoverlabel=dict(bgcolor="#161B22", font_color="#FAFAFA", bordercolor="#30363D"),
    )
    return fig


# ── Overview tab ─────────────────────────────────────────────────────────

def rating_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="rating", nbins=30, color_discrete_sequence=[ACCENT], opacity=0.85,
    )
    mean_val = df["rating"].mean()
    median_val = df["rating"].median()
    fig.add_vline(x=mean_val, line_dash="dash", line_color="#58A6FF",
                  annotation_text=f"Mean {mean_val:.2f}")
    fig.add_vline(x=median_val, line_dash="dot", line_color="#3FB950",
                  annotation_text=f"Median {median_val:.2f}")
    fig.update_layout(xaxis_title="Rating", yaxis_title="Count")
    return _layout(fig, "Rating Distribution")


def vote_count_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="vote_count", nbins=40, color_discrete_sequence=["#58A6FF"], opacity=0.8,
    )
    mean_val = df["vote_count"].mean()
    fig.add_vline(x=mean_val, line_dash="dash", line_color=ACCENT,
                  annotation_text=f"Mean {mean_val:,.0f}")
    fig.update_layout(xaxis_title="Vote Count", yaxis_title="Count")
    return _layout(fig, "Vote Count Distribution")


def era_distribution(df: pd.DataFrame) -> go.Figure:
    era_counts = df["era"].value_counts().sort_index()
    fig = px.bar(
        x=era_counts.index, y=era_counts.values,
        color_discrete_sequence=[ACCENT],
        labels={"x": "Era", "y": "Movies"},
    )
    fig.update_layout(xaxis_title="Era", yaxis_title="Movies")
    return _layout(fig, "Movies by Era")


def popularity_bucket_chart(df: pd.DataFrame) -> go.Figure:
    order = ["Very High", "High", "Medium", "Low"]
    counts = df["popularity_bucket"].value_counts().reindex(order, fill_value=0)
    colors = [ACCENT, "#58A6FF", "#D29922", "#8B949E"]
    fig = go.Figure(go.Bar(
        y=counts.index, x=counts.values, orientation="h",
        marker_color=colors,
        text=[f"{v:,}" for v in counts.values],
        textposition="outside",
    ))
    fig.update_layout(xaxis_title="Movies", yaxis_title="")
    return _layout(fig, "Movies by Popularity Bucket")


# ── Trends tab ───────────────────────────────────────────────────────────

def movies_per_year(df: pd.DataFrame) -> go.Figure:
    year_counts = df["release_year"].value_counts().sort_index()
    fig = px.line(
        x=year_counts.index, y=year_counts.values,
        markers=True, color_discrete_sequence=[ACCENT],
        labels={"x": "Year", "y": "Movies"},
    )
    return _layout(fig, "Movies Released Per Year")


def age_vs_rating(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df, x="movie_age", y="rating", color="popularity",
        color_continuous_scale="Plasma", opacity=0.6,
        labels={"movie_age": "Movie Age (years)", "rating": "Rating"},
    )
    return _layout(fig, "Movie Age vs Rating")


def rating_trend(df: pd.DataFrame) -> go.Figure:
    avg = df.groupby("release_year")["rating"].mean().sort_index()
    fig = px.line(
        x=avg.index, y=avg.values,
        color_discrete_sequence=["#58A6FF"],
        labels={"x": "Year", "y": "Avg Rating"},
    )
    return _layout(fig, "Average Rating Trend")


# ── Genres tab ───────────────────────────────────────────────────────────

def genre_distribution(df: pd.DataFrame) -> go.Figure:
    all_genres = []
    for gs in df["genres"].dropna():
        all_genres.extend(gs.split("|"))
    counts = pd.Series(all_genres).value_counts().head(10)
    fig = px.bar(
        y=counts.index, x=counts.values, orientation="h",
        color_discrete_sequence=[ACCENT],
        text=counts.values,
        labels={"x": "Movies", "y": "Genre"},
    )
    fig.update_traces(textposition="outside")
    return _layout(fig, "Top 10 Genres")


def genres_by_rating(df: pd.DataFrame) -> go.Figure:
    rows = []
    for _, r in df.iterrows():
        if pd.notna(r["genres"]):
            for g in r["genres"].split("|"):
                rows.append({"genre": g, "rating": r["rating"]})
    if not rows:
        return go.Figure()
    gdf = pd.DataFrame(rows)
    avg = gdf.groupby("genre")["rating"].agg(["mean", "count"]).sort_values("mean", ascending=False).head(10)
    fig = px.bar(
        y=avg.index, x=avg["mean"], orientation="h",
        color=avg["mean"], color_continuous_scale="RdYlGn",
        text=[f'{v:.2f} (n={int(c)})' for v, c in zip(avg["mean"], avg["count"])],
        labels={"x": "Avg Rating", "y": "Genre"},
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    return _layout(fig, "Top Genres by Average Rating")


def rating_category_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["rating_category"].value_counts()
    fig = px.bar(
        x=counts.index, y=counts.values,
        color_discrete_sequence=["#58A6FF"],
        labels={"x": "Category", "y": "Movies"},
    )
    return _layout(fig, "Rating Category Distribution")


def popularity_bucket_bar(df: pd.DataFrame) -> go.Figure:
    counts = df["popularity_bucket"].value_counts()
    fig = px.bar(
        x=counts.index, y=counts.values,
        color_discrete_sequence=[ACCENT],
        labels={"x": "Bucket", "y": "Movies"},
    )
    return _layout(fig, "Popularity Bucket Distribution")


# ── Relationships tab ────────────────────────────────────────────────────

def popularity_vs_rating(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df, x="rating", y="popularity", color="vote_count",
        color_continuous_scale="RdYlGn", opacity=0.6,
        labels={"rating": "Rating", "popularity": "Popularity", "vote_count": "Votes"},
    )
    return _layout(fig, "Popularity vs Rating")


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    num_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[num_cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r",
        aspect="auto",
    )
    return _layout(fig, "Correlation Matrix")
