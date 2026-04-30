import pandas as pd
import numpy as np

def segment_viewers(df: pd.DataFrame) -> pd.DataFrame:
    """Classify users into Binge Viewer, Casual Viewer, or Drop-off Risk."""
    user_stats = df.groupby('user_id').agg(
        avg_completion_rate=('completion_rate', 'mean'),
        total_sessions=('session_date', 'count'),
        avg_episodes_per_session=('episodes_watched', 'mean')
    ).reset_index()
    
    # Get favourite genre (mode)
    fav_genre = df.groupby('user_id')['genre'].apply(lambda x: x.mode().iloc[0]).reset_index(name='favourite_genre')
    
    # Also grab the first subscription tier found for each user
    sub_tier = df.groupby('user_id')['user_subscription'].first().reset_index()
    
    res = user_stats.merge(fav_genre, on='user_id').merge(sub_tier, on='user_id')
    
    def assign_segment(row):
        if row['avg_episodes_per_session'] > 3 and row['avg_completion_rate'] > 0.75:
            return 'Binge Viewer'
        elif row['avg_completion_rate'] < 0.40 or (row['total_sessions'] == 1 and row['avg_episodes_per_session'] == 1):
            return 'Drop-off Risk'
        elif 1 <= row['avg_episodes_per_session'] <= 3 and row['avg_completion_rate'] > 0.50:
            return 'Casual Viewer'
        else:
            return 'Other'
            
    res['segment'] = res.apply(assign_segment, axis=1)
    
    # In case there are 'Other' users, we can just map them to Casual for simplicity, 
    # but based on the rules, we might have gaps. We will keep 'Other' for visibility or merge them.
    # We will map 'Other' to 'Casual Viewer' to match the 3 segments constraint.
    res['segment'] = res['segment'].replace('Other', 'Casual Viewer')
    
    return res

def content_risk_matrix(content_efficiency_df: pd.DataFrame) -> pd.DataFrame:
    """Assign content to quadrants based on views and completion rate."""
    res = content_efficiency_df.copy()
    
    median_views = res['total_views'].median()
    median_completion = res['avg_completion_rate'].median()
    
    def assign_quadrant(row):
        if row['total_views'] >= median_views and row['avg_completion_rate'] >= median_completion:
            return 'Star Content'
        elif row['total_views'] >= median_views and row['avg_completion_rate'] < median_completion:
            return 'Clickbait'
        elif row['total_views'] < median_views and row['avg_completion_rate'] >= median_completion:
            return 'Hidden Gem'
        else:
            return 'Dead Weight'
            
    res['quadrant'] = res.apply(assign_quadrant, axis=1)
    return res
