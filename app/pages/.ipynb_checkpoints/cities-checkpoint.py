import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback
from dash.dependencies import Input, Output,State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

import dash

dash.register_page(__name__)
df = pd.read_csv('./pages/unified_data_SR.csv')

ds= df.query('Year <2005')
da = df.query('Year>=2005')
##Find 0 values in 2000
s =df.query('Year ==2000 & NO2==0')
ds.loc[(ds['ID'].isin(s.ID)),('NO2')] =np.nan
dfilt = pd.concat([ds,da])

cont_l = df.continent.dropna().unique()
units={'CO2':'CO<sub>2</sub> (tonnes)','NO2': 'NO<sub>2</sub> (ppb)','O3':'O<sub>3</sub> (ppb)','PM': 'PM (μg/m<sup>3</sup>)',"Population":''}
#formats ={'CO2':'CO<sub>2</sub>','NO2': 'NO<sub>2</sub>','O3':'O<sub>3</sub>','PM': 'PM',"Population":''}

colors = [["#58a862","#00e81d"],
["#9466c9","#7905ff"],
["#9b9c3b","#f0f216"],
["#c75a8e","#f20c7a"],
["#c98443","#ff7d03"],
["#cb4f42","#ff260f"],
["#6295cd","#6295cd"]]
cont_dict = {}
for i in range(len(cont_l)):
    cont_dict[cont_l[i]]=colors[i]

import dash.dependencies


pd.options.plotting.backend = "plotly"

available_indicators = ['O3','PM','NO2','CO2']

colors = {
    'background': 'white',
    'text': '#123c69',
    'subtext': '#6a8099'
}

pol_buttons=dbc.RadioItems(
                id="crossfilter-yaxis-column",
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
lin_log=dbc.RadioItems(
                id='crossfilter-xaxis-type',
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-secondary",
                labelCheckedClassName="secondary",
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],                
                value='Log',
                labelStyle={'display': 'inline-block'}
            )

off_canva = dbc.Stack([dbc.Button("Details", id="open-offcanvas", n_clicks=0,
                   color='secondary'),
                       dbc.Offcanvas([
                 html.H5(children='Pollutant',style ={'color':colors['text']},),
                 html.P(   
                    children="Select the pollutant to visualize with the buttons on the left",style ={'color':colors['subtext']}
                ),
                 html.H5(children='Population Axis',style ={'color':colors['text']}),
                 html.P(children=   
                    "Select whether you want the population data to be displayed with a logarithmic or linear axis using the center buttons",style ={'color':colors['subtext']}
                ),
                html.H5(children='Select a City',style ={'color':colors['text']},),
                html.P(children=
                    "Explore the cities by hovering over the graph on the left. The city your mouse is closest to will populate the population and time series plots on the right. Alternatively, select a city of interest by clicking or searching in the dropdown menu; your selection will be highlighted on the scatter plot and plotted on the right-hand side. ",style ={'color':colors['subtext']}),
                html.H5(children='Select a Year',style ={'color':colors['text']},),
                html.P(children=
                    "Choose which year of data to visualize with the year slider on the bottom.",style ={'color':colors['subtext']},)],
                id="offcanvas",
                style ={'color':colors['text']},
                title="More Information",
                backdrop=False,
                is_open=False,
                autofocus=False,
                placement='end'
            )])

city_drop = html.Div(dcc.Dropdown(
                    id='CityS',
                    options=sorted(df["CityCountry"].unique()),
                    value='Tokyo, Japan (13017)',
                ),className='single-dropd')
cont_drop = html.Div(dcc.Dropdown(
            id="ContS",
            value=list(cont_l.astype(str)),
            options=list(cont_l.astype(str)),
            multi=True,
        ),className="custom-dropdown")
sliders =  dbc.Stack([dcc.Slider(
        id='crossfilter-year--slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=df['Year'].max(),
        marks={str(year): str(year) for year in df['Year'].unique()},
        step=None
    )])
                      
main_graph = dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'Tokyo, Japan (13017)'}]}
        )                        
