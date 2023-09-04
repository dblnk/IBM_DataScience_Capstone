# Import required libraries
import os
import subprocess

# Specify the name of the data file that will be used for dashboard visualization
file = "spacex_launch_dash.csv"

# Check if the file exists in the current directory
if not os.path.exists(file):
    # If the file doesn't exist, download it using wget
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"  # Replace with the actual URL
    subprocess.run(["wget", url])

# load libraries necessary for dashboard generation
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv(file)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

dropdown_options = [
    {'label': 'All Sites', 'value': 'ALL'},
    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
]   
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div(
                                    [dcc.Dropdown(
                                    id='site-dropdown',
                                    options = dropdown_options,
                                    value = 'ALL',
                                    placeholder='Select a site',
                                    searchable=True,
                                    style={'textAlign' : 'left', 'width' : '50%', 'padding' : '3px', 'font-size' : '20px'}
                                )]),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                        2500: '2500',
                                        7500: '7500',
                                        10000: '10000'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id = 'success-pie-chart', component_property='figure'),
    Input(component_id = 'site-dropdown', component_property='value')
    )   

# Computation to callback function and return graph
def get_pie_chart(entered_site):
    all_sites = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
    if entered_site == 'ALL':
        fig = px.pie(all_sites,
               values = 'class',
               names = 'Launch Site',
               )
        fig.update_layout(title = 'Total Successful Launches by Site',
                        title_x=0.5)
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_rate = filtered_df['class'].mean()
        failure_rate = 1-success_rate
        fig = px.pie(filtered_df,
               values = [failure_rate, success_rate],
               names = ['Failure','Success'],
               color_discrete_map={'Failure': "red", 'Success': "green"})
        fig.update_traces(marker=dict(colors=['red', 'green']))
        fig.update_layout(title = 'Success Rate at Launch Site: %s' % entered_site,
               title_x=0.5)
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id = 'success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id="payload-slider", component_property="value")]
    )

def get_scatter(entered_site, payload):

    if entered_site == 'ALL':
        filter_payload = spacex_df[ 
            (spacex_df['Payload Mass (kg)'] >= payload[0]) &
            (spacex_df['Payload Mass (kg)'] <= payload[1])
            ]
        fig = px.scatter(filter_payload,
               x = 'Payload Mass (kg)',
               y = 'class',
               color = 'Booster Version Category',
               )
        fig.update_yaxes(tickvals=[0, 1], ticktext=['Failure', 'Success'])
        fig.update_layout(xaxis_title='Payload Mass (kg)',
                            title='Success vs. Payload Mass by Booser Category for All Sites',
                            title_x=0.5)
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filter_payload = filtered_df[ 
            (filtered_df['Payload Mass (kg)'] >= payload[0]) &
            (filtered_df['Payload Mass (kg)'] <= payload[1])
        ]
        fig = px.scatter(filter_payload,
               x = 'Payload Mass (kg)',
               y = 'class',
               color = 'Booster Version Category'
               )
        fig.update_yaxes(tickvals=[0, 1], ticktext=['Failure', 'Success'])
        fig.update_layout(xaxis_title='Payload Mass (kg)', 
                          title='Success vs. Payload Mass by Booser Category at Launch Site: %s' % entered_site,
                          title_x=0.5)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
