import os
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'

def _ensure_processed_dir():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def export_genre_performance(genre_perf: pd.DataFrame, efficiency: pd.DataFrame, retention: pd.DataFrame) -> str:
    """Export genre_performance.csv."""
    _ensure_processed_dir()
    
    # Merge metrics for genre
    avg_eff = efficiency.groupby('genre')['efficiency_score'].mean().reset_index(name='avg_efficiency_score')
    
    final = genre_perf.merge(avg_eff, on='genre', how='left').merge(retention[['genre', 'retention_rate_pct']], on='genre', how='left')
    
    path = PROCESSED_DIR / 'genre_performance.csv'
    final.to_csv(path, index=False, float_format='%.4f')
    return str(path)

def export_content_efficiency(content_efficiency_matrix: pd.DataFrame) -> str:
    """Export content_efficiency.csv."""
    _ensure_processed_dir()
    path = PROCESSED_DIR / 'content_efficiency.csv'
    
    cols = ['content_id', 'title', 'genre', 'content_type', 'total_views', 
            'avg_completion_rate', 'content_length_mins', 'efficiency_score', 'tier', 'quadrant']
    
    # Add quadrant if it exists
    if 'quadrant' not in content_efficiency_matrix.columns:
        content_efficiency_matrix['quadrant'] = 'Unknown'
        
    content_efficiency_matrix[cols].to_csv(path, index=False, float_format='%.4f')
    return str(path)

def export_viewer_segments(segments_df: pd.DataFrame) -> str:
    """Export viewer_segments.csv."""
    _ensure_processed_dir()
    path = PROCESSED_DIR / 'viewer_segments.csv'
    
    cols = ['user_id', 'segment', 'avg_completion_rate', 'avg_episodes_per_session', 
            'total_sessions', 'favourite_genre', 'user_subscription']
    
    # rename user_subscription to subscription_tier to match prompt
    df = segments_df.rename(columns={'user_subscription': 'subscription_tier'}).copy()
    
    df[cols].to_csv(path, index=False, float_format='%.4f')
    return str(path)

def export_dropoff_curve(dropoff_df: pd.DataFrame) -> str:
    """Export dropoff_curve.csv."""
    _ensure_processed_dir()
    path = PROCESSED_DIR / 'dropoff_curve.csv'
    dropoff_df.to_csv(path, index=False, float_format='%.4f')
    return str(path)

def export_peak_viewing(hourly_df: pd.DataFrame, daily_df: pd.DataFrame) -> str:
    """Export peak_viewing.csv containing both datasets."""
    _ensure_processed_dir()
    path = PROCESSED_DIR / 'peak_viewing.csv'
    
    # The prompt asked for both in one CSV, which is unusual for BI tools.
    # Usually it's better to have two CSVs, but to strictly follow the prompt:
    with open(path, 'w') as f:
        f.write("--- Hourly Volume ---\n")
        hourly_df.to_csv(f, index=False)
        f.write("\n--- Daily Volume ---\n")
        daily_df.to_csv(f, index=False)
    
    return str(path)
