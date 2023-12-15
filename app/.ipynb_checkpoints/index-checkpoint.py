from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from app import server
from pages import home,countries, cities,states

# Connect the navbar to the index
from components import navbar

# Define the navbar
nav = navbar.Navbar()

# Define the index page layout
app.title = 'Urban AQ Explorer'
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav, 
    html.Div(id='page-content', children=[]), 
])

# Create the callback to handle mutlipage inputs
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/countries':
        return countries.layout
    if pathname == '/networks':
        return cities.layout
    if pathname == '/states':
        return states.layout
    if pathname == '/':
        return home.layout
    else: # if redirected to unknown link
        return "404 Page Error! Please choose a link"

if __name__== '__main__':
    app.run_server(host= '0.0.0.0', debug=True)  