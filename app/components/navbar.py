# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc

# Define the navbar structure
def Navbar():

    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Countries", href="/country")),
                dbc.NavItem(dbc.NavLink("Cities", href="/cities")),
                dbc.NavItem(dbc.NavLink("States", href="/states")),
            ] ,
            brand="Exploring 13000 Cities Data",
            brand_href="/cities",
            color="light",
            dark=False,
        ), 
    ])

    return layout