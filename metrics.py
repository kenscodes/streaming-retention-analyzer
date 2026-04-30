import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def completion_rate_by_genre(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate mean completion rate, median, total views, and std dev by genre."""
    res = df.groupby('genre').agg(
        mean_completion_rate=('completion_rate', 'mean'),
        median_completion_rate=('completion_rate', 'median'),
        total_views=('user_id', 'count'),
        std_deviation=('completion_rate', 'std')
    ).reset_index()
    res = res.sort_values('mean_completion_rate', ascending=False)
    return res

def content_efficiency_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Content Efficiency Score.
    efficiency = (total_views * avg_completion_rate) / avg_content_length_mins
    Normalize to 0-100 and add tiers.
    """
    res = df.groupby(['content_id', 'title', 'genre', 'content_type']).agg(
        total_views=('user_id', 'count'),
        avg_completion_rate=('completion_rate', 'mean'),
        content_length_mins=('content_length_mins', 'mean')
    ).reset_index()
    
    # Calculate raw score
    res['raw_efficiency'] = (res['total_views'] * res['avg_completion_rate']) / res['content_length_mins']
    
    # Normalize to 0-100 scale using MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 100))
    res['efficiency_score'] = scaler.fit_transform(res[['raw_efficiency']])
    
    # Assign tiers
    def assign_tier(score, quantiles):
        if score >= quantiles[0.9]: return 'Elite'
        if score >= quantiles[0.7]: return 'Strong'
        if score >= quantiles[0.3]: return 'Average'
        if score >= quantiles[0.1]: return 'Weak'
        return 'Underperforming'
        
    quantiles = res['efficiency_score'].quantile([0.1, 0.3, 0.7, 0.9]).to_dict()
    res['tier'] = res['efficiency_score'].apply(lambda x: assign_tier(x, quantiles))
    
    return res.drop(columns=['raw_efficiency']).sort_values('efficiency_score', ascending=False)

def dropoff_curve(df: pd.DataFrame) -> pd.DataFrame:
    """For Series content, calculate % of viewers still watching at each episode."""
    series_df = df[df['content_type'] == 'Series'].copy()
    
    max_episodes = int(series_df['episodes_watched'].max())
    total_starters = len(series_df)
    
    rows = []
    prev_pct = 100.0
    for ep in range(1, max_episodes + 1):
        still_watching = len(series_df[series_df['episodes_watched'] >= ep])
        pct_still_watching = (still_watching / total_starters) * 100 if total_starters > 0 else 0
        dropoff = prev_pct - pct_still_watching
        
        rows.append({
            'episode_number': ep,
            'pct_still_watching': pct_still_watching,
            'dropoff_from_previous_pct': dropoff
        })
        prev_pct = pct_still_watching
        
    return pd.DataFrame(rows)

def genre_retention_funnel(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate % of users who watched a genre and returned to watch it again."""
    user_genre_counts = df.groupby(['user_id', 'genre']).size().reset_index(name='views')
    
    res = user_genre_counts.groupby('genre').agg(
        total_starters=('user_id', 'count'),
        returned_viewers=('views', lambda x: (x > 1).sum())
    ).reset_index()
    
    res['retention_rate_pct'] = (res['returned_viewers'] / res['total_starters']) * 100
    return res.sort_values('retention_rate_pct', ascending=False)

def device_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate completion rate and avg watch duration by device."""
    res = df.groupby('device').agg(
        avg_completion_rate=('completion_rate', 'mean'),
        avg_watch_duration_mins=('watch_duration_mins', 'mean'),
        total_views=('user_id', 'count')
    ).reset_index()
    return res.sort_values('avg_completion_rate', ascending=False)

def peak_viewing_analysis(df: pd.DataFrame):
    """Return hourly volume and daily volume DataFrames."""
    df_date = df.copy()
    df_date['hour_of_day'] = df_date['session_date'].dt.hour
    df_date['day_of_week'] = df_date['session_date'].dt.day_name()
    
    hourly = df_date['hour_of_day'].value_counts().reset_index()
    hourly.columns = ['hour_of_day', 'viewing_volume']
    hourly = hourly.sort_values('hour_of_day')
    
    daily = df_date['day_of_week'].value_counts().reset_index()
    daily.columns = ['day_of_week', 'viewing_volume']
    
    # Ensure standard order for days
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily['day_of_week'] = pd.Categorical(daily['day_of_week'], categories=days, ordered=True)
    daily = daily.sort_values('day_of_week')
    
    return hourly, daily
