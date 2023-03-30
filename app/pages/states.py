import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output,State
import dash.dependencies
from dash import dcc
from dash import html
import plotly.io as pio
import dash
import json
import pickle

dash.register_page(__name__)

countries = ['United States','China','India']
df = pd.read_csv('./pages/unified_data_SR.csv')
#df['CO2']= df['CO2']/2000
states_df ={}
for i in countries:
    states_df[i] = pd.read_csv('./pages/geojs/IDtoState'+i+'.csv')
units={'CO2':'CO<sub>2</sub> (tonnes)','NO2': 'NO<sub>2</sub> (ppb)','O3':'O<sub>3</sub> (ppb)','PM': 'PM (μg/m<sup>3</sup>)',"Population":''}

c_gjson={}
c_gjson['China']= json.load(open("./pages/geojs/states_china.geojson", "r"))
c_gjson['India']= json.load(open("./pages/geojs/states_india.geojson", "r"))
id_dict={}
with open('./pages/geojs/chinadict.pickle', 'rb') as handle:
    id_dict['China'] = pickle.load(handle)


## Filter df
ds= df.query('Year <2005')
da = df.query('Year>=2005')
##Find 0 values in 2000
s =df.query('Year ==2000 & NO2==0')
ds.loc[(ds['ID'].isin(s.ID)),('NO2')] =np.nan
ds.loc[(ds.ID ==923),('NO2')]=np.nan
##use the filtered dataset throughout
total = pd.concat([ds,da])

#df['CityState'] = df.City + ', ' + df.State + ' (' +df.ID.apply(int).apply(str) +')'
pol = ['NO2','O3','PM','CO2']


#pio.templates.default = "plotly_white"

def w_avg(df, values, weights):
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()


def find_stats(dataframe):
    me = dataframe.groupby(['State','Year']).mean(numeric_only=True)[['Population','PM','O3','NO2','CO2']].round(decimals= 2)
    dd = dataframe[['State','Year','Population','O3','NO2','PM','CO2']].dropna()
    me['w_NO2']=dd.groupby(['State','Year']).apply(w_avg,'NO2','Population')
    me['w_PM']=dd.groupby(['State','Year']).apply(w_avg,'PM','Population')
    me['w_O3']=dd.groupby(['State','Year']).apply(w_avg,'O3','Population')
    me['w_CO2']=dd.groupby(['State','Year']).apply(w_avg,'CO2','Population')
    me.Population = me.Population.round(decimals=-3)
    me = me.reset_index()

    _ma = dataframe.groupby(['State','Year']).max(numeric_only=True)[['Population','PM','O3','NO2','CO2']].round(decimals = 2)
    _ma.Population = me.Population
    _ma = _ma.reset_index()

    _mi = dataframe.groupby(['State','Year']).min(numeric_only=True)[['Population','PM','O3','NO2','CO2']].round(decimals = 2)
    _mi.Population = me.Population
    _mi = _mi.reset_index()
    _co = dataframe.groupby(['State','Year']).count()[['Population','PM','O3','NO2','CO2']]
    _co = _co.reset_index()
    return me,_ma,_mi,_co

df = {}
mean_df = {}
stats ={}
for i in countries:
    df[i] = total.query('Country ==@i')[['ID','City','c40','Year','Population','NO2','PM','O3','CO2']]
    df[i] = df[i].merge(states_df[i][['ID','State']], how='left',on='ID')
    if i =='China':
        df[i] = df[i][df[i].State != '자강도']
        df[i]["State"] = df[i]["State"].apply(lambda x: id_dict[i][x])
    df[i]['CityID'] = df[i].City + ' (' +df[i].ID.apply(int).apply(str) +')'
    mean, _max, _min,count = find_stats(df[i])
    stats[i]={'mean':mean,'min':_min,'max':_max,'count':count}
    mean_df[i] = df[i].groupby('Year')[['NO2','PM','O3','CO2']].mean().reset_index()
    
#fmean,fmax,fmin,fcount = find_stats(dfilt)

pd.options.plotting.backend = "plotly"

colors = {
    'background': 'white',
    'text': '#123C69',
    'subtext': '#6a8099'
}


