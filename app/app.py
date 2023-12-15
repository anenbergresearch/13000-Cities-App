# Import necessary libraries 
import dash_bootstrap_components as dbc
import dash
# Connect to main app.py file
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://raw.githubusercontent.com/necolas/normalize.css/master/normalize.css'], 
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)
app.title = 'Urban AQ Explorer'
server = app.server
app.config.suppress_callback_exceptions = True