graph_stack = dbc.Stack([dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series')])

        
layout =dbc.Container([dbc.Row([dbc.Col(off_canva,width=2),
        dbc.Col(
            html.Div(style={'backgroundColor': colors['background']}, children=[html.H1(children='Cities Scatter Plot', style={'textAlign': 'center','color': colors['text'],'font':'helvetica','font-weight': 'bold'}),html.Div(children='Exploring Individual Cities', style={'textAlign': 'center','color': colors['subtext'],'font':'helvetica'})]),width={"offset": 2}),dbc.Col()]),
    dbc.Row([dbc.Col(pol_buttons,className="radio-group",width=2),dbc.Col(lin_log,className="radio-group",width=2),dbc.Col(cont_drop,width=8)]),dbc.Row(dbc.Col(city_drop,width={'offset':9})),dbc.Row(),
    dbc.Row([dbc.Col(main_graph,width=7),dbc.Col(graph_stack,width=5)]),
    dbc.Row(sliders)],fluid=True)

@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

@callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),

    [
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value'),
    dash.dependencies.Input('CityS', 'value'),
        dash.dependencies.Input('ContS','value')
     ])


def update_graph(yaxis_column_name,
                 xaxis_type,
                 year_value,cityS,contS):
    dff =dfilt.query('Year == @year_value').copy()
    city_df = dff.query('CityCountry ==@cityS').copy()
    
    c='c40'
    nc='not_c40'
    #nc=dff[dff['c40']=='not_c40']
    plot = []
    for i in contS:
        _c=dff.query('c40 ==@c & continent==@i')
        plot.append(go.Scatter(name = i, legendgroup= c,legendgrouptitle={'text':'C40 Cities'}, x=_c['Population'], y=_c[yaxis_column_name], mode='markers',
                               customdata=_c['CityCountry'],
                               hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br>' + f'{units[yaxis_column_name]}: '+'%{y}',
                              marker={'color':cont_dict[i][1], 'symbol':'star','size':10,'line':dict(width=0.8,
                                        color=colors['background'])}))
        _nc=dff.query('c40 ==@nc & continent==@i')
        plot.append(go.Scatter(name = i, legendgroup= nc, legendgrouptitle= {'text':'Other Cities'}, x=_nc['Population'],y=_nc[yaxis_column_name],mode='markers',customdata=_nc['CityCountry'],hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br> ' + f'{units[yaxis_column_name]}: '+ '%{y}',
                              marker={'color':cont_dict[i][1],'opacity':0.2}))
    fig =go.Figure(data=plot)

    fig.update_layout(legend=dict(groupclick="toggleitem"))
  
    fig.update_layout(legend_title_text='',paper_bgcolor= colors['background'],plot_bgcolor=colors['background'])
    fig.add_trace(
        go.Scattergl(
            mode='markers',
            x=city_df['Population'],
            y=city_df[yaxis_column_name],
            opacity=1,
            marker=dict(
                symbol='circle-dot',
                color='#FAED26',
                #size=11,
                size=11,
                line=dict(
                        color=colors['text'],
                        width=2
                ),
            ),
            showlegend=False,
            hoverinfo='skip'
        )
    )    
    fig.update_xaxes(title='Population', type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=units[yaxis_column_name])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    
    return fig


def create_time_series(dff, axis_type, title, axiscol_name):

    fig = px.scatter(dff, x='Year', y=axiscol_name, template='simple_white')

    fig.update_traces(mode='lines+markers')

    fig.update_xaxes(showgrid=False)

    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log',title = units[axiscol_name])

    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)

    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10},paper_bgcolor=colors['background'], plot_bgcolor=colors['background'])
    return fig
@callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
    dash.dependencies.Input('CityS', 'value')])
def update_y_timeseries(hoverData, axis_type,city_sel):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = hoverData['points'][0]['customdata'] if input_id == 'crossfilter-indicator-scatter' else city_sel
    dff = dfilt[dfilt['CityCountry'] == city_sel] 
    country_name = dff['CityCountry'].iloc[0]
    title = '<b>{}</b><br>{}'.format(country_name, 'Population')
    return create_time_series(dff, axis_type, title, 'Population')


@callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('CityS', 'value')
     ])
def update_x_timeseries(hoverData, yaxis_column_name,city_sel):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = hoverData['points'][0]['customdata'] if input_id == 'crossfilter-indicator-scatter' else city_sel
    dff = dfilt[dfilt['CityCountry'] == city_sel] 
    country_name = dff['CityCountry'].iloc[0]
    return create_time_series(dff, 'Linear', country_name,yaxis_column_name)

@callback(
    Output("CityS", "value"),
    Input("CityS", "value"),
    Input('crossfilter-indicator-scatter', 'hoverData')
)
def sync_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'] if input_id == 'crossfilter-indicator-scatter' else city_sel
    return value