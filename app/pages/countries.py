import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback
from dash.dependencies import Input, Output,State
from dash import dcc
from dash import html
import plotly.io as pio
import dash
import copy
import dash_bootstrap_components as dbc

dash.register_page(__name__)

df = pd.read_csv('./pages/unified_data_SR.csv')
pol = ['NO2','O3','PM','CO2']
units={'CO2':'CO<sub>2</sub> (tonnes)','NO2': 'NO<sub>2</sub> (ppb)','O3':'O<sub>3</sub> (ppb)','PM': 'PM (μg/m<sup>3</sup>)',"Population":''}

import dash.dependencies
pio.templates.default = "simple_white"

def w_avg(df, values, weights):
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()
## Filter df
ds= df.query('Year <2005')
da = df.query('Year>=2005')
##Find 0 values in 2000
s =df.query('Year ==2000 & NO2==0')
ds.loc[(ds['ID'].isin(s.ID)),('NO2')] =np.nan
ds.loc[(ds.ID ==923),('NO2')]=np.nan
dfilt = pd.concat([ds,da])

#dfilt['CityCountry'] = dfilt.City + ', ' + dfilt.Country + ' (' +dfilt.ID.apply(int).apply(str) +')'


def find_stats(dataframe):
    me = dataframe.groupby(['Country','Year']).mean(numeric_only=True)[['Population','PM','O3','NO2','CO2','Latitude','Longitude']].round(decimals= 2)
    dd = dataframe[['Country','Year','Population','O3','NO2','PM','CO2']].dropna()
    me['w_NO2']=dd.groupby(['Country','Year']).apply(w_avg,'NO2','Population')
    me['w_PM']=dd.groupby(['Country','Year']).apply(w_avg,'PM','Population')
    me['w_O3']=dd.groupby(['Country','Year']).apply(w_avg,'O3','Population')
    me['w_CO2']=dd.groupby(['Country','Year']).apply(w_avg,'CO2','Population')
    me.Population = me.Population.round(decimals=-3)
    me = me.reset_index()
    #me['iso'] = coco.convert(names=me.Country,to='ISO3')

    _ma = dataframe.groupby(['Country','Year']).max(numeric_only=True)[['Population','PM','O3','NO2','CO2','Latitude','Longitude']].round(decimals = 2)
    _ma.Population = me.Population
    _ma = _ma.reset_index()

    _mi = dataframe.groupby(['Country','Year']).min(numeric_only=True)[['Population','PM','O3','NO2','CO2','Latitude','Longitude']].round(decimals = 2)
    _mi.Population = me.Population
    _mi = _mi.reset_index()
    return me,_ma,_mi

mean, _max, _min = find_stats(df)
fmean,fmax,fmin = find_stats(dfilt)

pd.options.plotting.backend = "plotly"

colors = {
    'background': 'white',
    'text': '#123C69',
    'subtext': '#6a8099'
}


available_indicators = ['O3','PM','NO2','CO2','w_O3','w_PM','w_NO2','w_CO2']
pol_buttons = dbc.Stack([dbc.RadioItems(
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
            ),
            dbc.RadioItems(
                    id='crossfilter-data-type',
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-secondary",
                    labelCheckedClassName="secondary",
                    options=[{'label': i, 'value': i} for i in ['Population Weighted', 'Unweighted']],
                    value='Unweighted',
                    labelStyle={'display': 'inline-block'}
                )
            ],className="radio-group")
main_graph =dcc.Graph(
            id='shaded-map',
            hoverData={'points': [{'customdata': 'United States'}]}
        )

graph_stack =dbc.Stack([
        dcc.Graph(id='cities-scatter', hoverData={'points': [{'hovertext': 'Washington D.C., United States (860)'}]}),
        dcc.Graph(id='country-trends-graph'),
    ])
slider =dcc.Slider(
        id='crossfilter-year--slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=df['Year'].max(),
        marks={str(year): str(year) for year in df['Year'].unique()},
        step=None
    )
country_drop = dcc.Dropdown(
                    id='country-s',
                    options=sorted(df["Country"].unique()),
                    value='United States',
                )
