# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # Dropdown list to select Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',  # Default value
        style={'width': '50%'}
    ),
    html.Br(),

    # Pie chart for success/failure count
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Slider for selecting Payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={i: str(i) for i in range(0, int(max_payload), 5000)},
        value=[min_payload, max_payload]
    ),

    # Scatter chart for payload vs launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for updating pie chart based on the selected site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Group by success and count the launches for all sites
        pie_data = spacex_df.groupby('class').size().reset_index(name='counts')
        pie_fig = px.pie(pie_data, names='class', values='counts',
                         title='Total Success vs Failed Launches')
    else:
        # Filter data by selected launch site
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        site_pie_data = site_data.groupby('class').size().reset_index(name='counts')
        pie_fig = px.pie(site_pie_data, names='class', values='counts',
                         title=f'Success vs Failed Launches for {selected_site}')
    return pie_fig

# TASK 4: Callback for updating scatter plot based on the selected site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filter data based on selected site and payload range
    filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                              (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        filtered_data = filtered_data[filtered_data['Launch Site'] == selected_site]

    scatter_fig = px.scatter(
        filtered_data,
        x='Payload Mass (kg)',
        y='class',
        color='class',
        title=f'Payload vs Launch Success for {selected_site if selected_site != "ALL" else "All Sites"}'
    )
    scatter_fig.update_layout(
        xaxis_title="Payload Mass (kg)",
        yaxis_title="Launch Success (1 = Success, 0 = Failure)"
    )
    return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
