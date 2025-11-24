import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os
from quixstreams import Application
import duckdb
import plotly.express as px
import pandas as pd

DB_FILE = "commits.duckdb"

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Live GitHub Data Stream", style={'font-family': 'Arial', 'text-align': 'center'}),
    
    html.Div(id='counter-display', style={
        'font-size': '80px', 
        'text-align': 'center', 
        'color': '#0074D9', 
        'font-weight': 'bold',
        'margin-top': '50px'
    }),
    html.Div("Commits Processed", style={'text-align': 'center', 'font-size': '20px', 'color': '#555'}),

    dcc.Graph(id='activity-graph', style={'marginBottom': '40px'}),

    dcc.Graph(id='author-graph', style={'height': '300px'}),

    # Update every 1 second (1000ms)
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
])

@app.callback(
    [Output('counter-display', 'children'),
     Output('activity-graph', 'figure'),
     Output('author-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    try:
        conn = duckdb.connect(DB_FILE, read_only=True)

        #time series
        df = conn.execute("""
            SELECT 
                date_trunc('day', date) AS day_bucket,
                COUNT(DISTINCT sha) AS commit_count
            FROM commits
            GROUP BY day_bucket
            ORDER BY day_bucket ASC
                          """).df()
        
        #top authors
        df_authors = conn.execute("""
            SELECT 
                author,
                COUNT(DISTINCT sha) AS commit_count
            FROM commits
            GROUP BY author
            ORDER BY commit_count DESC
            LIMIT 5
        """).df()
        
        conn.close()

        if df.empty:
            empty_fig = px.line(title="Waiting for data...")
            return "0", empty_fig
        
        total_commits = df['commit_count'].sum()

        fig_line = px.line(
            df, 
            x='day_bucket', 
            y='commit_count', 
            title="Commit Frequency Over Time",
            markers=True
        )
        
        fig_line.update_layout(
            xaxis_title="Date", 
            yaxis_title="Commits per Day",
            template="plotly_white"
        )
        fig_bar = px.bar(
            df_authors, 
            x='author', 
            y='commit_count', 
            orientation='v',
            title="Top 5 Contributors",
            text='commit_count'
        )
        fig_bar.update_layout(
            yaxis={'categoryorder':'total ascending'},
            xaxis_title="Author", 
            yaxis_title="Number of Commits",
            template="plotly_white",
            margin=dict(l=20, r=20, t=30, b=30)
        )
        
        return f"{total_commits:,}", fig_line, fig_bar

    except Exception as e:
        err_fig = px.line(title=f"Error: {str(e)}")
        return "Error", err_fig, err_fig

    
   

if __name__ == '__main__':
    app.run(debug=True, port=8050)