available_indicators = ['O3','PM','NO2','CO2','w_O3','w_PM','w_NO2','w_CO2']

pol_buttons=dbc.Stack([dbc.RadioItems(
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
                )],className="radio-group")
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

region_buttons= dbc.RadioItems(
                id='region-selection',
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-secondary",
                labelCheckedClassName="secondary",
                options=[{'label': i, 'value': i}for i in countries],
                value='United States'
            )
slider = dcc.Slider(
        id='crossfilter-year--slider',
        min=total['Year'].min(),
        max=total['Year'].max(),
        value=total['Year'].max(),
        marks={str(year): str(year) for year in total['Year'].unique()},
        step=None
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
                html.H5(children='Select a State',style ={'color':colors['text']},),
                html.P(children=
                    "Explore the states by hovering over the map on the left. The graph on the upper right will populate with a scatter plot of cities within the state that is selected on the left. Alternatively, select a state of interest by clicking or searching in the first dropdown menu; your selection will be highlighted on the map and plotted on the upper right-hand side. ",style ={'color':colors['subtext']}),
                html.H5(children='Select a City',style ={'color':colors['text']},),
                html.P(children=
                    "Explore the cities by hovering over the graph on the upper right. The city your mouse is closest to will highlight and plot as an orange line in the bottom right graph. Alternatively, select a city of interest by clicking or searching in the second dropdown menu; your selection will be highlighted on the scatter plot and plotted on the lower right-hand side.",style ={'color':colors['subtext']}),
                html.H5(children='Statewide Trends',style ={'color':colors['text']},),
                html.P(children=
                    "The bottom right graph is a timeseries that compares the statewide mean (teal) concentration with the country mean (black) and the selected city trend (orange). The light gray lines indicate the minimum and maximum concentration values of the states over time. Hover over the graph to see the values.",style ={'color':colors['subtext']}),
                html.H5(children='Select a Year',style ={'color':colors['text']},),
                html.P(children=
                    "Choose which year of data to visualize with the year slider on the bottom.",style ={'color':colors['subtext']},)],
                id="offcanvas-states",
                style ={'color':colors['text']},
                title="More Information",
                backdrop=False,
                is_open=False,
                autofocus=False,
                placement='end'
            )])

main_graph = dcc.Graph(
            id='shaded-states',
            hoverData={'points': [{'customdata': 'CA'}]}
        )

graph_stack=dbc.Stack([dcc.Graph(id='states-scatter', hoverData={'points': [{'hovertext': 'Honolulu (1)'}]}),
        dcc.Graph(id='State-trends-graph')])

state_drop = dcc.Dropdown(
                    id='state-s',
                    options=sorted(states_df['United States']['State'].unique()),
                    value='CA',
                )
city_drop = dcc.Dropdown(
                    id='city-sel',
                    options= df['United States']["CityID"].unique(),
                    value='Honolulu (1)',
                )
@callback(
    Output("state-s", "options"),
    Input("region-selection", "value"),
)
def chained_callback_state(country):
    return df[country]['State'].unique()

@callback(
    Output("city-sel", "options"),
    Input("region-selection", "value"),
    Input("state-s", "value"),
)
def chained_callback_city(country,state):
    l = df[country][df[country]['State']==state]
    return l['CityID'].unique()

