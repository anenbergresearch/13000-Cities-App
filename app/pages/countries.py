import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback,dcc,html
from dash.dependencies import Input, Output,State
import plotly.io as pio
import dash
import copy
from components import buttons,const,data_prep
import dash_bootstrap_components as dbc
dash.register_page(__name__)

df = data_prep.DFILT

pio.templates.default = "simple_white"

fmean,fmax,fmin = data_prep.MEAN,data_prep.MAX,data_prep.MIN


main_graph =dcc.Graph(
            id='shaded-map',
            hoverData={'points': [{'customdata': 'United States'}]}
        )
metrics = buttons.health_metrics('country')



pops = html.Div(buttons.pop_weighted('')
            ,className="radio-group")

pop_stack = dbc.Stack([buttons.pol_buttons('country'),buttons.pop_weighted('')],className="radio-group",direction="horizontal",gap=4)

pol_buttons = dbc.Stack([metrics, pop_stack
            ],className="radio-group")
graph_stack =dbc.Stack([
        dcc.Graph(id='cities-scatter', hoverData={'points': [{'customdata': 'Washington D.C., United States (860)'}]}),
        dcc.Graph(id='country-trends-graph'),
    ])
slider =buttons.sliders(df)
inst = buttons.instruct('open-offcanvas-c')

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
lin_log=html.Div(buttons.lin_log(),className='ms-auto radio-group')
off_canva = dbc.Collapse([dbc.Card([
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
                html.H5(children='Select a Country',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Explore the countries by hovering over the map on the left. The graph on the upper right will populate with a scatter plot of cities within the country that is selected on the left. Alternatively, select a country by clicking or searching in the first dropdown menu; your selection will be highlighted on the map and the cities within it will be plotted on the upper right-hand side. ",style ={'color':const.DISP['subtext']}),
                html.H5(children='Select a City',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Explore the cities by hovering over the graph on the upper right. The city your mouse is closest to will highlight and plot as an orange line in the bottom right graph. Alternatively, select a city of interest by clicking or searching in the second dropdown menu; your selection will be highlighted on the scatter plot and plotted on the lower right-hand side.",style ={'color':const.DISP['subtext']}),
                html.H5(children='Countrywide Trends',style ={'color':const.DISP['text']},),
                html.P(children=
                    "The bottom right graph is a timeseries that compares the country mean (teal) concentration and the selected city trend (orange). The light gray lines indicate the minimum and maximum concentration values of the states over time. Hover over the graph to see the values.",style ={'color':const.DISP['subtext']}),
                html.H5(children='Select a Year',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Choose which year of data to visualize with the year slider on the bottom.",style ={'color':const.DISP['subtext']},)],body=True,              
                style ={'color':const.DISP['text'],'font-size':'xlarge'})],id="offcanvas-countries",style ={'color':const.DISP['text']},is_open=False)

layout =dbc.Container([dbc.Row([dbc.Col(width=2),
        dbc.Col(html.Div(style={'backgroundColor': const.DISP['background']}, children=[
            html.H1(
                children='Map of Mean Concentration',
                style={
                    'textAlign': 'center',
                    'color': const.DISP['text'],'font':'helvetica','font-weight': 'bold'
                    
                }
            ),

            html.Div(children='Exploring Countrywide Trends', style={
                'textAlign': 'center','font':'helvetica',
                'color': const.DISP['subtext']
            })])),dbc.Col(inst,width=2)],align='center'),
    dbc.Row(dbc.Col(off_canva)),
    html.Hr(),
    dbc.Row([dbc.Col(pol_buttons,width=7),dbc.Col(country_drop,width=2),dbc.Col(dbc.Stack([city_drop,lin_log]),width=3)]),
    
    dbc.Row([dbc.Col(main_graph,width=7),dbc.Col(graph_stack,width=5),html.Hr()]),
    dbc.Row(slider)],fluid=True)

@callback(
    Output("offcanvas-countries", "is_open"),
    Input("open-offcanvas-c", "n_clicks"),
    [State("offcanvas-countries", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@callback(
    Output("open-offcanvas-c", "children"),
    Output("open-offcanvas-ctt","children"),
    Input("open-offcanvas-c", "n_clicks"),
    [State("offcanvas-countries", "is_open")],
)
def toggle_button(n1, is_open):
    if n1%2:
        return "Close Details", "Click Close Details to hide text."
    return "Open Details","Click Open Details for more information on the compenents of the webpage."

##Deactivates CO2 if anything but concentration is selected and vice-versa
@callback(
    [Output('health-metricscountry','options',allow_duplicate=True),
    Output('crossfilter-yaxis-columncountry','options')],
    [Input('crossfilter-yaxis-columncountry', 'value'),
    Input('health-metricscountry', 'value'),
    Input('crossfilter-yaxis-columncountry', 'options'),
    Input('health-metricscountry', 'options')],
    prevent_initial_call=True,
    )
def trigger_function(yaxis_col,data_type,yaxis,dtype):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id =='crossfilter-yaxis-columncountry':
        if yaxis_col == 'CO2':
            dtype = const.metric_options(True)
        else:
            dtype = const.metric_options(False)
            
    elif input_id == 'health-metricscountry':
        if data_type !='Concentration':
            yaxis = const.pol_options(True)
        else:
            yaxis = const.pol_options(False)
    return dtype,yaxis

#Creates dropdown list based on selected country
@callback(
    Output("city-s", "options"),
    Output("city-s","value", allow_duplicate=True),
    Input("country-s", "value"),
    prevent_initial_call=True
)
def chained_callback_city(country):

    dff = copy.deepcopy(df)
    if country is not None:
        dff = dff.query("Country == @country")
    return sorted(dff["CityCountry"].unique()),sorted(dff["CityCountry"].unique())[0]

##Creates and updates shaded map of all countries
@callback(
    Output('shaded-map', 'figure'),
    [
     Input('crossfilter-yaxis-columncountry', 'value'), ##Indicates selected value of pollutant
     Input('crossfilter-data-type', 'value'), #Population weighted or unweighted
     Input('crossfilter-year--slider', 'value'), #Which year is selected
     Input('country-s','value'), #What country is hovered over for the highlight
     Input('health-metricscountry','value')
     ])
def update_graph(pollutant,
                  data_type,year_value,countryS,metric):
    m = fmean.query('Year == @year_value').copy()
    unit_s = pollutant
    if metric !='Concentration':
        pollutant = metric +'_'+pollutant
    if data_type =='Population Weighted':
        pollutant = 'w_'+pollutant
    if 'CO2' in pollutant:
        if data_type == 'Unweighted':
            maxx= 4e6
        else:
            maxx =50e6
        m['text'] = '<b>'+m['Country'] + '</b><br>'+const.UNITS['Concentration'][unit_s]+': '+ round((m[pollutant].astype(float)/1000000),3).astype(str) + 'M'
    else:
        m['text'] = '<b>'+m['Country'] + '</b><br>'+const.UNITS[metric][unit_s]+': '+ m[pollutant].round(2).astype(str)
        if pollutant == 'Cases_NO2':
            maxx =500
        elif pollutant == 'Cases_PM':
            maxx=300
        else:
            maxx=m[pollutant].max()
    
    fig = go.Figure(data=go.Choropleth(locations = m['Country'],locationmode = 'country names',customdata=m['Country'],
            z = m[pollutant],hovertext=m['text'],hoverinfo='text',
                        colorscale=const.CS[metric],
                        zmin=0,
                       zmax=maxx))
    #Adds the hightlight of the country selected
    ctry = m.query('Country ==@countryS')  #Creates dataframe for highlighted country
    fig.add_traces(data=go.Choropleth(locations = ctry['Country'],locationmode = 'country names',
            z = ctry[pollutant],hoverinfo='skip',
                        colorscale=const.CS[metric],
                        zmin=0,
                       zmax=maxx,marker = dict(line_width=3)))
    fig.update_geos(showframe=False)
    fig.update_layout(legend_title_text='',paper_bgcolor= const.DISP['background'],plot_bgcolor=const.DISP['background'],margin={'l': 10, 'b': 10, 't': 10, 'r': 0}, hovermode='closest',coloraxis_colorbar_x=-0.1)
    fig.update_yaxes(title=pollutant)
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY
        ))
    return fig


def create_time_series(city,means, title, cityname, axiscol_name,metric,units):
    fig = go.Figure()
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
            family = const.FONTFAMILY
        ))
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
    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode="x unified",paper_bgcolor= const.DISP['background'],plot_bgcolor=const.DISP['background'],
                      legend=dict(y=1,x=1),height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    if metric != 'Concentration':
        fig.update_yaxes(title=metric)
    else:
        fig.update_yaxes(title=const.UNITS[metric][units])
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    return fig

@callback(
    Output('cities-scatter', 'figure'),
    [Input('shaded-map', 'hoverData'),
    Input('crossfilter-yaxis-columncountry', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-data-type', 'value'),
    Input('crossfilter-year--slider','value'),
    Input('country-s','value'),
    Input('city-s','value'),
    Input('health-metricscountry','value')])


def update_y_timeseries(hoverData, pollutant, xaxis_type,data_type,year_value,countryS,cityS,metric):
    if metric !='Concentration':
        plot_x = metric +'_'+pollutant
    else:
        plot_x = pollutant
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    country_name = hoverData['points'][0]['customdata'] if input_id == 'shaded-map' else countryS
    dff = df[df['Country']==country_name]
    dff = dff.query('Year ==@year_value')
    city_df = dff.query('CityCountry ==@cityS')
    title = '<b>{}</b><br>{}'.format(const.UNITS[metric][pollutant], country_name)
    plot = []
    for i in const.COUNTRY_SCATTER:
        _c=dff.query('C40 ==@i')
        if _c.empty:
            continue
        if plot_x =='CO2':
            plot.append(go.Scatter(name = const.COUNTRY_SCATTER[i]['name'], x=_c['Population'], y=_c[plot_x], mode='markers',
                               customdata=np.stack((_c['CityCountry'],_c[pollutant]),axis=-1),
                               hovertemplate="<b>%{customdata[0]}</b><br>" +'Population: %{x} <br>' + f"{const.UNITS['Concentration'][pollutant]}: "+'%{y} <br>',
                              marker={'color':const.COUNTRY_SCATTER[i]['color'], 'symbol':const.COUNTRY_SCATTER[i]['symbol'],'line':dict(width=1,
                                        color=const.COUNTRY_SCATTER[i]['color'])}))
        else:
            plot.append(go.Scatter(name = const.COUNTRY_SCATTER[i]['name'], x=_c['Population'], y=_c[plot_x], mode='markers',
                                   customdata=np.stack((_c['CityCountry'],_c[pollutant],_c['PAF_'+pollutant],_c['Cases_'+pollutant]),axis=-1),
                                   hovertemplate="<b>%{customdata[0]}</b><br>" +'Population: %{x} <br>' + f"{const.UNITS['Concentration'][pollutant]}: "+'%{customdata[1]} <br>'+ f"{const.UNITS['PAF'][pollutant]}: "+'%{customdata[2]} <br>' + f"{const.UNITS['Cases'][pollutant]}: "+'%{customdata[2]}',
                                  marker={'color':const.COUNTRY_SCATTER[i]['color'], 'symbol':const.COUNTRY_SCATTER[i]['symbol'],'line':dict(width=1,
                                            color=const.COUNTRY_SCATTER[i]['color'])}))
    fig =go.Figure(data=plot)
    fig.add_trace(
        go.Scattergl(
            mode='markers',
            x=city_df['Population'],
            y=city_df[plot_x],
            customdata=np.stack((city_df['CityCountry'],city_df[pollutant]),axis=-1),
            opacity=1,
            marker=dict(
                symbol='circle-open-dot',
                color='#FAED26',
                size=10,
                line=dict(width=2)),
            showlegend=False,
            hoverinfo='skip'
        )
    )
    
    fig.update_xaxes(title='Population', type='linear' if xaxis_type == 'Linear' else 'log')

    if metric != 'Concentration':
        fig.update_yaxes(title=metric)
    else:
        fig.update_yaxes(title=const.UNITS[metric][pollutant])    
    
    fig.update_layout(height = 225, margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',legend_title_text='',legend_x=1, legend_y=0,paper_bgcolor= const.DISP['background'],plot_bgcolor=const.DISP['background'])
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY
        ))
    fig.add_annotation(x=0, y=0.73, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title, font=dict(size=12,
            ),)
    return fig

@callback(
    Output('country-trends-graph', 'figure'),
    [Input('cities-scatter','hoverData'),
    Input('country-s', 'value'),
    Input('crossfilter-yaxis-columncountry', 'value'),
    Input('crossfilter-data-type', 'value'),
    Input('city-s','value'),
    Input('health-metricscountry','value')])
def update_x_timeseries(cityName, country_name, pollutant, data_type,cityS,metric):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = cityName['points'][0]['customdata'][0] if input_id == 'cities-scatter' else cityS
    units = pollutant
    if metric !='Concentration':
        pollutant = metric +'_'+pollutant
    city = df[df.CityCountry ==city_sel][pollutant]
    _df = fmean[fmean['Country'] == country_name][['Year',pollutant,'w_'+pollutant]]
    _df['Minimum'] = fmin[fmin['Country'] == country_name][pollutant]
    _df['Maximum'] = fmax[fmax['Country'] == country_name][pollutant]
    return create_time_series(city,_df, country_name,city_sel,pollutant,metric,units)

##Syncing the hover effect and the city and country dropdown menus##

#Sync the countries selected
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

#Sync the cities selected
@callback(
    Output("city-s", "value"),
    Input("city-s", "value"),
    Input('cities-scatter', 'hoverData')
)
def sync_city_input(city_sel, hoverData):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = hoverData['points'][0]['customdata'][0] if input_id == 'cities-scatter' else city_sel
    return value