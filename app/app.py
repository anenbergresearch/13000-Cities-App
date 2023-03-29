# Import necessary libraries 
import dash_bootstrap_components as dbc
import dash

# Connect to main app.py file
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP], 
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)

server = app.server
app.config.suppress_callback_exceptions = True


