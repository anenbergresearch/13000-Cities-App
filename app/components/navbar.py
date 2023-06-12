# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc

MILKEN_LOGO = "assets/milken_institute.png"
HAQAST_LOGO = "assets/HAQAST.png"

logos = dbc.Row([dbc.Col(html.Img(src=MILKEN_LOGO, height="50px")),dbc.Col(html.Img(src=HAQAST_LOGO, height="50px"))],  className="ms-auto flex-nowrap mt-3 mt-md-0",
    align="center")

# Define the navbar structure
def Navbar():

    layout = html.Div([
        dbc.Navbar(dbc.Container([dbc.Row([dbc.Col(
            dbc.NavbarBrand("Home",href='/')),dbc.Col(
            dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Networks", href="/networks")),
                    dbc.NavItem(dbc.NavLink("Countries", href="/countries")),
                    dbc.NavItem(dbc.NavLink("States", href="/states")),
                    dbc.NavItem(dbc.NavLink("     "))],
                style={'font-size':'larger','color':'white','font-family':'helvetica'},className='me-auto',navbar=True,))
                                          ]),logos],
            fluid=True),   
            className='mb-1 fixed-top',
            color="rgba(3, 60, 90,0.7)",
            #sticky='top',
            #fixed=True,
            dark=True,
        ), 
        
    ])

    return layout


def Navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Networks", href="/networks")),
            dbc.NavItem(dbc.NavLink("Countries", href="/countries")),
            dbc.NavItem(dbc.NavLink("States", href="/states")),
            logos
        ],
        brand="Home",
        brand_href="/",
        color="rgba(3, 60, 90,0.9)",
        dark=True,
        fluid=True,
        links_left =False,
        sticky='top',
        style={'font-size':'24px'}
    )
    return navbar