city_drop = dcc.Dropdown(
                    id='city-s',
                    options=sorted(df["CityCountry"].unique()),
                    value='Washington D.C., United States (860)',
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
                html.P(   
                    children="Select whether you would like to see the simple (unweighted) mean or the population weighted mean weighted by the population of each city within the state.",style ={'color':colors['subtext']}
                ),
                html.H5(children='Region',style ={'color':colors['text']}),
                 html.P(children=   
                    "Select the region to display: United States, India or China.",style ={'color':colors['subtext']}
                ),
                 html.H5(children='Population Axis',style ={'color':colors['text']}),
                 html.P(children=   
                    "Select whether you want the population data to be displayed with a logarithmic or linear axis using the center buttons",style ={'color':colors['subtext']}
                ),
                html.H5(children='Select a Country',style ={'color':colors['text']},),
                html.P(children=
                    "Explore the countries by hovering over the map on the left. The graph on the upper right will populate with a scatter plot of cities within the country that is selected on the left. Alternatively, select a country by clicking or searching in the first dropdown menu; your selection will be highlighted on the map and the cities within it will be plotted on the upper right-hand side. ",style ={'color':colors['subtext']}),
                html.H5(children='Select a City',style ={'color':colors['text']},),
                html.P(children=
                    "Explore the cities by hovering over the graph on the upper right. The city your mouse is closest to will highlight and plot as an orange line in the bottom right graph. Alternatively, select a city of interest by clicking or searching in the second dropdown menu; your selection will be highlighted on the scatter plot and plotted on the lower right-hand side.",style ={'color':colors['subtext']}),
                html.H5(children='Countrywide Trends',style ={'color':colors['text']},),
                html.P(children=
                    "The bottom right graph is a timeseries that compares the country mean (teal) concentration and the selected city trend (orange). The light gray lines indicate the minimum and maximum concentration values of the states over time. Hover over the graph to see the values.",style ={'color':colors['subtext']}),
                html.H5(children='Select a Year',style ={'color':colors['text']},),
                html.P(children=
                    "Choose which year of data to visualize with the year slider on the bottom.",style ={'color':colors['subtext']},)],
                id="offcanvas-countries",
                style ={'color':colors['text'],'font-size':'xlarge'},
                title="More Information",
                backdrop=False,
                is_open=False,
                autofocus=False,
                placement='end'
            )])

layout =dbc.Container([dbc.Row([dbc.Col(off_canva,width=2),
        dbc.Col(html.Div(style={'backgroundColor': colors['background']}, children=[
            html.H1(
                children='Map of Mean Concentration',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],'font':'helvetica','font-weight': 'bold'
                    
                }
            ),

            html.Div(children='Exploring Countrywide Trends', style={
                'textAlign': 'center','font':'helvetica',
                'color': colors['subtext']
            })])),dbc.Col(width=2)]),
    dbc.Row([dbc.Col(pol_buttons,width=4),dbc.Col(lin_log,className="radio-group",width=2),dbc.Col(country_drop,width=2),dbc.Col(city_drop,className="radio-group",width=4)]),
    dbc.Row([dbc.Col(main_graph,width=7),dbc.Col(graph_stack,width=5)]),
    dbc.Row(slider)],fluid=True)

@callback(
    Output("offcanvas-countries", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas-countries", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

@callback(
    Output("city-s", "options"),
    Input("country-s", "value"),
)
def chained_callback_city(country):

    dff = copy.deepcopy(df)

    if country is not None:
        dff = dff.query("Country == @country")

    return sorted(dff["CityCountry"].unique())


@callback(
    dash.dependencies.Output('shaded-map', 'figure'),
    [
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-data-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value'),
        Input('country-s','value')
     ])


def update_graph(yaxis_column_name,
                 xaxis_type, data_type,
                 year_value,countryS):
    m = fmean.query('Year == @year_value').copy()
    if data_type =='Population Weighted':
        yaxis_column_name = 'w_'+yaxis_column_name
    for i in pol:
        if i in yaxis_column_name:
            unit_s = i
    #m = m.query('@pop_limit[0] < Population <@pop_limit[1]')
    if yaxis_column_name=='CO2':
        maxx= 5e6
        m['text'] = '<b>'+m['Country'] + '</b><br>'+units[unit_s]+': '+ round((m[yaxis_column_name].astype(float)/1000000),3).astype(str) + 'M'
    else:
        m['text'] = '<b>'+m['Country'] + '</b><br>'+units[unit_s]+': '+ m[yaxis_column_name].round(2).astype(str)
        maxx=m[yaxis_column_name].max()
    ctry = m.query('Country ==@countryS')
    fig = go.Figure(data=go.Choropleth(locations = m['Country'],locationmode = 'country names',customdata=m['Country'],
            #hoverlabel=m['Country'],
            z = m[yaxis_column_name],hovertext=m['text'],hoverinfo='text',
                        colorscale='OrRd',
                        zmin=0,
                       zmax=maxx))
    fig.add_traces(data=go.Choropleth(locations = ctry['Country'],locationmode = 'country names',
            #hoverlabel=m['Country'],
            z = ctry[yaxis_column_name],hoverinfo='skip',
                        colorscale='OrRd',
                        zmin=0,
                       zmax=maxx,marker = dict(line_width=3)))

    #fig.update_layout(legend=dict(groupclick="toggleitem"))

        
    fig.update_layout(legend_title_text='',paper_bgcolor= colors['background'],plot_bgcolor=colors['background'])


    #fig.update_traces(customdata=m['Country'])
    
    #fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig


def create_time_series(city,means, title, cityname, axiscol_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x= means.Year, y=means.Maximum, name = 'Maximum', 
                             marker = {'color':'lightgray'},line= {'color':'lightgray'},
        showlegend=True))
    fig.add_trace(go.Scatter(x= means.Year, y=means[axiscol_name], name = 'Mean', 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391'},
        showlegend=True))
    fig.add_trace(go.Scatter(x= means.Year, y=means['w_'+axiscol_name].round(decimals= 2), name = 'Wgt. Mean',opacity=0.7, 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391','dash':'dash'},
        showlegend=True))
    fig.add_trace(go.Scatter(x= means.Year, y=means.Minimum, name = 'Minimum', 
                             marker = {'color':'lightgray'},line= {'color':'lightgray'},
        showlegend=True))
    fig.add_trace(go.Scatter(x= means.Year, y=city.round(decimals= 2), name = cityname, 
                             marker = {'color':'#CC5500'},line= {'color':'#CC5500'},
        showlegend=False))
    
    # px.scatter(means, x= 'Year',y= ['Maximum',axiscol_name,'Minimum'],
    #                  color_discrete_sequence=['lightgray','red','lightgray'])

    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode="x unified",paper_bgcolor= colors['background'],plot_bgcolor=colors['background'],legend=dict(
        y=1,
        x=1))
    #fig.update_xaxes(showgrid=False)

    fig.update_yaxes(title=units[axiscol_name])
    
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)

    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

