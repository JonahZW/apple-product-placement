# import libraries
from dash import Dash, html, dcc, Input, Output, callback 
import pandas as pd
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc


# initialize app
stylesheets = [dbc.themes.ZEPHYR, 'https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet
app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app

# read CSV with data in
df = pd.read_csv('data.csv', low_memory=False)
df = df[df['startYear'] > 2019]


# *************************************************************************************
# ********************************** Widget/Nav Bar ***********************************
# *************************************************************************************

# include instructions for reference
instructions = html.Div([
    html.H3('Instructions'),
    html.P('Interact with the selector widgets below to update the displays. Utilize these \
           displays to visualize the effect and prevalence of Apple\'s product placements in \
           popular TV shows and movies.'),
    html.P('Selecting specific titles, years, devices, or other filters make it easy to dive into \
           an in-depth exploration of where many of Apple\'s product placements occured, and to \
           potentially visualize any correlation between usage and perception of the title.'),
    html.Br()
], className='row', style={'text-align':'justify'})

# now, the actual widgets/tools

## first, going to create each one
title_dropdown = html.Div([
    html.Label('Title'),
    dcc.Dropdown(id = 'title', options = df['Title'].unique(), multi = True),
    html.Br()
])

years = np.sort(df['startYear'].unique())

year_slider = html.Div([
    html.Label('Year(s)'),
    dcc.RangeSlider(
        id = 'year',
        min = years[0], 
        max = years[len(years)-1], 
        step = 1,
        value = [years[0], years[len(years)-1]], #default values
        marks={i: '{}'.format(i) for i in range(years[0], years[len(years)-1]+1, 1)},
        allowCross=False,
    ),
    html.Br()
])

type_dropdown = html.Div([
    html.Label('Movie or Show'),
    dcc.Dropdown(id = 'type', options = ['Movie', 'Show'], multi = True),
    html.Br()
])

device_dropdown = html.Div([
    html.Label('Device'),
    dcc.Dropdown(id = 'device', options = df['Device'].unique(), multi = True),
    html.Br()
])

imgCount = np.sort(df['imgCount'].unique())

imgCount_slider = html.Div([
    html.Label('Number of Apple Devices per Instance'),
    dcc.RangeSlider(
        id = 'imgCount',
        min = imgCount[0], 
        max = imgCount[len(imgCount)-1], 
        step = 1,
        value = [imgCount[0], imgCount[len(imgCount)-1]], #default values
        marks={i: '{}'.format(i) for i in range(imgCount[0], imgCount[len(imgCount)-1]+1, 10)},
        allowCross=False,
    ),
    html.Br()
])

rating = np.sort(df['averageRating'].unique())

rating_slider = html.Div([
    html.Label('Average Title Rating'),
    dcc.RangeSlider(
        id = 'rating',
        min = 0, 
        max = 10, 
        step = 0.25,
        value = [0, 10], #default values
        marks={i: '{}'.format(i) for i in range(0, 12, 1)},
        allowCross=False,
    ),
    html.Br()
])

## now, add each widget to the collection of widgets, to be added to the navBar overall
widgets = html.Div([
    html.H3('Selections'),
    title_dropdown,
    year_slider,
    type_dropdown,
    device_dropdown,
    html.H5('Advanced Selections'),
    imgCount_slider,
    rating_slider
])

# and this is the final div which will be added to the layout representing the entire navbar
navBar = html.Div([
    instructions,
    widgets
], className='three columns', style={'height':'100%'})


# *************************************************************************************
# ********************************** Visualizations ***********************************
# *************************************************************************************

## First, I include the functions which actually create the graphs

# creates the pie chart showing frequency of devices in titles
@callback(
        Output('pie-devices', 'figure'),
        Input('title','value'),
        Input('year','value'),
        Input('type','value'),
        Input('device','value'),
        Input('imgCount','value'),
        Input('rating','value')
)
def pie_devices(title, year, type, device, imgCount, rating):
    # set defaults if not set
    if title == None or title == []:
        title = df['Title'].unique()
    if type == None or type == []:
        type = df['Media'].unique()
    if device == None or device == []:
        device = df['Device'].unique()
    resolved_df = df.loc[df['Title'].isin(title) & (df['startYear'] >= year[0]) & (df['startYear'] <= year[1])
                         & df['Media'].isin(type) & df['Device'].isin(device) & (df['imgCount'] >= imgCount[0])
                         & (df['imgCount'] <= imgCount[1]) & (df['averageRating'] >= rating[0]) 
                         & (df['averageRating'] <= rating[1]) ]
    fig = px.pie(
        resolved_df.groupby(['Device'])['Device'].count().reset_index(name='count'),
        values='count',
        names='Device',
        title='Apple Products Placed in Titles by Device'
    )
    return fig

# creates scatterplot of rating vs number of product placements
@callback(
        Output('scatter-ratings', 'figure'),
        Input('title','value'),
        Input('year','value'),
        Input('type','value'),
        Input('device','value'),
        Input('imgCount','value'),
        Input('rating','value')
)
def scatter_ratings(title, year, type, device, imgCount, rating):
    # set defaults if not set
    if title == None or title == []:
        title = df['Title'].unique()
    if type == None or type == []:
        type = df['Media'].unique()
    if device == None or device == []:
        device = df['Device'].unique()
    resolved_df = df.loc[df['Title'].isin(title) & (df['startYear'] >= year[0]) & (df['startYear'] <= year[1])
                         & df['Media'].isin(type) & df['Device'].isin(device) & (df['imgCount'] >= imgCount[0])
                         & (df['imgCount'] <= imgCount[1]) & (df['averageRating'] >= rating[0]) 
                         & (df['averageRating'] <= rating[1])]
    same_cols = ['tconst', 'Title', 'numVotes', 'startYear','Media']
    agg_dict = {
        'Device':'count',
        'averageRating':'mean',
        'Season':'count',
        'Episode':'count',
        'imgCount':'mean' 
    }
    resolved_data = resolved_df.groupby(same_cols).agg(agg_dict).drop(columns=['Season','Device']).reset_index()
    resolved_data = resolved_data[resolved_data['imgCount'] > 1]
    resolved_data['year'] = resolved_data['startYear'].astype('string')
    fig = px.scatter(
        resolved_data,
        x='imgCount',
        y='averageRating',
        color='year',
        category_orders={'year': resolved_data['year'].sort_values().unique()},
        hover_name='Title',
        log_x=True,
        labels={
            'imgCount':'Number of Product Placements (logarithmic scale)',
            'averageRating':'Average Title Rating',
            'year':'Year'
        },
        title='Product Placements by Title vs Average Rating'
    )
    return fig

# creates line chart showing number of devices in titles over time
@callback(
        Output('line-device-time', 'figure'),
        Input('title','value'),
        Input('year','value'),
        Input('type','value'),
        Input('device','value'),
        Input('imgCount','value'),
        Input('rating','value')
)
def line_device_time(title, year, type, device, imgCount, rating):
    # set defaults if not set
    if title == None or title == []:
        title = df['Title'].unique()
    if type == None or type == []:
        type = df['Media'].unique()
    if device == None or device == []:
        device = df['Device'].unique()
    resolved_df = df.loc[df['Title'].isin(title) & (df['startYear'] >= year[0]) & (df['startYear'] <= year[1])
                         & df['Media'].isin(type) & df['Device'].isin(device) & (df['imgCount'] >= imgCount[0])
                         & (df['imgCount'] <= imgCount[1]) & (df['averageRating'] >= rating[0]) 
                         & (df['averageRating'] <= rating[1])]
    same_cols = ['startYear','Device']
    agg_dict = {
        'imgCount':'count', # add radio button to swap this b/w count, mean, sum
        'averageRating':'mean' 
    }
    resolved_df = resolved_df.drop(columns=['tconst','Title','numVotes','Media','Season','Episode'])
    resolved_df = resolved_df.groupby(same_cols).agg(agg_dict).reset_index()
    fig = px.line(
        resolved_df,
        x='startYear',
        y='imgCount',
        color='Device',
        markers=True,
        title='Number of Placements by Device over Time'
    )
    fig.update_xaxes(type='category')
    return fig

## Second, I combine all the figures/parts in correct divs

header_div = html.Div([
    html.H1('Apple Product Placements in Movies and TV Shows')
], style={'text-align':'center'})

pie_devices_div = html.Div([
    dcc.Graph(
        figure = pie_devices(None, [0,0],None,None,[0,0],[0,0]), id='pie-devices'
    ),
], className='four columns')

scatter_ratings_div = html.Div([
    dcc.Graph(
        figure = scatter_ratings(None, [0,0],None,None,[0,0],[0,0]), id='scatter-ratings'
    ),
])

line_device_time_div = html.Div([
    dcc.Graph(
        figure = line_device_time(None, [0,0],None,None,[0,0],[0,0]), id='line-device-time'
    ),
], className='eight columns')

# then organize into rows...
row1 = html.Div([
    pie_devices_div,
    line_device_time_div
], className='row')

row2 = html.Div([
    scatter_ratings_div
], className='row')

# and then the main section all together
main_div = html.Div([
    header_div,
    row1,
    row2
], className = 'nine columns')

# *************************************************************************************
# ********************************** Utility Stuff ************************************
# *************************************************************************************

# add everything to the app layout
app.layout = html.Div([
    navBar,
    main_div
], className='row', style={'padding':'20px'})

# run the app!
if __name__ == '__main__':
    app.run_server(debug=True) # comment this line when developing locally
    # app.run(jupyter_mode='tab', debug=True) # comment this line in production