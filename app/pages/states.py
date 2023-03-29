import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback
from dash.dependencies import Input, Output
import dash.dependencies
from dash import dcc
from dash import html
import plotly.io as pio
import dash
import json
import pickle

dash.register_page(__name__)

countries = ['United States','China','India']
df = pd.read_csv('./pages/updated_unified_data.csv')
states_df ={}
for i in countries:
    states_df[i] = pd.read_csv('./pages/geojs/IDtoState'+i+'.csv')

c_gjson={}
c_gjson['China']= json.load(open("./pages/geojs/states_china.geojson", "r"))
c_gjson['India']= json.load(open("./pages/geojs/states_india.geojson", "r"))
id_dict={}
with open('./pages/geojs/chinadict.pickle', 'rb') as handle:
    id_dict['China'] = pickle.load(handle)
c40 = pd.read_excel('./pages/cityid-c40_crosswalk.xlsx')
ID_pop = df[df['Year']==2019][['ID','Population']]
c40_p = c40.merge(ID_pop, how = 'left', left_on = 'city_id', right_on ='ID')
total = c40_p[['ID','c40','continent']].merge(df, how = 'right', on ='ID')

## Filter df
ds= total.query('Year <2005')
da = total.query('Year>=2005')
##Find 0 values in 2000
s =total.query('Year ==2000 & NO2==0')
ds.loc[(ds['ID'].isin(s.ID)),('NO2')] =np.nan
ds.loc[(ds.ID ==923),('NO2')]=np.nan
##use the filtered dataset throughout
total = pd.concat([ds,da])

#df['CityState'] = df.City + ', ' + df.State + ' (' +df.ID.apply(int).apply(str) +')'
pol = ['NO2','O3','PM']


pio.templates.default = "plotly_white"

def w_avg(df, values, weights):
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()


def find_stats(dataframe):
    me = dataframe.groupby(['State','Year']).mean(numeric_only=True)[['Population','PM','O3','NO2']].round(decimals= 2)
    dd = dataframe[['State','Year','Population','O3','NO2','PM']].dropna()
    me['w_NO2']=dd.groupby(['State','Year']).apply(w_avg,'NO2','Population')
    me['w_PM']=dd.groupby(['State','Year']).apply(w_avg,'PM','Population')
    me['w_O3']=dd.groupby(['State','Year']).apply(w_avg,'O3','Population')
    me.Population = me.Population.round(decimals=-3)
    me = me.reset_index()

    _ma = dataframe.groupby(['State','Year']).max(numeric_only=True)[['Population','PM','O3','NO2']].round(decimals = 2)
    _ma.Population = me.Population
    _ma = _ma.reset_index()

    _mi = dataframe.groupby(['State','Year']).min(numeric_only=True)[['Population','PM','O3','NO2']].round(decimals = 2)
    _mi.Population = me.Population
    _mi = _mi.reset_index()
    _co = dataframe.groupby(['State','Year']).count()[['Population','PM','O3','NO2']]
    _co = _co.reset_index()
    return me,_ma,_mi,_co

df = {}
mean_df = {}
stats ={}
for i in countries:
    df[i] = total.query('Country ==@i')[['ID','City','c40','Year','Population','NO2','PM','O3']]
    df[i] = df[i].merge(states_df[i][['ID','State']], how='left',on='ID')
    if i =='China':
        df[i] = df[i][df[i].State != '자강도']
        df[i]["State"] = df[i]["State"].apply(lambda x: id_dict[i][x])
    mean, _max, _min,count = find_stats(df[i])
    stats[i]={'mean':mean,'min':_min,'max':_max,'count':count}
    mean_df[i] = df[i].groupby('Year')[['NO2','PM','O3']].mean().reset_index()
    
#fmean,fmax,fmin,fcount = find_stats(dfilt)

pd.options.plotting.backend = "plotly"

colors = {
    'background': 'white',
    'text': '#468570'
}


