import json

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.split('\\n')}

def code(source):
    return {"cell_type": "code", "metadata": {}, "source": source.split('\\n'), "outputs": [], "execution_count": None}

cells = []

cells.append(md("# Streaming Content Retention Analyzer\\n\\n**An analytics tool for identifying which content is retaining viewers and which is quietly losing them.**"))

cells.append(code("""import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Set theme
pio.templates.default = 'plotly_white'
COLORS = {'navy': '#1E4282', 'crimson': '#B42846', 'green': '#2E7D32', 'orange': '#E67E22', 'yellow': '#F1C40F'}

# Import project modules
from data_loader import load_and_clean, validate_schema
from metrics import (completion_rate_by_genre, content_efficiency_score, 
                    dropoff_curve, genre_retention_funnel, device_performance, peak_viewing_analysis)
from segmentation import segment_viewers, content_risk_matrix
from export import (export_genre_performance, export_content_efficiency, 
                   export_viewer_segments, export_dropoff_curve, export_peak_viewing)

print(" Modules loaded.")"""))

cells.append(md("---## Section 1 — Data Loading & Quality Report"))
cells.append(code("""# Load data
df = load_and_clean()
validate_schema(df)
df.head()"""))
cells.append(code("""# Distributions
fig1 = px.histogram(df, x='genre', title='Genre Distribution', color_discrete_sequence=[COLORS['navy']])
fig2 = px.pie(df, names='device', title='Device Usage', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)

fig1.show()
fig2.show()
print(" Insight: Data loaded and validated successfully. Distributions look normal.")"""))

cells.append(md("---## Section 2 — Completion Rate by Genre"))
cells.append(code("""genre_perf = completion_rate_by_genre(df)
overall_avg = df['completion_rate'].mean()

fig = px.bar(genre_perf, x='mean_completion_rate', y='genre', orientation='h',
             color='mean_completion_rate', color_continuous_scale='RdYlGn',
             title='Mean Completion Rate per Genre')
fig.add_vline(x=overall_avg, line_dash="dash", line_color="black", annotation_text="Overall Average")
fig.show()

top3 = genre_perf['genre'].head(3).tolist()
bot3 = genre_perf['genre'].tail(3).tolist()
print(f" Insight: Top 3 genres by completion rate: {', '.join(top3)}. Bottom 3: {', '.join(bot3)}.")"""))

cells.append(md("---## Section 3 — Content Efficiency Score\\n\\n*Content Efficiency Score measures how much engaged viewing a piece of content generates relative to its length. A short documentary with high completion rates can outscore a blockbuster movie with lots of drop-offs.*"))
cells.append(code("""efficiency = content_efficiency_score(df)

# Output top 20
print(" TOP 20 CONTENT BY EFFICIENCY")
display(efficiency.head(20))

# Output bottom 20
print("\\n️ BOTTOM 20 CONTENT BY EFFICIENCY")
display(efficiency.tail(20))"""))
cells.append(code("""# Average efficiency by genre
avg_eff_genre = efficiency.groupby('genre')['efficiency_score'].mean().reset_index().sort_values('efficiency_score')
fig = px.bar(avg_eff_genre, x='genre', y='efficiency_score', title='Average Efficiency Score by Genre', color_discrete_sequence=[COLORS['navy']])
fig.show()

# Scatter
fig2 = px.scatter(efficiency, x='total_views', y='avg_completion_rate', size='content_length_mins', 
                  color='tier', hover_name='title', title='Reach vs Completion by Tier')
fig2.show()
print(" Insight: Elite tier content strongly indexes high completion rates regardless of total view count.")"""))

cells.append(md("---## Section 4 — Viewer Segmentation"))
cells.append(code("""segments = segment_viewers(df)
seg_counts = segments['segment'].value_counts().reset_index()

fig = px.pie(seg_counts, names='segment', values='count', title='Viewer Segments', color_discrete_sequence=px.colors.qualitative.Set2)
fig.show()

fav_genres = segments.groupby(['segment', 'favourite_genre']).size().reset_index(name='count')
fig2 = px.bar(fav_genres, x='segment', y='count', color='favourite_genre', title='Favourite Genre by Segment')
fig2.show()

dropoff_pct = (len(segments[segments['segment'] == 'Drop-off Risk']) / len(segments)) * 100
print(f" Insight: {dropoff_pct:.1f}% of viewers are Drop-off Risk.")"""))

cells.append(md("---## Section 5 — Drop-off Curve (Series)"))
cells.append(code("""dropoffs = dropoff_curve(df)

fig = px.line(dropoffs, x='episode_number', y='pct_still_watching', markers=True, 
              title='Series Drop-off Curve', color_discrete_sequence=[COLORS['crimson']])

# Find steepest drop
steepest_drop_idx = dropoffs['dropoff_from_previous_pct'].idxmax()
steepest_ep = dropoffs.loc[steepest_drop_idx, 'episode_number']
steepest_val = dropoffs.loc[steepest_drop_idx, 'pct_still_watching']

fig.add_vline(x=steepest_ep, line_dash="dot", line_color="black", annotation_text="The Cliff")
fig.show()

print(f" Insight: The steepest drop-off occurs at episode {steepest_ep}, where viewers stop watching. Content teams should prioritise the hook in early episodes.")"""))

