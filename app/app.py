# Import necessary libraries 
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash

# Connect to main app.py file
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.LUX], 
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)

server = app.server
# Connect to your app pages
from pages import country, cities

# Connect the navbar to the index
from components import navbar

# Define the navbar
nav = navbar.Navbar()

# Define the index page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav, 
    html.Div(id='page-content', children=[]), 
])

# Create the callback to handle mutlipage inputs
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/country':
        return country.layout
    if pathname == '/cities':
        return cities.layout
    else: # if redirected to unknown link
        return "404 Page Error! Please choose a link"