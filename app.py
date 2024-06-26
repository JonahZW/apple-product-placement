# import libraries
from dash import Dash, html, dcc, Input, Output, callback 
import pandas as pd
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


# initialize app
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css" # css for dash w bootstrap
stylesheets = [dbc.themes.LUX, dbc_css] # load the CSS stylesheet
app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app
server = app.server # make it work for render

load_figure_template("lux")
bootstrap_colors = ['rgb(60, 60, 60)', 'rgb(198, 91, 85)', 'rgb(104, 189, 122)', 'rgb(246, 195, 112)', 'rgb(90, 153, 203)', 
                    'rgb(111, 111, 111)', 'rgb(223, 167, 164)'] # the colors for LUX theme so I can reuse as needed


# read CSV with data in
df = pd.read_csv('data/data.csv', low_memory=False)
df = df[df['startYear'] > 2019]


# *************************************************************************************
# ********************************** Widget/Nav Bar ***********************************
# *************************************************************************************

# include instructions for reference
instructions = html.Div([
    html.H3('Instructions', className='card-title'),
    html.P('Interact with the selector widgets below to update the displays. Utilize these \
           displays to visualize the effect and prevalence of Apple\'s product placements in \
           popular TV shows and movies.'),
    html.P('Selecting specific titles, years, devices, or other filters make it easy to dive into \
           an in-depth exploration of where many of Apple\'s product placements occured, and to \
           potentially visualize any correlation between usage and perception of the title.'),
    html.P('Deselect all titles, devices, and/or media types to see all of the relevant category')
], className='card-header', style={'text-align':'justify'})

# now, the actual widgets/tools

## first, going to create each one
@callback(
        Output('title','options'),
        Input('type','value'),
        Input('year','value')
)
def title(type, year):
    if type == None or type == []:
        type = df['Media'].unique()
    if year == None or year == []:
        year = df['startYear'].unique()
        year = [year[0], year[(len(year)-1)]]
    return [{'label': i, 'value': i} for i in df.loc[df['Media'].isin(type) & (df['startYear'] >= year[0]) & (df['startYear'] <= year[1])]['Title'].unique()]

title_dropdown = html.Div([
    html.Label('Specific Title (selecting none displays all)'),
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
    dcc.Dropdown(id = 'type', options = ['Movie', 'Show'], multi = True, value=['Movie','Show']),
    html.Br()
])

device_dropdown = html.Div([
    html.Label('Device'),
    dcc.Dropdown(id = 'device', options = df['Device'].unique(), multi = True, value=df['Device'].unique()),
    html.Br()
])

imgCount = np.sort(df['imgCount'].unique())