@callback(
    Output("offcanvas-states", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas-states", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

layout =dbc.Container([dbc.Row([dbc.Col(off_canva,width=2),
        dbc.Col(
            html.Div(style={'backgroundColor': colors['background']}, children=[html.H1(children='Map of Mean State Concentration', style={'textAlign': 'center','color': colors['text'],'font':'helvetica','font-weight':'bold'}),html.Div(children='Exploring Statewide Trends', style={'textAlign': 'center','color': colors['subtext'],'font':'helvetica'})])),dbc.Col(width=2)]),
    dbc.Row([dbc.Col(pol_buttons,width=4),dbc.Col(dbc.Stack([region_buttons,lin_log],className="radio-group"),width=4),dbc.Col(state_drop,width=2),dbc.Col(city_drop,width=2)]),
    dbc.Row([dbc.Col(main_graph,width=7),dbc.Col(graph_stack)]),
    dbc.Row(slider)],fluid=True)




@callback(
    dash.dependencies.Output('shaded-states', 'figure'),
    [dash.dependencies.Input('region-selection', 'value'),
    dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-data-type', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value'),
     Input('state-s','value')
     ])


def update_graph(region,yaxis_column_name,data_type,
                 xaxis_type,
                 year_value,state):
    if data_type =='Population Weighted':
        yaxis_column_name = 'w_'+yaxis_column_name
    for i in pol:
        if i in yaxis_column_name:
            unit_s = i
    m = stats[region]['mean'].query('Year == @year_value').copy()
    st = m.query('State ==@state')
    if yaxis_column_name=='CO2':
        maxx= 5e6
        m['text'] = '<b>'+m['State'] + '</b><br>'+units[unit_s]+': '+ round((m[yaxis_column_name].astype(float)/1000000),3).astype(str) + 'M'
    else:
        m['text'] = '<b>'+m['State'] + '</b><br>'+units[unit_s]+': '+ m[yaxis_column_name].round(2).astype(str)
        maxx=m[yaxis_column_name].max()
    #m = m.query('@pop_limit[0] < Population <@pop_limit[1]')
    if region == 'United States':
        fig = go.Figure(data=go.Choropleth(locations = m['State'],locationmode = 'USA-states',customdata=m['State'],
            #hoverlabel=m['Country'],
            z = m[yaxis_column_name],hovertext=m['text'],hoverinfo='text',
                        colorscale='OrRd',zmin=0,zmax=maxx,
                        ))
        fig.add_traces(data=go.Choropleth(locations = st['State'],locationmode = 'USA-states',
            #hoverlabel=m['Country'],
            z = st[yaxis_column_name],hoverinfo='skip',
                        colorscale='OrRd',
                        marker = dict(line_width=3),zmin=0,zmax=maxx))
        fig.update_geos(scope='usa')
        
#         px.choropleth(m, locationmode="USA-states",locations = 'State', scope = 'usa',
#                 hover_name='State',
#                 color = yaxis_column_name, color_continuous_scale='OrRd')
    elif region =='China':
        fig = go.Figure(data=go.Choropleth(locations=m["State"], geojson=c_gjson[region],z=m[yaxis_column_name],
                           hovertext=m['text'],featureidkey='properties.NAME_1', hoverinfo='text',
                           colorscale='OrRd',zmin=0,zmax=maxx))
        fig.add_traces(data=go.Choropleth(locations = st['State'],geojson=c_gjson[region],featureidkey='properties.NAME_1',
            #hoverlabel=m['Country'],
            z = st[yaxis_column_name],hoverinfo='skip',
                        colorscale='OrRd',zmin=0,zmax=maxx,
                        marker = dict(line_width=3)))
        fig.update_geos(fitbounds='locations',visible=False)
    elif region =='India':
        fig = go.Figure(data=go.Choropleth(locations=m["State"], geojson=c_gjson[region],z=m[yaxis_column_name],
                           hovertext=m['text'],featureidkey='properties.st_nm', hoverinfo='text',
                           colorscale='OrRd',zmin=0,zmax=maxx))
        fig.add_traces(data=go.Choropleth(locations = st['State'], geojson=c_gjson[region], featureidkey='properties.st_nm',
            z = st[yaxis_column_name],hoverinfo='skip',
                        colorscale='OrRd',zmin=0,zmax=maxx,
                        marker = dict(line_width=3)))
        fig.update_geos(fitbounds='locations',visible=False)    
    fig.update_layout(legend_title_text='')


    fig.update_traces(customdata=m['State'])
    
    #fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig

##region: is country, city: city dataframe, means: state dataframe, title: state abbreviation
def create_time_series(region,city,means, title, cityname, axiscol_name):
    fig = go.Figure()
    if means.Count.mean() < 3:
        fig.add_trace(go.Scatter(x= means.Year, y=means[axiscol_name], name = 'Mean ', 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391'},
        showlegend=True))
        fig.add_trace(go.Scatter(x= means.Year, y=means['w_'+axiscol_name].round(decimals= 2), name = 'Wgt. Mean',opacity=0.7, 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391','dash':'dash'},
        showlegend=True))
        fig.add_trace(go.Scatter(x= mean_df[region].Year, y=mean_df[region][axiscol_name].round(decimals= 2), name = region, 
                                 marker = {'color':'black'},line= {'color':'black','dash':'dot'},
                                 showlegend=True))
        fig.add_trace(go.Scatter(x= means.Year, y=city.round(decimals= 2), name = cityname, 
                                 marker = {'color':'#CC5500'},line= {'color':'#CC5500'},showlegend=False))
    else:    
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
        fig.add_trace(go.Scatter(x= mean_df[region].Year, y=mean_df[region][axiscol_name].round(decimals= 2), name = region, 
                                 marker = {'color':'black'},line= {'color':'black','dash':'dot'},
            showlegend=True))

    # px.scatter(means, x= 'Year',y= ['Maximum',axiscol_name,'Minimum'],
    #                  color_discrete_sequence=['lightgray','red','lightgray'])

    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode="x unified")
    #fig.update_xaxes(showgrid=False)
    fig.update_yaxes(title=units[axiscol_name])
    #fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')

    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)

    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

