# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                html.Br(),

                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                             ],
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True),
                                
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=100,
                                    marks={i: str(i) for i in range(int(min_payload), int(max_payload) + 1, 100)},
                                    value=[int(min_payload), int(max_payload)]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2: Callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        data = spacex_df.groupby('Launch Site')['class'].value_counts().unstack().fillna(0)
        data = data.rename(columns={0: 'Failed', 1: 'Successful'})
        fig = px.pie(data_frame=data, values='Successful', names=data.index,
                     title='Total Successful Launches for All Sites')
    else:
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        data = site_data['class'].value_counts().reset_index()
        data.columns = ['Launch Outcome', 'Count']
        fig = px.pie(data_frame=data, values='Count', names='Launch Outcome',
                     title=f'Success vs Failed Launches for {selected_site}')
    return fig

# TASK 4: Callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Launch Site', title='Payload vs Launch Success',
                     labels={'class': 'Launch Success (1 = Success, 0 = Failure)', 'Payload Mass (kg)': 'Payload Mass (kg)'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)