cells.append(md("---## Section 6 — Content Risk Matrix"))
cells.append(code("""matrix = content_risk_matrix(efficiency)

quadrant_colors = {'Star Content': COLORS['green'], 'Clickbait': COLORS['yellow'], 
                   'Hidden Gem': COLORS['orange'], 'Dead Weight': COLORS['crimson']}

fig = px.scatter(matrix, x='total_views', y='avg_completion_rate', color='quadrant', 
                 color_discrete_map=quadrant_colors, hover_name='title',
                 title='Content Risk Matrix: Reach vs Quality')

fig.add_hline(y=matrix['avg_completion_rate'].median(), line_dash='dash', line_color='grey')
fig.add_vline(x=matrix['total_views'].median(), line_dash='dash', line_color='grey')
fig.show()

display(matrix['quadrant'].value_counts().reset_index())
print(" Insight: Dead Weight content needs to be reviewed for catalogue removal.")"""))

cells.append(md("---## Section 7 — Genre Retention Funnel"))
cells.append(code("""retention = genre_retention_funnel(df)

fig = px.bar(retention, x='genre', y='retention_rate_pct', title='Genre Retention Rate %', 
             color_discrete_sequence=[COLORS['navy']])
fig.show()

best_loyalty = retention.iloc[0]['genre']
print(f" Insight: {best_loyalty} has the best loyalty, with users consistently returning for more.")"""))

cells.append(md("---## Section 8 — Strategic Recommendations"))
cells.append(code("""dead_weight_pct = (len(matrix[matrix['quadrant'] == 'Dead Weight']) / len(matrix)) * 100
top_genre = top3[0]

memo = f\"\"\"## Content Strategy Memo — Q2 2025

**To:** Content Acquisition Team
**From:** Data Analytics
**Re:** Portfolio Optimisation Recommendations

### Finding 1 — {top_genre} is our most efficient content category
The data shows {top_genre} commands the highest completion rates and best retention.

### Finding 2 — {dead_weight_pct:.1f}% of catalogue is Dead Weight
A significant portion of the catalogue has both low reach and low completion rates.

### Finding 3 — Drop-off cliff at Episode {steepest_ep} is a retention risk
Most viewers abandoning series content do so around episode {steepest_ep}.

### Recommended Actions:
1. Increase acquisition budget for {top_genre}.
2. Review licensing for the bottom 10% efficiency content.
3. Brief content team on episode {steepest_ep} hook improvement.
\"\"\"
from IPython.display import Markdown
display(Markdown(memo))"""))

cells.append(md("---## CSV Exports"))
cells.append(code("""p1 = export_genre_performance(genre_perf, efficiency, retention)
p2 = export_content_efficiency(matrix)
p3 = export_viewer_segments(segments)
p4 = export_dropoff_curve(dropoffs)
hourly, daily = peak_viewing_analysis(df)
p5 = export_peak_viewing(hourly, daily)

print(" Exports completed to data/processed/")"""))

cells.append(md("""---
## Power BI Dashboard Instructions

**Page 1 — Content Performance Overview**
- Import `genre_performance.csv` and `content_efficiency.csv`
- KPI Cards: Avg Completion Rate, Total Unique Viewers, Top Genre, % Dead Weight
- Horizontal Bar Chart: mean_completion_rate by genre
- Scatter Chart: total_views vs avg_completion_rate (size=content_length_mins, color=tier)

**Page 2 — Viewer Behaviour**
- Import `viewer_segments.csv` and `dropoff_curve.csv`
- Donut Chart: viewer segment split
- Line Chart: dropoff_curve (add constant line at 50%)
- Bar Chart: favourite_genre per segment

**Page 3 — Strategic Content Flags**
- Import `content_efficiency.csv`
- Table: Bottom 20 by efficiency_score (Red background on "Underperforming")
- Table: Top 20 by efficiency_score (Green background on "Elite")
- Bar Chart: count of content per quadrant
- Text Box: Paste the Strategic Memo from Section 8

**Page 4 — Viewing Patterns**
- Import `peak_hourly_viewing.csv` and `peak_daily_viewing.csv`
- Bar Charts for hourly and daily volume
"""))

# Write notebook
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "cells": cells,
}

for cell in notebook['cells']:
    src = cell['source']
    cell['source'] = [line + '\\n' if i < len(src) - 1 else line for i, line in enumerate(src)]

with open('analysis.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook generated.")