@callback(
    dash.dependencies.Output('states-scatter', 'figure'),
    [dash.dependencies.Input('region-selection', 'value'),
        dash.dependencies.Input('shaded-states', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     Input('crossfilter-year--slider','value'),
    Input('state-s','value'),
    Input('city-sel','value')])
def update_y_timeseries(region,hoverData, yaxis_column_name, xaxis_type,year_value,stateS,cityS):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    state_name = hoverData['points'][0]['customdata'] if input_id == 'shaded-states' else stateS
    dff = df[region][df[region]['State']==state_name]
    dff = dff.query('Year ==@year_value')
    city_df = dff.query('CityID ==@cityS')
    title = '<b>{}</b><br>{}'.format(state_name, yaxis_column_name)
    fig = px.scatter(dff, x='Population',
            y=yaxis_column_name,
            hover_name='CityID',
            color = 'c40',
            symbol='c40',
            symbol_map = {'not_c40':'circle','c40':'star'},
            #opacity = 0.4,
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
                size=6,
                line=dict(
                    width=2
            )
            ),
            showlegend=False,
            hoverinfo='skip'
        )
    )
    #fig.update_traces(customdata=len(dff))
    fig.update_xaxes(title='Population', type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=units[yaxis_column_name])
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    fig.update_layout(height = 225, margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    fig.update_layout(legend_title_text='')

    return fig

@callback(
    dash.dependencies.Output('State-trends-graph', 'figure'),
    [dash.dependencies.Input('region-selection', 'value'),
    dash.dependencies.Input('states-scatter','hoverData'),
    dash.dependencies.Input('shaded-states', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
    Input('city-sel','value'),
    Input("state-s", "value")])
def update_x_timeseries(region,cityName, hoverData, yaxis_column_name,cityS,stateS):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = cityName['points'][0]['hovertext'] if input_id == 'states-scatter' else cityS
    ds =stats[region] ##Selects the stats dict for the region
    ddf= df[region] ##Selects the dataset with the city data
    _df = ds['mean'][ds['mean']['State'] == stateS][['Year',yaxis_column_name,'w_'+yaxis_column_name]]
    _df['Minimum'] = ds['min'][ds['min']['State'] == stateS][yaxis_column_name]
    _df['Maximum'] = ds['max'][ds['max']['State'] == stateS][yaxis_column_name]
    _df['Count'] = ds['count'][ds['count']['State'] == stateS][yaxis_column_name]
    city = ddf[ddf.CityID==city_sel][yaxis_column_name]
    return create_time_series(region,city,_df, stateS,city_sel,yaxis_column_name)

@callback(
    Output("state-s", "value"),
    Input("state-s", "value"),
    Input('shaded-states', 'hoverData')
)
def sync_input(state_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'] if input_id == 'shaded-states' else state_sel
    return value

@callback(
    Output("city-sel", "value"),
    Input("city-sel", "value"),
    Input('states-scatter', 'hoverData')
)
def sync_city_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['hovertext'] if input_id == 'states-scatter' else city_sel
    return value