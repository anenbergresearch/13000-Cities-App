# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc

# Define the navbar structure
def Navbar():

    layout = html.Div([
        dbc.Navbar(dbc.Container([
            dbc.NavbarBrand("Home",href='/'),
            dbc.Nav(
                children=[
                    dbc.NavItem(dbc.NavLink("Cities", href="/cities")),
                    dbc.NavItem(dbc.NavLink("Countries", href="/countries")),
                    dbc.NavItem(dbc.NavLink("States", href="/states")),

                ] ,style={'font-size':'larger','color':'white','font-family':'helvetica'},
                className='ms-auto',navbar=True,)]),
            className='mb-5',
            color="#123C69",
            sticky='top',
            fixed=True,
            dark=True,
        ), 
    ])

    return layout