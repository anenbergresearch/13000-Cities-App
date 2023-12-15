# Import necessary libraries
import dash_bootstrap_components as dbc
from dash import dcc,html

def sliders(df):
    layout = dbc.Stack([dcc.Slider(
        id='crossfilter-year--slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=df['Year'].max(),
        marks= {str(year): {"label":str(year),"style":{'transform':'rotate(-45deg) translateX(-50%)'}} for year in df['Year'].unique()},
        step=None,
        included=False,
        dots=False
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

def health_metrics(name):
    tt= dbc.Tooltip(
                "Population Attributable Fraction (PAF) is the the proportion of cases for an outcome that can be attributed to the pollutant among the entire population",
                target='PAF',
                #is_open =True,
                trigger ='hover focus legacy'
            )
    td= dbc.Tooltip(
                "Annual cases for an outcome attributable to the pollutant",
                target='Cases',
                #is_open =True,
                trigger ='hover focus legacy'
            )
    ts= dbc.Tooltip(
                "Annual cases for an outcome attributable to the pollutant per 100K people",
                target='Rates',
                #is_open =True,
                trigger ='hover focus legacy'
            )
    metrics=html.Div([dbc.RadioItems(
                    id='health-metrics'+name,
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-secondary",
                    labelCheckedClassName="secondary",
                    options=[{'label': i, 'value': i, 'label_id':i} for i in ['Concentration','PAF','Cases','Rates']],                
                    value='Concentration',
                    labelStyle={'display': 'inline-block'}
                ),tt,td,ts])
    return metrics

def details_tip(tar):
    tt= dbc.Tooltip(
                "Click Open Details for more information on the compenents of the webpage.",
                target=tar,
                #is_open =True,
                trigger ='hover focus legacy'
            )
    return tt

def c40():
    city_drop = html.Div(dcc.Dropdown(
                    id='membsDrop',
                    options=['Global Covenant of Mayors','Breathe Life 2030','Climate Mayors (US ONLY)','Carbon Neutral Cities Alliance ','Resilient Cities Network','C40','All Memberships', 'Number of Memberships'],
                    value='C40',
                ),className='single-dropd')

    return city_drop
def members():
    C40 = dbc.RadioItems(
                    id='c40-toggle',
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-secondary",
                    labelCheckedClassName="secondary",
                    options=[{'label': i, 'value': i} for i in ['Members','All Cities']],                
                    value='Members',
                    labelStyle={'display': 'inline-block'}
                )
    return C40

def instruct(ids):
    inst = html.Div([html.Div(dbc.Button(children="Open Details", id=ids, n_clicks=0,
                   color='primary'), className = 'd-grid mx-auto'),
                    dbc.Tooltip(
                        children ="Click Open Details for more information on the compenents of the webpage.",
                        id = ids+'tt',
                        target=ids,
                        is_open =True,
                        trigger ='hover focus legacy'
                    )]
                   )
    return inst

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