# Import necessary libraries
import dash_bootstrap_components as dbc
from dash import dcc,html

def sliders(df):
    layout = dbc.Stack([dcc.Slider(
        id='crossfilter-year--slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=df['Year'].max(),
        marks={str(year): str(year) for year in df['Year'].unique()},
        step=None
    )])
    return layout

def lin_log():
    linlog=dbc.RadioItems(
                    id='crossfilter-xaxis-type',
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-secondary",
                    labelCheckedClassName="secondary",
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],                
                    value='Log',
                    labelStyle={'display': 'inline-block'}
                )
    return linlog

def pol_buttons(ident):
    pols = dbc.RadioItems(
                id="crossfilter-yaxis-column"+ident,
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-secondary",
                labelCheckedClassName="secondary",
                options=[
                    {"label": u'NO\u2082', "value": 'NO2'},
                    {"label": u'O\u2083', "value": 'O3'},
                    {"label": u'PM\u2082\u2085', "value": 'PM'},
                    {"label": u'CO\u2082', "value": 'CO2'},
                ],
                value='NO2',
                labelStyle={'display': 'inline-block'}
            )
    return pols

def pop_weighted(ident):
    wgt = dbc.RadioItems(
                    id='crossfilter-data-type'+ident,
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-secondary",
                    labelCheckedClassName="secondary",
                    options=[{'label': i, 'value': i} for i in ['Unweighted','Population Weighted']],
                    value='Unweighted',
                    labelStyle={'display': 'inline-block'}
                )
    return wgt