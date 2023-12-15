import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback,dcc,html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output,State
import dash
from components import buttons,const,data_prep

dash.register_page(__name__)

countries = ['United States','China','India']
feature_id = {'China':'properties.NAME_1','India':'properties.st_nm'}
#Import dictionary with geojson of states
states_df =data_prep.STATES_DF

#Import dictionary with state applied dataframes
df = data_prep.DF
#Import dictionary with mean region values of pollutants
mean_df = data_prep.MEAN_DF
#Import dataframe with stats for each state
stats =data_prep.STATS
c_gjson = data_prep.GJSON
metrics = buttons.health_metrics('state')
pol_buttons=dbc.Stack([metrics,buttons.pol_buttons('state')],className="radio-group")

lin_log=html.Div(buttons.lin_log(),className ='ms-auto radio-group')
inst = buttons.instruct('open-offcanvas')
region_buttons= dbc.RadioItems(
                id='region-selection',
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-secondary",
                labelCheckedClassName="secondary",
                options=[{'label': i, 'value': i}for i in countries],
                value='United States'
            )
slider = buttons.sliders(df['China'])



off_canva = dbc.Collapse([
                       dbc.Card([
                 html.H5(children='Metric',style ={'color':const.DISP['text']},),
                 html.P(   
                    children="Select which metric to visualize. Concentration will display the pollutant concentrations, and the others will display health metrics related to each pollutant. For O3 and PM2.5, the metrics indicate premature deaths attributable to the corresponding pollutants. For NO2, the metrics indicate pediatric asthma incidence attributable to NO2. Health metrics are not available for CO2.",style ={'color':const.DISP['subtext']}
                ),
                 html.H5(children='Pollutant',style ={'color':const.DISP['text']},),
                 html.P(   
                    children="Select the pollutant to visualize with the buttons on the left. Select whether you would like to see the simple (unweighted) mean or the population weighted mean weighted by the population of each city within the state.",style ={'color':const.DISP['subtext']}
                ),
                html.H5(children='Region',style ={'color':const.DISP['text']}),
                 html.P(children=   
                    "Select the region to display: United States, India or China.",style ={'color':const.DISP['subtext']}
                ),
                 html.H5(children='Population Axis',style ={'color':const.DISP['text']}),
                 html.P(children=   
                    "Select whether you want the population data to be displayed with a logarithmic or linear axis using the center buttons",style ={'color':const.DISP['subtext']}
                ),
                html.H5(children='Select a State',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Explore the states by hovering over the map on the left. The graph on the upper right will populate with a scatter plot of cities within the state that is selected on the left. Alternatively, select a state of interest by clicking or searching in the first dropdown menu; your selection will be highlighted on the map and plotted on the upper right-hand side. ",style ={'color':const.DISP['subtext']}),
                html.H5(children='Select a City',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Explore the cities by hovering over the graph on the upper right. The city your mouse is closest to will highlight and plot as an orange line in the bottom right graph. Alternatively, select a city of interest by clicking or searching in the second dropdown menu; your selection will be highlighted on the scatter plot and plotted on the lower right-hand side.",style ={'color':const.DISP['subtext']}),
                html.H5(children='Statewide Trends',style ={'color':const.DISP['text']},),
                html.P(children=
                    "The bottom right graph is a timeseries that compares the statewide mean (teal) concentration with the country mean (black) and the selected city trend (orange). The light gray lines indicate the minimum and maximum concentration values of the states over time. Hover over the graph to see the values.",style ={'color':const.DISP['subtext']}),
                html.H5(children='Select a Year',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Choose which year of data to visualize with the year slider on the bottom.",style ={'color':const.DISP['subtext']},)],body=True
            )],id="offcanvas-states",
                style ={'color':const.DISP['text']},
                is_open=False,)

##Define graphs
main_graph = dcc.Graph(
            id='shaded-states',
            hoverData={'points': [{'customdata': 'CA'}]})
graph_stack=dbc.Stack([dcc.Graph(id='states-scatter', hoverData={'points': [{'customdata': 'Honolulu (1)'}]}),
        dcc.Graph(id='State-trends-graph')])

#Define dropdown menus
state_drop = dcc.Dropdown(
                    id='state-s',
                    options=sorted(states_df['United States']['State'].unique()),
                    value='CA')
city_drop = dcc.Dropdown(
                    id='city-sel',
                    options= sorted(df['United States']["CityID"].unique()),
                    value='Honolulu (1)')

#Update state dropdown based on selected region
@callback(
    Output("state-s", "options"),
    Output("state-s",'value', allow_duplicate=True),
    Input("region-selection", "value"),
    prevent_initial_call=True
)
def chained_callback_state(country):
    return sorted(df[country]['State'].dropna().unique()),sorted(df[country]['State'].unique())[0]


#Update city dropdown based on selected state
@callback(
    Output("city-sel", "options"),
    Output("city-sel",'value', allow_duplicate=True),
    Input("region-selection", "value"),
    Input("state-s", "value"),
    prevent_initial_call=True
)
def chained_callback_city(country,state):
    l = df[country][df[country]['State']==state]
    return sorted(l['CityID'].unique()),sorted(l['CityID'].unique())[0]

#Open offcanvas when button is clicked
@callback(
    Output("offcanvas-states", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas-states", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@callback(
    Output("open-offcanvas", "children"),
    Output("open-offcanvastt","children"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas-states", "is_open")],
)
def toggle_button(n1, is_open):
    if n1%2:
        return "Close Details", "Click Close Details to hide text."
    return "Open Details","Click Open Details for more information on the compenents of the webpage."

##Set-up layout with dbc container
layout =dbc.Container([dbc.Row([dbc.Col(width=2),
        dbc.Col(html.Div(style={'backgroundColor': const.DISP['background']}, children=[html.H1(children='Map of Mean State Concentration', style={'textAlign': 'center','color': const.DISP['text'],'font':'helvetica','font-weight':'bold'}),html.Div(children='Exploring Statewide Trends', style={'textAlign': 'center','color': const.DISP['subtext'],'font':'helvetica',})])),dbc.Col(inst,width=2),html.Hr()],align='center'),dbc.Row(dbc.Col(off_canva)), 
    dbc.Row([dbc.Col(pol_buttons,width=4),dbc.Col(dbc.Stack([region_buttons,buttons.pop_weighted('')],className="radio-group"),width=4),dbc.Col(state_drop,width=2),dbc.Col(dbc.Stack([city_drop,lin_log]),width=2)]),
    dbc.Row([dbc.Col(main_graph,width=7),dbc.Col(graph_stack,width=5)]),
    dbc.Row(slider)],fluid=True)

##Deactivates CO2 if anything but concentration is selected and vice-versa
@callback(
    [Output('health-metricsstate','options',allow_duplicate=True),
    Output('crossfilter-yaxis-columnstate','options',allow_duplicate=True)],
    [Input('crossfilter-yaxis-columnstate', 'value'),
    Input('health-metricsstate', 'value'),
    Input('crossfilter-yaxis-columnstate', 'options'),
    Input('health-metricsstate', 'options')],
    prevent_initial_call=True,
    )
def trigger_function(yaxis_col,data_type,yaxis,dtype):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id =='crossfilter-yaxis-columnstate':
        if yaxis_col == 'CO2':
            dtype = const.metric_options(True)
        else:
            dtype = const.metric_options(False)
            
    elif input_id == 'health-metricsstate':
        if data_type !='Concentration':
            yaxis = const.pol_options(True)
        else:
            yaxis = const.pol_options(False)
    return dtype,yaxis

##Function to create main map of shaded states and update based on selections
@callback(
    Output('shaded-states', 'figure'), #outputs maps
    [Input('region-selection', 'value'), #input of region (US, China, India)
    Input('crossfilter-yaxis-columnstate', 'value'), #input of pollutant
     Input('crossfilter-data-type', 'value'), #Population weighted or unweighted
     Input('crossfilter-year--slider', 'value'),
     Input('state-s','value'),
     Input('health-metricsstate','value')
     ])
def update_graph(region,pollutant,data_type,year_value,state,metric):
    unit_s = pollutant
    if metric !='Concentration':
        pollutant = metric +'_'+pollutant
    if data_type =='Population Weighted':
        pollutant = 'w_'+pollutant
    m = stats[region]['mean'].query('Year == @year_value').copy()
    st = m.query('State ==@state')
    
    if 'CO2' in pollutant:
        if data_type == 'Unweighted':
            maxx= 7e6
        else:
            maxx =50e6
        m['text'] = '<b>'+m['State'] + '</b><br>'+const.UNITS[metric][unit_s]+': '+ round((m[pollutant].astype(float)/1000000),3).astype(str) + 'M'
    else:
        m['text'] = '<b>'+m['State'] + '</b><br>'+const.UNITS[metric][unit_s]+': '+ m[pollutant].round(2).astype(str)
        if pollutant == 'Cases_NO2':
            maxx =1980
        elif pollutant == 'Cases_PM':
            maxx=250
        elif pollutant == 'Cases_O3':
            maxx=110
        else:
            maxx=m[pollutant].max()
    
    if region == 'United States':  #No outside geojson for USA so plot with plotly's internal USA-states locations
        fig = go.Figure(data=go.Choropleth(locations = m['State'],locationmode = 'USA-states',customdata=m['State'],
            z = m[pollutant],hovertext=m['text'],hoverinfo='text',
                        colorscale=const.CS[metric],zmin=0,zmax=maxx,
                        ))
        fig.add_traces(data=go.Choropleth(locations = st['State'],locationmode = 'USA-states',
            z = st[pollutant],hoverinfo='skip',
                        colorscale=const.CS[metric],
                        marker = dict(line_width=3),zmin=0,zmax=maxx))
        fig.update_geos(scope='usa')
        
    else: ##Use the uploaded geojson files for China and India states
        fig = go.Figure(data=go.Choropleth(locations=m["State"], geojson=c_gjson[region],z=m[pollutant],
                           hovertext=m['text'],featureidkey=feature_id[region], hoverinfo='text',
                           colorscale=const.CS[metric],zmin=0,zmax=maxx))
        fig.add_traces(data=go.Choropleth(locations = st['State'],geojson=c_gjson[region],featureidkey=feature_id[region],
            z = st[pollutant],hoverinfo='skip',
                        colorscale=const.CS[metric],zmin=0,zmax=maxx,
                        marker = dict(line_width=3)))
        fig.update_geos(fitbounds='locations',visible=False)
    fig.update_layout(legend_title_text='',margin={'l': 10, 'b': 10, 't': 10, 'r': 0}, hovermode='closest')
    fig.update_traces(customdata=m['State'])
    fig.update_yaxes(title=pollutant)
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family=const.FONTFAMILY
        ))
    return fig

##Function to graph the time series for statewide trends compared to national average
#region: is country, city: city dataframe, means: state dataframe, title: state abbreviation, cityname: name of selected city, axiscol_name: name of pollutant selected
def create_time_series(region,city,means, title, cityname, axiscol_name,metric):
    fig = go.Figure()
    unit_s = axiscol_name
    if axiscol_name == 'CO2':
        dec = 0
    else:
        dec=2
    if metric !='Concentration':
        axiscol_name = metric +'_'+axiscol_name
    if means.Count.mean() < 3:
        fig.add_trace(go.Scatter(x= means.Year, y=means[axiscol_name], name = 'Mean ', 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391'},
        showlegend=True))
        fig.add_trace(go.Scatter(x= means.Year, y=means['w_'+axiscol_name].round(decimals= dec), name = 'Wgt. Mean',opacity=0.7, 
                             marker = {'color':'#4CB391'},line= {'color':'#4CB391','dash':'dash'},hovertemplate ='%{y:,}',
        showlegend=True))
        fig.add_trace(go.Scatter(x= mean_df[region].Year, y=mean_df[region][axiscol_name].round(decimals= dec), name = region, 
                                 marker = {'color':'black'},line= {'color':'black','dash':'dot'},hovertemplate ='%{y:,}',
                                 showlegend=True))
        fig.add_trace(go.Scatter(x= means.Year, y=city.round(decimals= dec), name = cityname, 
                                 marker = {'color':'#CC5500'},line= {'color':'#CC5500'},hovertemplate ='%{y:,}',showlegend=True))
    else:    
        fig.add_trace(go.Scatter(x= means.Year, y=means.Maximum.round(decimals= dec), name = 'Maximum', hovertemplate ='%{y:,}',
                                 marker = {'color':'lightgray'},line= {'color':'lightgray'},
            showlegend=True))
        fig.add_trace(go.Scatter(x= means.Year, y=means[axiscol_name].round(decimals= dec), name = 'Mean', hovertemplate ='%{y:,}',
                                 marker = {'color':'#4CB391'},line= {'color':'#4CB391'},
            showlegend=True))

        fig.add_trace(go.Scatter(x= means.Year, y=means['w_'+axiscol_name].round(decimals= dec), name = 'Wgt. Mean',opacity=0.7, 
                                 marker = {'color':'#4CB391'},line= {'color':'#4CB391','dash':'dash'}, hovertemplate ='%{y:,}',
            showlegend=True))
        fig.add_trace(go.Scatter(x= means.Year, y=means.Minimum.round(decimals= dec), name = 'Minimum', hovertemplate ='%{y:,}',
                                 marker = {'color':'lightgray'},line= {'color':'lightgray'},
            showlegend=True))
        fig.add_trace(go.Scatter(x= means.Year, y=city.round(decimals= dec), name = cityname, hovertemplate = '%{y:,}',
                                 marker = {'color':'#CC5500'},line= {'color':'#CC5500'},
            showlegend=True))
        fig.add_trace(go.Scatter(x= mean_df[region].Year, y=mean_df[region][axiscol_name].round(decimals= dec), name = region, hovertemplate = '%{y:,}',marker = {'color':'black'},line= {'color':'black','dash':'dot'},
            showlegend=True))

    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode="x unified",height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    if metric != 'Concentration':
        fig.update_yaxes(title=metric)
    else:
        fig.update_yaxes(title=const.UNITS[metric][unit_s])   
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY
        ))
    return fig

@callback(
    Output('states-scatter', 'figure'),
    [Input('region-selection', 'value'),
    Input('shaded-states', 'hoverData'),
    Input('crossfilter-yaxis-columnstate', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-year--slider','value'),
    Input('state-s','value'),
    Input('city-sel','value'),
    Input('health-metricsstate','value')])
def update_y_timeseries(region,hoverData, pollutant, xaxis_type,year_value,stateS,cityS,metric):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    state_name = hoverData['points'][0]['customdata'] if input_id == 'shaded-states' else stateS
    dff = df[region][df[region]['State']==state_name]
    dff = dff.query('Year ==@year_value')
    city_df = dff.query('CityID ==@cityS')
    unit_s = pollutant
    if metric !='Concentration':
        pollutant = metric +'_'+pollutant
    title = '<b>{}</b><br>{}'.format(const.UNITS[metric][unit_s],state_name)
    plot = []
    for i in const.COUNTRY_SCATTER:
        
        _c=dff.query('C40 ==@i')
        if unit_s =='CO2':
            plot.append(go.Scatter(name = const.COUNTRY_SCATTER[i]['name'], x=_c['Population'], y=_c[unit_s], mode='markers',
                               customdata=np.stack((_c['CityID'],_c[pollutant]),axis=-1),
                               hovertemplate="<b>%{customdata[0]}</b><br>" +'Population: %{x} <br>' + f"{const.UNITS['Concentration'][unit_s]}: "+'%{y} <br>',
                              marker={'color':const.COUNTRY_SCATTER[i]['color'], 'symbol':const.COUNTRY_SCATTER[i]['symbol'],'line':dict(width=1,
                                        color=const.COUNTRY_SCATTER[i]['color'])}))
        else:
            plot.append(go.Scatter(name = const.COUNTRY_SCATTER[i]['name'], x=_c['Population'], y=_c[pollutant], mode='markers',
                                   customdata=np.stack((_c['CityID'],_c[unit_s],_c['PAF_'+unit_s],_c['Cases_'+unit_s]),axis=-1),
                                   hovertemplate="<b>%{customdata[0]}</b><br>" +'Population: %{x} <br>' + f"{const.UNITS['Concentration'][unit_s]}: "+'%{customdata[1]} <br>'+ f"{const.UNITS['PAF'][unit_s]}: "+'%{customdata[2]} <br>' + f"{const.UNITS['Cases'][unit_s]}: "+'%{customdata[2]}',
                                  marker={'color':const.COUNTRY_SCATTER[i]['color'], 'symbol':const.COUNTRY_SCATTER[i]['symbol'],'line':dict(width=1,
                                            color=const.COUNTRY_SCATTER[i]['color'])}))
    fig =go.Figure(data=plot)
    fig.add_trace(
        go.Scattergl(
            mode='markers',
            x=city_df['Population'],
            y=city_df[pollutant],
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

    fig.update_yaxes(title=metric)
    fig.add_annotation(x=0, y=0.73, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    fig.update_layout(height = 225, margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',legend_title_text='')
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY
        ))
    return fig

@callback(
    Output('State-trends-graph', 'figure'),
    [Input('region-selection', 'value'),
    Input('states-scatter','hoverData'),
    Input('shaded-states', 'hoverData'),
    Input('crossfilter-yaxis-columnstate', 'value'),
    Input('city-sel','value'),
    Input("state-s", "value"),
    Input('health-metricsstate','value')])
def update_x_timeseries(region,cityName, hoverData, pollutant,cityS,stateS,metric):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = cityName['points'][0]['customdata'][0] if input_id == 'states-scatter' else cityS
    unit_s =pollutant
    if metric !='Concentration':
        pollutant = metric +'_'+pollutant
    ds =stats[region] ##Selects the stats dict for the region
    ddf= df[region] ##Selects the dataset with the city data
    _df = ds['mean'][ds['mean']['State'] == stateS][['Year',pollutant,'w_'+pollutant]]
    _df['Minimum'] = ds['min'][ds['min']['State'] == stateS][pollutant]
    _df['Maximum'] = ds['max'][ds['max']['State'] == stateS][pollutant]
    _df['Count'] = ds['count'][ds['count']['State'] == stateS][pollutant]
    city = ddf[ddf.CityID==city_sel][pollutant]
    return create_time_series(region,city,_df, stateS,city_sel,unit_s,metric)

##Sync the states selected by hover with the dropdown menu
@callback(
    Output("state-s", "value"),
    Input("state-s", "value"),
    Input('shaded-states', 'hoverData'),
    
)
def sync_input(state_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'] if input_id == 'shaded-states' else state_sel
    return value

##Sync the cities selected by hover with the dropdown menu
@callback(
    Output("city-sel", "value"),
    Input("city-sel", "value"),
    Input('states-scatter', 'hoverData')
)
def sync_city_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'][0] if input_id == 'states-scatter' else city_sel
    return value