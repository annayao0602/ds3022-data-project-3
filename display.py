import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os
from quixstreams import Application
import duckdb
import plotly.express as px
import pandas as pd

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:19092,127.0.0.1:29092,127.0.0.1:39092")
TOPIC_NAME = "github-commits"

try:
    app_kafka = Application(
        broker_address=KAFKA_BROKER,
        consumer_group="display-counter",
        auto_offset_reset="earliest",
        consumer_extra_config={"allow.auto.create.topics": "true"}
    )
    topic = app_kafka.topic(name=TOPIC_NAME, value_deserializer="json")
    consumer = app_kafka.get_consumer()
    consumer.subscribe([TOPIC_NAME])
    print("Kafka Consumer connected!")
except Exception as e:
    print(f"Kafka connection failed: {e}")
    consumer = None


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
    html.Div("Commits Processed", style={'text-align': 'center', 'font-size': '24px', 'color': '#555'}),

    dcc.Graph(id='activity-graph'),

    # Update every 1 second (1000ms)
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
])

@app.callback(
    [Output('counter-display', 'children'),
     Output('activity-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    try:
        conn = duckdb.connect("commits.duckdb", read_only=True)
        df = conn.execute("""
            SELECT 
                date,
                count(*) AS commit_count
            FROM commits
            GROUP BY date
            ORDER BY date ASC
                          """).df()
        
        conn.close()

        if df.empty:
            empty_fig = px.line(title="Waiting for data...")
            return empty_fig, "0"
        
        total_commits = df['commit_count'].sum()

        fig = px.line(
            df, 
            x='date', 
            y='commit_count', 
            title="Commit Frequency Over Time",
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Date", 
            yaxis_title="Commits per Day",
            template="plotly_white"
        )
        
        return fig, f"{total_commits:,}"

    except Exception as e:
        return (f"DB Error: {e}")

    
   

if __name__ == '__main__':
    app.run(debug=True, port=8050)