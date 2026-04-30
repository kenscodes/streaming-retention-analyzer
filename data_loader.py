import os
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'
RAW_DIR = DATA_DIR / 'raw'

def generate_synthetic_dataset(n: int = 50000) -> pd.DataFrame:
    """Generate a realistic synthetic streaming dataset."""
    print(f"Generating synthetic dataset with {n} records...")
    np.random.seed(42)
    
    genres = ['Drama', 'Comedy', 'Thriller', 'Action', 'Documentary',
              'Romance', 'Sci-Fi', 'Horror', 'Animation', 'Reality']
    
    df = pd.DataFrame({
        'user_id':          [f'U{i:06d}' for i in np.random.randint(1, 10001, n)],
        'content_id':       [f'C{i:04d}' for i in np.random.randint(1, 1001, n)],
        'title':            np.random.choice([f'Title_{i}' for i in range(1, 1001)], n),
        'genre':            np.random.choice(genres, n, p=[0.18,0.15,0.13,0.12,0.08,0.10,0.08,0.07,0.05,0.04]),
        'content_type':     np.random.choice(['Series', 'Movie'], n, p=[0.65, 0.35]),
        'total_episodes':   np.where(np.random.choice(['Series','Movie'], n, p=[0.65,0.35])=='Movie',
                                     1, np.random.randint(1, 25, n)),
        'watch_duration_mins': np.random.exponential(45, n).clip(1, 300).astype(int),
        'content_length_mins': np.random.choice([90, 120, 45, 60, 30, 150], n),
        'session_date':     pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 90, n), unit='D') + pd.to_timedelta(np.random.normal(19, 4, n).astype(int) % 24, unit='h') + pd.to_timedelta(np.random.randint(0, 60, n), unit='m'),
        'device':           np.random.choice(['Mobile', 'TV', 'Tablet', 'Desktop'], n, p=[0.45, 0.30, 0.15, 0.10]),
        'country':          np.random.choice(['IN', 'US', 'UK', 'BR', 'DE'], n, p=[0.40, 0.25, 0.15, 0.12, 0.08]),
        'user_subscription': np.random.choice(['Basic', 'Standard', 'Premium'], n, p=[0.35, 0.40, 0.25]),
        'rating':           np.random.choice([1,2,3,4,5,None], n, p=[0.05,0.08,0.15,0.30,0.25,0.17]),
    })
    
    # Calculate episodes watched ensuring it doesn't exceed total_episodes
    df['episodes_watched'] = df.apply(lambda r: np.random.randint(1, int(r['total_episodes'])+1), axis=1)
    df['completion_rate'] = (df['episodes_watched'] / df['total_episodes']).clip(0, 1)
    
    return df

def load_and_clean() -> pd.DataFrame:
    """
    Attempt to load Kaggle CSV from data/raw/. 
    If not found, generate synthetic data.
    Clean the data and return.
    """
    csv_files = list(RAW_DIR.glob('*.csv'))
    
    if csv_files:
        print(f"Loading raw dataset from {csv_files[0]}...")
        df = pd.read_csv(csv_files[0])
        # Add basic mapping if kaggle columns differ slightly
        col_mapping = {
            'User_ID': 'user_id', 'Content_ID': 'content_id', 'Title': 'title',
            'Genre': 'genre', 'Content_Type': 'content_type', 'Total_Episodes': 'total_episodes',
            'Episodes_Watched': 'episodes_watched', 'Watch_Duration_Mins': 'watch_duration_mins',
            'Content_Length_Mins': 'content_length_mins', 'Session_Date': 'session_date',
            'Device': 'device', 'Country': 'country', 'User_Subscription': 'user_subscription',
            'Rating': 'rating', 'Completion_Rate': 'completion_rate'
        }
        df.rename(columns=col_mapping, inplace=True)
    else:
        print("No raw CSV found. Falling back to synthetic dataset generator.")
        df = generate_synthetic_dataset()
    
    # Cleaning
    df['session_date'] = pd.to_datetime(df['session_date'])
    df['completion_rate'] = df['completion_rate'].clip(0, 1)
    if 'total_episodes' in df.columns:
        df['total_episodes'] = df['total_episodes'].fillna(1).astype(int)
    
    return df

def validate_schema(df: pd.DataFrame) -> None:
    """Print data quality report."""
    print("="*50)
 print(" DATA QUALITY REPORT")
    print("="*50)
    print(f"Total Records: {len(df):,}")
    print(f"Unique Users: {df['user_id'].nunique():,}")
    print(f"Unique Content Titles: {df['title'].nunique():,}")
    print(f"Date Range: {df['session_date'].min().date()} to {df['session_date'].max().date()}")
    
    print("\\nMissing Values (%) per column:")
    nulls = df.isnull().mean() * 100
    print(nulls[nulls > 0].to_string() if not nulls[nulls > 0].empty else "No missing values!")
    
    print("\\nGenre Distribution:")
    print(df['genre'].value_counts(normalize=True).mul(100).round(1).astype(str) + '%')
    print("="*50)