@callback(
    dash.dependencies.Output('cities-scatter', 'figure'),
    [dash.dependencies.Input('shaded-map', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-data-type', 'value'),
     Input('crossfilter-year--slider','value'),
    Input('country-s','value'),
    Input('city-s','value')])
def update_y_timeseries(hoverData, yaxis_column_name, xaxis_type,data_type,year_value,countryS,cityS):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    country_name = hoverData['points'][0]['customdata'] if input_id == 'shaded-map' else countryS
    dff = dfilt[dfilt['Country']==country_name]
    dff = dff.query('Year ==@year_value')
    city_df = dff.query('CityCountry ==@cityS')
    title = '<b>{}</b><br>'.format(country_name)
    fig = px.scatter(dff, x='Population',
            y=yaxis_column_name,
            hover_name='CityCountry',
            symbol = 'c40',
            color='c40',
            hover_data={'c40':False},
            #opacity = 0.4,
            symbol_map = {'not_c40':'circle','c40':'star'},
            color_discrete_map= {'not_c40':'rgba(76, 179, 145,0.8)','c40':'rgba(30, 49, 133,0.9)'}
            ) 
    fig.add_trace(
        go.Scattergl(
            mode='markers',
            x=city_df['Population'],
            y=city_df[yaxis_column_name],
            opacity=1,
            marker=dict(
                symbol='circle-open-dot',
                color='#FAED26',
                size=10,
                line=dict(
                    width=2
            )
            ),
            showlegend=False,
            hoverinfo='skip'
        )
    )
    
    fig.update_xaxes(title='Population', type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=units[yaxis_column_name])
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    fig.update_layout(height = 225, margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    fig.update_layout(legend_title_text='',legend_x=1, legend_y=0,paper_bgcolor= colors['background'],plot_bgcolor=colors['background'])

    return fig

@callback(
    dash.dependencies.Output('country-trends-graph', 'figure'),
    [dash.dependencies.Input('cities-scatter','hoverData'),
    dash.dependencies.Input('country-s', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-data-type', 'value'),
    Input('city-s','value')])
def update_x_timeseries(cityName, countryS, yaxis_column_name, data_type,cityS):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    city_sel = cityName['points'][0]['hovertext'] if input_id == 'cities-scatter' else cityS
    
    city = dfilt[dfilt.CityCountry ==city_sel][yaxis_column_name]
    country_name = countryS
    _df = fmean[fmean['Country'] == country_name][['Year',yaxis_column_name,'w_'+yaxis_column_name]]
    _df['Minimum'] = fmin[fmin['Country'] == country_name][yaxis_column_name]
    _df['Maximum'] = fmax[fmax['Country'] == country_name][yaxis_column_name]
    
    return create_time_series(city,_df, country_name,city_sel,yaxis_column_name)


@callback(
    Output("country-s", "value"),
    Input("country-s", "value"),
    Input('shaded-map', 'hoverData')
)
def sync_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'] if input_id == 'shaded-map' else city_sel
    return value

@callback(
    Output("city-s", "value"),
    Input("city-s", "value"),
    Input('cities-scatter', 'hoverData')
)
def sync_city_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['hovertext'] if input_id == 'cities-scatter' else city_sel
    return value