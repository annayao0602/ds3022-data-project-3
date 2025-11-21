import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os
from quixstreams import Application

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

TOTAL_COMMITS = 0

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

    # Update every 1 second (1000ms)
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
])

@app.callback(
    Output('counter-display', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_counter(n):
    global TOTAL_COMMITS
    
    if consumer:
        
        for _ in range(50):
            msg = consumer.poll(0.01) 
            
            if msg is None:
                break 
            
            if msg.error():
                print("Kafka Error:", msg.error())
                continue
            
            TOTAL_COMMITS += 1
            
            consumer.store_offsets(msg)

    return f"{TOTAL_COMMITS}"

if __name__ == '__main__':
    app.run(debug=True, port=8050)