available_indicators = ['O3','PM','NO2','w_O3','w_PM','w_NO2']
layout = html.Div([
    html.Div([
        html.Div(style={'backgroundColor': colors['background']}, children=[
            html.H1(
                children='Map of Mean State Concentration',
                style={
                    'textAlign': 'center',
                    'color': 'black'
                }
            ),

            html.Div(children='Exploring Statewide Trends', style={
                'textAlign': 'center',
                'color': 'lightgray'
            })]),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='NO2'
            ),
            dcc.RadioItems(
                id='crossfilter-data-type',
                options=[{'label': i, 'value': i} for i in ['Filtered']],
                value='Filtered',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='region-selection',
                options=[{'label': i, 'value': i}for i in countries],
                value='United States'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],                
                value='Log',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'white',
        'backgroundColor': 'white',
        'padding': '10px 5px'
    }),
    

    html.Div([
        dcc.Graph(
            id='shaded-states',
            hoverData={'points': [{'hovertext': 'CA'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='states-scatter', hoverData={'points': [{'hovertext': 'Los Angeles'}]}),
        dcc.Graph(id='State-trends-graph'),
    ], style={'display': 'inline-block', 'width': '49%'}),

    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=df['United States']['Year'].min(),
        max=df['United States']['Year'].max(),
        value=df['United States']['Year'].max(),
        marks={str(year): str(year) for year in df['United States']['Year'].unique()},
        step=None
    ), style={'width': '95%', 'padding': '0px 20px 20px 20px'})
])

@callback(
    dash.dependencies.Output('shaded-states', 'figure'),
    [dash.dependencies.Input('region-selection', 'value'),
    dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value'),
     ])


def update_graph(region,yaxis_column_name,
                 xaxis_type,
                 year_value):
    m = stats[region]['mean'].query('Year == @year_value')
    #m = m.query('@pop_limit[0] < Population <@pop_limit[1]')
    if region == 'United States':
        fig = px.choropleth(m, locationmode="USA-states",locations = 'State', scope = 'usa',
                hover_name='State',
                color = yaxis_column_name, color_continuous_scale='OrRd')
    elif region =='China':
        fig = px.choropleth(m,locations="State", geojson=c_gjson[region], scope = 'asia',color=yaxis_column_name,
                           hover_name="State",featureidkey='properties.NAME_1', hover_data={'State':False},
                           color_continuous_scale='OrRd')
        fig.update_geos(fitbounds='locations',visible=False)
    elif region =='India':
        fig = px.choropleth(m,locations="State", geojson=c_gjson[region], scope = 'asia',color=yaxis_column_name,
                           hover_name="State",featureidkey='properties.st_nm', hover_data={'State':False},
                           color_continuous_scale='OrRd')
        fig.update_geos(fitbounds='locations',visible=False)
    #fig.update_layout(legend=dict(groupclick="toggleitem"))

        
    fig.update_layout(legend_title_text='')


    fig.update_traces(customdata=m['State'])
    
    #fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig


def create_time_series(region,city,means, title, cityname, axiscol_name):
    fig = go.Figure()
    if means.Count.mean() < 3:
        fig.add_trace(go.Scatter(x= means.Year, y=means[axiscol_name], name = 'Mean '+axiscol_name, 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391'},
        showlegend=False))
        fig.add_trace(go.Scatter(x= means.Year, y=means['w_'+axiscol_name].round(decimals= 2), name = 'Pop-W Mean '+axiscol_name,opacity=0.7, 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391','dash':'dash'},
        showlegend=False))
        fig.add_trace(go.Scatter(x= mean_df[region].Year, y=mean_df[region][axiscol_name].round(decimals= 2), name = 'Country Mean '+axiscol_name, 
                                 marker = {'color':'black'},line= {'color':'black','dash':'dot'},
                                 showlegend=False))
    else:    
        fig.add_trace(go.Scatter(x= means.Year, y=means.Maximum, name = 'Maximum', 
                                 marker = {'color':'lightgray'},line= {'color':'lightgray'},
            showlegend=False))
        fig.add_trace(go.Scatter(x= means.Year, y=means[axiscol_name], name = 'Mean '+axiscol_name, 
                                 marker = {'color':'#4CB391'},line= {'color':'#4CB391'},
            showlegend=False))

        fig.add_trace(go.Scatter(x= means.Year, y=means['w_'+axiscol_name].round(decimals= 2), name = 'Pop-W Mean '+axiscol_name,opacity=0.7, 
                                 marker = {'color':'#4CB391'},line= {'color':'#4CB391','dash':'dash'},
            showlegend=False))
        fig.add_trace(go.Scatter(x= means.Year, y=means.Minimum, name = 'Minimum', 
                                 marker = {'color':'lightgray'},line= {'color':'lightgray'},
            showlegend=False))
        fig.add_trace(go.Scatter(x= means.Year, y=city.round(decimals= 2), name = cityname, 
                                 marker = {'color':'#CC5500'},line= {'color':'#CC5500'},
            showlegend=False))
        fig.add_trace(go.Scatter(x= mean_df[region].Year, y=mean_df[region][axiscol_name].round(decimals= 2), name = 'Country Mean '+axiscol_name, 
                                 marker = {'color':'black'},line= {'color':'black','dash':'dot'},
            showlegend=False))

    # px.scatter(means, x= 'Year',y= ['Maximum',axiscol_name,'Minimum'],
    #                  color_discrete_sequence=['lightgray','red','lightgray'])

    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode="x unified")
    #fig.update_xaxes(showgrid=False)

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
     Input('crossfilter-year--slider','value')])
def update_y_timeseries(region,hoverData, yaxis_column_name, xaxis_type,year_value):
    
    for i in pol:
        if i in yaxis_column_name:
            yaxis_column_name = i
   
    dff = df[region][df[region]['State']==hoverData['points'][0]['hovertext']]
    dff = dff.query('Year ==@year_value')
    State_name = hoverData['points'][0]['hovertext']
    title = '<b>{}</b><br>{}'.format(State_name, yaxis_column_name)
    fig = px.scatter(dff, x='Population',
            y=yaxis_column_name,
            hover_name='City',
            color = 'c40',
            #opacity = 0.4,
            color_discrete_map= {'not_c40':'rgba(76, 179, 145,0.4)','c40':'rgba(30, 49, 133,0.9)'}
            )    
    #fig.update_traces(customdata=len(dff))
    fig.update_xaxes(title='Population', type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name)
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    fig.update_layout(height = 225, margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    fig.update_layout(showlegend=False)

    return fig

@callback(
    dash.dependencies.Output('State-trends-graph', 'figure'),
    [dash.dependencies.Input('region-selection', 'value'),
    dash.dependencies.Input('states-scatter','hoverData'),
    dash.dependencies.Input('shaded-states', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_x_timeseries(region,cityName, hoverData, yaxis_column_name):
    for i in pol:
        if i in yaxis_column_name:
            yaxis_column_name = i
    ds =stats[region] ##Selects the stats dict for the region
    ddf= df[region] ##Selects the dataset with the city data
    _df = ds['mean'][ds['mean']['State'] == hoverData['points'][0]['hovertext']][['Year',yaxis_column_name,'w_'+yaxis_column_name]]
    _df['Minimum'] = ds['min'][ds['min']['State'] == hoverData['points'][0]['hovertext']][yaxis_column_name]
    _df['Maximum'] = ds['max'][ds['max']['State'] == hoverData['points'][0]['hovertext']][yaxis_column_name]
    _df['Count'] = ds['count'][ds['count']['State'] == hoverData['points'][0]['hovertext']][yaxis_column_name]
    city = ddf[ddf.City==cityName['points'][0]['hovertext']][yaxis_column_name]
    State_name = hoverData['points'][0]['hovertext']
    city_name = cityName['points'][0]['hovertext']
    return create_time_series(region,city,_df, State_name,city_name,yaxis_column_name)
