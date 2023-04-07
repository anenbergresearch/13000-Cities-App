# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc

# Define the navbar structure
def Navbar():

    layout = html.Div([
        dbc.Navbar(dbc.Container([dbc.Row([dbc.Col(
            dbc.NavbarBrand("Home",href='/')),dbc.Col(
            dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Cities", href="/cities")),
                    dbc.NavItem(dbc.NavLink("Countries", href="/countries")),
                    dbc.NavItem(dbc.NavLink("States", href="/states"))],
                style={'font-size':'large','color':'white','font-family':'helvetica'},className='me-auto',navbar=True,))])],
            fluid=True),   
            className='mb-1 fixed-top',
            color="#123C69",
            #sticky='top',
            #fixed=True,
            dark=True,
        ), 
        
    ])

    return layout