imgCount_slider = html.Div([
    html.Label('Number of Apple Devices per Instance'),
    dcc.RangeSlider(
        id = 'imgCount',
        min = imgCount[0]-1, 
        max = imgCount[len(imgCount)-1], 
        step = 1,
        value = [imgCount[0], imgCount[len(imgCount)-1]], #default values
        marks={i: '{}'.format(i) for i in range(imgCount[0]-1, imgCount[len(imgCount)-1]+1, 10)},
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

### create a mini div for the accordion of "advanced" widgets:
accordion = html.Div([
    dbc.Accordion([
        dbc.AccordionItem([
            title_dropdown,
            imgCount_slider,
            rating_slider
        ], title="Advanced Selections",)
    ], start_collapsed=True, flush=True)
], className='card border-secondary mb-3 p-0')


## now, add each widget to the collection of widgets, to be added to the navBar overall
widgets = html.Div([
    html.H3('Selections', className='card-title'),
    type_dropdown,
    year_slider,
    device_dropdown,
    accordion
], className='card-body')

# and this is the final div which will be added to the layout representing the entire navbar
navBar = html.Div([
    instructions,
    widgets
], className='card border-primary mb-3 col-lg-3 p-0', style={'height':'100%'})


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
        title='Apple Products Placed in Titles by Device',
        height=500
    )
    fig.update_traces(sort=False, direction='clockwise')
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
        'imgCount':'sum' 
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
    fig.update_traces(marker=dict(size=9, line=dict(width=0.5,color='DarkSlateGrey')), selector=dict(mode='markers'))
    return fig

# creates line chart showing number of devices in titles over time
@callback(
        Output('line-device-time', 'figure'),
        Input('title','value'),
        Input('year','value'),
        Input('type','value'),
        Input('device','value'),
        Input('imgCount','value'),
        Input('rating','value'),
        Input('line_device_radio','value')
)
def line_device_time(title, year, type, device, imgCount, rating,line_device_radio):
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
        'imgCount':line_device_radio, # radio button to swap this b/w count, mean, sum
        'averageRating':'mean' 
    }
    if line_device_radio == 'count':
        y_axis_title = 'Titles with 1+ Device Instance in Year'
    elif line_device_radio == 'sum':
        y_axis_title = 'Total Devices in Year'
    elif line_device_radio == 'mean':
        y_axis_title = 'Avg Instances of Device per Title in Year'
    resolved_df = resolved_df.drop(columns=['tconst','Title','numVotes','Media','Season','Episode'])
    resolved_df = resolved_df.groupby(same_cols).agg(agg_dict).reset_index()
    fig = px.line(
        resolved_df,
        x='startYear',
        y='imgCount',
        color='Device',
        markers=True,
        title='Number of Placements by Device over Time',
        labels={
            'imgCount':y_axis_title,
            'startYear':'Year'
        },
        color_discrete_sequence=bootstrap_colors[:len(resolved_df['Device'].unique())],
        height=420
    )
    fig.update_xaxes(type='category')
    fig.update_traces(marker=dict(size=9, line=dict(width=0.5,color='DarkSlateGrey')), line=dict(width=4))
    return fig

## Second, I combine all the figures/parts in correct divs

header_div = html.Div([
    html.H1('Apple Product Placements in Movies and TV Shows')
], style={'text-align':'center'})

pie_devices_div = html.Div([
    dcc.Graph(
        figure = pie_devices(None, [0,0],None,None,[0,0],[0,0]), id='pie-devices'
    ),
], className='card border-secondary mr-1', style={'float':'left', 'width':'36%', 'margin-right':'1%'})

scatter_ratings_div = html.Div([
    dcc.Graph(
        figure = scatter_ratings(None, [0,0],None,None,[0,0],[0,0]), id='scatter-ratings'
    ),
], className='card border-secondary mb-3')

line_device_time_div = html.Div([
    html.Div([
    dcc.Graph(
        figure = line_device_time(None, [0,0],None,None,[0,0],[0,0], 'mean'), id='line-device-time'
    ),
    html.Div([
        html.Label('Select below to change grouping of the data on the y-axis of graph above',htmlFor='line_device_radio'),
        dbc.RadioItems(
            options = [
                {'label': 'Average', 'value': 'mean', 'label_id': 'mean-rdio'},
                {'label': 'Count', 'value': 'count', 'label_id': 'count-rdio'},
                {'label': 'Sum', 'value': 'sum', 'label_id': 'sum-rdio'}
            ],
            value = 'mean',
            inline=True,
            id='line_device_radio',
            labelStyle={'display': 'inline-block','padding-right': '7px', 'textDecoration': 'underline dotted', 'cursor': 'pointer'}
        ),
        # add tooltips to explain what each option actually does
        dbc.Tooltip('Average number of instances of each device per title in a year', target='mean-rdio', placement='bottom'),
        dbc.Tooltip('Total number of titles which contained multiple instances of a device per year', target='count-rdio', placement='bottom'),
        dbc.Tooltip('Total number of times the specified device appeared in titles in a given year', target='sum-rdio', placement='bottom')
        ], style={"textAlign": "center",'margin-right':'3%','margin-left':'3%'}, className='row bg-light card mb-2')
    ])
], className='card border-secondary', style={'float':'right', 'width':'63%'})#f"{100*2/3-1}%"})

# then organize into rows...
row1 = html.Div([
    pie_devices_div,
    line_device_time_div
], className='container row mb-3')

row2 = html.Div([
    scatter_ratings_div
], className='container row')

# and then the main section all together
main_div = html.Div([
    header_div,
    row1,
    row2
], className = 'col-lg-9')

# *************************************************************************************
# ********************************** Utility Stuff ************************************
# *************************************************************************************

# add everything to the app layout
app.layout = dbc.Container([
    html.Div([
        navBar,
        main_div
    ], className='row', style={'padding':'20px'}),
    # add footer:
    html.Footer([ 
        html.P('This dashboard was created by Jonah Werbel for DS 4003 (taught by Dr. Natalie Kupperman) at UVA in Spring 2024.'),
        html.P(['Data originally sourced from ',html.A('Kaggle', 
            href='https://www.kaggle.com/datasets/mohammadhmozafary/apples-product-placements-in-movies-and-tv-shows', className='text-success'),
            '. See the GitHub repository with all work for this project ',html.A('here', 
            href='https://github.com/JonahZW/apple-product-placement/', className='text-success'),'.'])
    ], className='row text-light bg-dark p-4', style={'text-align':'center'})
], className='dbc', fluid=True)

app.title='Apple Product Placements'

# run the app!
if __name__ == '__main__':
    app.run_server(debug=True) # comment this line when developing locally
    # app.run(jupyter_mode='tab', debug=True) # comment this line in production