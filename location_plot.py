from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Load data from CSV
file_path = "./2024-10-01_2024-12-31_counts.csv"
df_sensor = pd.read_csv(file_path)

# Extract the first 60 rows for map visualization
df_sensor_60 = df_sensor.head(60)

# Ensure unique countlineId for dropdown
unique_ids = df_sensor["countlineId"].unique()

# Traffic participant options
participant_options = ["Car", "Pedestrian", "Cyclist", "Motorbike", "Bus", "OGV1", "OGV2", "LGV"]

app = Dash(__name__)

# Layout for the Dash app
app.layout = html.Div([
    html.Div(style={'height': '20px'}),
    html.H4("VivaCity Traffic Sensor Data Overview",
            style={'text-align': 'center', 'font-size': '36px', 'margin-bottom': '20px'}),

    html.P(
        "Our dataset comes from the VivaCity system, which includes data collected from 60 advanced traffic sensors strategically placed across major traffic hubs and key road nodes in the city. These sensors leverage cutting-edge computer vision and artificial intelligence technologies to monitor and classify various types of traffic participants in real-time. This includes cars, pedestrians, cyclists, motorbikes, buses, light goods vehicles (LGVs), and heavy goods vehicles (OGV1 and OGV2).",
        style={'font-size': '16px', 'line-height': '1.8', 'margin-bottom': '30px'}
    ),

    # Map to display sensor locations
    html.Div([
        dcc.Graph(
            id="sensor_map",
            figure=px.scatter_mapbox(
                df_sensor_60,
                lat="Latitude",
                lon="Longitude",
                hover_name="countlineName",
                zoom=10,
                title="Traffic Sensor Locations",
            ).update_layout(
                mapbox_style="carto-positron",
                margin={"r": 0, "t": 30, "l": 0, "b": 0}
            )
        ),
    ], style={'margin-bottom': '30px'}),
    html.Div(style={'height': '40px'}),
    # Table to display sensor details
    html.Div([
        html.H5("Sensor Details", style={'text-align': 'center', 'font-size': '24px', 'margin-bottom': '10px'}),
        dash_table.DataTable(
            id="sensor-table",
            columns=[
                {"name": "Countline Name", "id": "countlineName"},
                {"name": "Latitude", "id": "Latitude"},
                {"name": "Longitude", "id": "Longitude"},
            ],
            data=df_sensor_60[["countlineName", "Latitude", "Longitude"]].to_dict("records"),
            style_table={'margin': '0 auto', 'width': '80%'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'fontSize': '14px'
            }
        ),
    ], style={'margin-bottom': '30px'}),
 html.Div(style={'height': '40px'}),

    html.Div([
        html.Label("Select Sensor Location:", style={'font-size': '18px', 'display': 'block', 'text-align': 'center'}),
        dcc.Dropdown(
            id="countline-selector",
            options=[{"label": str(i), "value": i} for i in unique_ids],
            value=unique_ids[0],
            style={'width': '60%', 'margin': '0 auto 20px'}
        )
    ], style={'text-align': 'center'}),

    html.Div([
        html.Label("Select Traffic Participant Types:",
                   style={'font-size': '18px', 'display': 'block', 'text-align': 'center'}),
        dcc.Checklist(
            id="participant-selector",
            options=[{"label": p, "value": p} for p in participant_options],
            value=["Car"],  # Default selection
            inline=True,
            style={'text-align': 'center'}
        )
    ], style={'margin-bottom': '30px'}),

    # Line chart for traffic data
    dcc.Graph(id="time-series-chart"),

    html.Div(style={'height': '30px'}),
])


# Callback to update the chart based on selections
@app.callback(
    Output("time-series-chart", "figure"),
    Input("countline-selector", "value"),
    Input("participant-selector", "value"),
)
def update_chart(selected_countline, selected_participants):
    # Filter data for the selected countlineId
    filtered_data = df_sensor[df_sensor["countlineId"] == selected_countline]

    # Create a line chart for selected participants
    fig = go.Figure()
    for participant in selected_participants:
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Local Datetime"],
                y=filtered_data[participant],
                mode="lines",
                name=participant
            )
        )

    # Update layout
    fig.update_layout(
        title=f"Traffic Data for Sensor {selected_countline}",
        xaxis_title="Local Datetime",
        yaxis_title="Count",
        xaxis_rangeslider_visible=True,
        template="plotly_white",
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
