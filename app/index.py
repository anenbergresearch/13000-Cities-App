from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash

from app import app
from app import server
from pages import country, cities,states

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
    if pathname == '/states':
        return states.layout
    else: # if redirected to unknown link
        return "404 Page Error! Please choose a link"

#if __name__== '__main__':
#    app.run_server(host= '127.0.0.1',debug=True)  