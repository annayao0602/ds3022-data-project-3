import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import duckdb
import plotly.express as px
import pandas as pd

DB_FILE = "commits.duckdb"

app = dash.Dash(__name__)
app.title = "NumPy GitHub Repository Dashboard"

APP_STYLE = {
    "fontFamily": "Inter, Arial, sans-serif",
    "backgroundColor": "#f7f9fc",
    "padding": "0px 40px"
}
CARD_STYLE = {
    "backgroundColor": "white",
    "padding": "25px",
    "borderRadius": "12px",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"
}
HEADER_STYLE = {
    "textAlign": "center",
    "padding": "40px 0 20px",
}

STAT_STYLE = {
    "fontSize": "64px",
    "color": "#484ADA",
    "fontWeight": "700",
    "textAlign": "center",
    "marginBottom": "0px"
}

SUBTITLE_STYLE = {
    "textAlign": "center",
    "fontSize": "18px",
    "color": "#666"
}

app.layout = html.Div(style=APP_STYLE, children=[
    # header
    html.Div([
        html.H1("NumPy GitHub Repository Dashboard", style={
            "fontSize": "42px",
            "fontWeight": "800",
            "marginBottom": "10px"
        }),
        html.Div("Live Streaming Analytics via Kafka + DuckDB", style=SUBTITLE_STYLE),
    ], style=HEADER_STYLE),

    # commits stats
    html.Div([
        html.Div([
            html.Div(id="commit-counter", style=STAT_STYLE),
            html.Div("Total Commits Processed", style=SUBTITLE_STYLE),
        ], style={**CARD_STYLE, "textAlign": "center"})
    ], style={"maxWidth": "400px", "margin": "auto"}),

    html.Br(),

    # time series figure
    html.Div([
        dcc.Graph(id="activity-graph", config={"displayModeBar": False})
    ], style=CARD_STYLE),

    # top contributors figure
    html.Div([
        dcc.Graph(id="author-graph", config={"displayModeBar": False})
    ], style=CARD_STYLE),

    # update every 1.5 seconds
    dcc.Interval(id="interval-component", interval=1500, n_intervals=0),
])

@app.callback(
    [Output("commit-counter", "children"),
    Output("activity-graph", "figure"),
    Output("author-graph", "figure"),],
    Input("interval-component", "n_intervals")
)
def update_dashboard(n):
    try:
        conn = duckdb.connect(DB_FILE, read_only=True)

        #time series
        df = conn.execute("""
            SELECT 
                date_trunc('month', date) AS month_bucket,
                COUNT(DISTINCT sha) AS commit_count
            FROM commits
            GROUP BY month_bucket
            ORDER BY month_bucket ASC
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
            return "0", empty_fig, {}
        
        # calculate total commits
        total_commits = df['commit_count'].sum()

        # time series figure
        fig_line = px.line(
            df,
            x="month_bucket",
            y="commit_count",
            title="Commit Activity Over Time",
            markers=True,
            template="plotly_white"
        )
        fig_line.update_layout(
            xaxis_title="Date",
            yaxis_title="Commits per Month",
            title_x=0.5,
            margin=dict(l=40, r=20, t=50, b=40),
        )

        # top contributors figure
        fig_bar = px.bar(
            df_authors,
            x="author",
            y="commit_count",
            text="commit_count",
            title="Top Contributors",
            template="plotly_white"
        )
        fig_bar.update_layout(
            xaxis_title="Contributor",
            yaxis_title="Commits",
            title_x=0.5,
            margin=dict(l=30, r=10, t=50, b=30),
        )
        # 
        fig_bar.update_traces(marker_color="#484ADA", textposition="outside")

        return f"{total_commits:,}", fig_line, fig_bar
    
    # error handling
    except Exception as e:
        err_fig = px.line(title=f"Error: {str(e)}")
        err_fig.update_layout(template="plotly_white")
        return "Error", err_fig, err_fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)