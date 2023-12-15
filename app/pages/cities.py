import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, callback,dcc,html
from dash.dependencies import Input, Output,State
import dash_bootstrap_components as dbc
from components import const,data_prep,buttons

import dash

dash.register_page(__name__)
df = data_prep.DFILT


cont_l = df.continent.dropna().unique()

cont_dict = {}
for i in range(len(cont_l)):
    cont_dict[cont_l[i]]=const.CITY[i]

available_indicators = const.POLS


membs =buttons.members()

lin_log=buttons.lin_log()
pop_weight = dbc.Stack([buttons.pop_weighted('cities')],className="radio-group")
metrics = buttons.health_metrics('')

pol_buttons=dbc.Stack([metrics],className="radio-group")

c40_sel = buttons.c40()


inst = buttons.instruct('open-offcanv')


off_canva = dbc.Stack([
                       dbc.Collapse([dbc.Card([
                 html.H5(children='Metric',style ={'color':const.DISP['text']},),
                 html.P(   
                    children="Select which metric to visualize. Concentration will display the pollutant concentrations, and the others will display health metrics related to each pollutant. For O3 and PM2.5, the metrics indicate premature deaths attributable to the corresponding pollutants. For NO2, the metrics indicate pediatric asthma incidence attributable to NO2. Health metrics are not available for CO2.",style ={'color':const.DISP['subtext']}
                ),
                 html.H5(children='Pollutant',style ={'color':const.DISP['text']},),
                 html.P(   
                    children="Select the pollutant to visualize with the buttons on the left",style ={'color':const.DISP['subtext']}
                ),
                 html.H5(children='Continent',style ={'color':const.DISP['text']}),
                 html.P(children=   
                    "Select the continents to appear on the scatter plot",style ={'color':const.DISP['subtext']}
                ),
                html.H5(children='Memberships',style ={'color':const.DISP['text']}),
                 html.P(children=   
                    "Select whether to see just cities that are members of climate groups, or all cities in the dataset. In the dropdown, select which membership group to plot. There is also an option to plot All Memberships, or to plot the number of memberships each city has.",style ={'color':const.DISP['subtext']}
                ),
                html.H5(children='Population Axis',style ={'color':const.DISP['text']}),
                 html.P(children=   
                    "Select whether you want the population data to be displayed with a logarithmic or linear axis using the center buttons",style ={'color':const.DISP['subtext']}
                ),
                html.H5(children='Select a City',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Explore the cities by hovering over the graph on the left. The city your mouse is closest to will populate the population and time series plots on the right. Alternatively, select a city of interest by clicking or searching in the dropdown menu; your selection will be highlighted on the scatter plot and plotted on the right-hand side. ",style ={'color':const.DISP['subtext']}),
                html.H5(children='Select a Year',style ={'color':const.DISP['text']},),
                html.P(children=
                    "Choose which year of data to visualize with the year slider on the bottom.",style ={'color':const.DISP['subtext']})],body=True)],
                id="offcanv",
                style ={'color':const.DISP['text']},
                is_open=False,
            )])

city_drop = html.Div(dcc.Dropdown(
                    id='CityS',
                    options=sorted(df["CityCountry"].unique()),
                    value='Tokyo, Japan (13017)',
                    placeholder= 'Select city...',
                style ={'color':'#123C69', 'font-size':'12px'},
                ),className='single-dropd')
cont_drop = html.Div(dcc.Dropdown(
            id="ContS",
            value=list(cont_l.astype(str)),
            options=list(cont_l.astype(str)),
            multi=True, style ={'color':'#123C69'},
            placeholder= 'Select continents...'
        ),className="custom-dropdown")
sliders =  buttons.sliders(df)
horz = dbc.Stack([pol_buttons,buttons.pol_buttons('cities'),membs,lin_log],direction="horizontal",
            gap=2,className="radio-group")        
drops = dbc.Stack([c40_sel,city_drop],direction ='horizontal',className='ms-auto')

main_graph = dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'Tokyo, Japan (13017)'}]}
        )                        
graph_stack = dbc.Stack([dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series')])

        
layout =dbc.Container([dbc.Row([dbc.Col(width=2),dbc.Col(
            html.Div(style={'backgroundColor': const.DISP['background']}, children=[html.H1(children='Urban Climate Network Memberships', style={'textAlign': 'center','color': const.DISP['text'],'font':'helvetica','font-weight': 'bold'}),html.Div(children='A closer look at cities in different urban climate networks', style={'textAlign': 'center','color': const.DISP['subtext'],'font':'helvetica'})])),dbc.Col(inst,width=2)],align='center'),
        dbc.Row([dbc.Col(off_canva),html.Hr()]),
dbc.Row([dbc.Col(horz)]),dbc.Row([dbc.Col(cont_drop,width=7),dbc.Col(c40_sel,width=2),dbc.Col(city_drop,width=3)]),
    dbc.Row([dbc.Col(main_graph,width=7),dbc.Col(graph_stack,width=5)]),
    dbc.Row(sliders)],fluid=True)


##Callbacks for open/close instructions and button changes
@callback(
    Output("offcanv", "is_open"),
    Input("open-offcanv", "n_clicks"),
    [State("offcanv", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

@callback(
    Output("open-offcanv", "children"),
    Output("open-offcanvtt","children"),
    Input("open-offcanv", "n_clicks"),
    [State("offcanv", "is_open")],
)
def toggle_button(n1, is_open):
    if n1%2:
        return "Close Details", "Click Close Details to hide text."
    return "Open Details","Click Open Details for more information on the compenents of the webpage."



##Deactivates CO2 if anything but concentration is selected and vice-versa
@callback(
    [Output('health-metrics','options',allow_duplicate=True),
    Output('crossfilter-yaxis-columncities','options')],
    [Input('crossfilter-yaxis-columncities', 'value'),
    Input('health-metrics', 'value'),
    Input('crossfilter-yaxis-columncities', 'options'),
    Input('health-metrics', 'options')],
    prevent_initial_call=True,
    )
def trigger_function(yaxis_col,data_type,yaxis,dtype):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id =='crossfilter-yaxis-columncities':
        if yaxis_col == 'CO2':
            dtype = const.metric_options(True)
        else:
            dtype = const.metric_options(False)
            
    elif input_id == 'health-metrics':
        if data_type !='Concentration':
            yaxis = const.pol_options(True)
        else:
            yaxis = const.pol_options(False)
    return dtype,yaxis
    

@callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    [Input('crossfilter-yaxis-columncities', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-year--slider', 'value'),
    Input('CityS', 'value'),
    Input('ContS','value'),
     Input('c40-toggle','value'),
     Input('membsDrop','value'),
     Input('health-metrics','value')
     ])
def update_graph(yaxis_column_name,
                 xaxis_type,
                 year_value,cityS,contS,toggle,memb,metric):
    dff =df.query('Year == @year_value').copy()
    city_df = dff.query('CityCountry ==@cityS').copy()
    
    if metric != 'Concentration':
        yaxis_plot = metric +'_'+yaxis_column_name
    else:
        yaxis_plot = yaxis_column_name
    
    
    plot = []
    if memb == 'Number of Memberships':
        _nc=dff.query('Memberships>0')
        coll=['#f4f100', '#c9e52f', '#76c68f', '#22a7f0', '#115f9a']
        if toggle == 'All Cities':
            _nc=dff.query('Memberships==0') 
            plot.append(go.Scatter(name = 'O Memberships', legendgroup= 'Memberships', legendgrouptitle= {'text':'Number of Memberships'}, 
                                               x=_nc['Population'],y=_nc[yaxis_plot],mode='markers',customdata=_nc['CityCountry'],
                                               hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br> ' + f'{const.UNITS[metric][yaxis_column_name]}: '+ '%{y}',
                                              marker={'color':'pink','opacity':0.4}))
        for i in range(1,5):
            _nc=dff.query('Memberships==@i')
            if i ==4:
                _nc=dff.query('Memberships>=@i')
            plot.append(go.Scatter(name = str(i) +' Memberships', legendgroup= 'Memberships', legendgrouptitle= {'text':'Number of Memberships'}, 
                               x=_nc['Population'],y=_nc[yaxis_plot],mode='markers',customdata=_nc['CityCountry'],
                                hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br> ' + f'{const.UNITS[metric][yaxis_column_name]}: '+ '%{y}',marker={'color':coll[i],'opacity':0.9}))
        
    elif memb == 'All Memberships':
        if toggle == 'All Cities':
            for i in contS:
                _nc=dff.query('Memberships==0 & continent==@i')
                plot.append(go.Scatter(name = i, legendgroup= 'Other Cities', legendgrouptitle= {'text':'Other Cities'}, 
                                                   x=_nc['Population'],y=_nc[yaxis_plot],mode='markers',customdata=_nc['CityCountry'],
                                                   hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br> ' + f'{const.UNITS[metric][yaxis_column_name]}: '+ '%{y}',
                                                  marker={'color':'lightgray','opacity':0.2}))
        for m in const.MEMBERS:
            _c =dff[dff[m]==True]
            plot.append(go.Scatter(name = m, legendgroup= memb,legendgrouptitle={'text':memb+' Cities'}, x=_c['Population'], y=_c[yaxis_plot], mode='markers',
                                       customdata=_c['CityCountry'],
                                       hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br>' + f'{const.UNITS[metric][yaxis_column_name]}: '+'%{y}',
                                      marker={'color':const.MEMBERS[m][1],'symbol':const.MEMBERS[m][0],'size':10,'opacity':0.8,'line':dict(width=0.5,
                                                color=const.DISP['background'])}))      
        
    else:        
        for i in contS:
            _c=dff.query('continent==@i')

            _c =_c[_c[memb]==True]
            if toggle == 'All Cities':
                _nc=dff.query('Memberships==0 & continent==@i')
                plot.append(go.Scatter(name = i, legendgroup= 'Other Cities', legendgrouptitle= {'text':'Other Cities'}, 
                                           x=_nc['Population'],y=_nc[yaxis_plot],mode='markers',customdata=_nc['CityCountry'],
                                           hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br> ' + f'{const.UNITS[metric][yaxis_column_name]}: '+ '%{y}',
                                          marker={'color':cont_dict[i][1],'opacity':0.2}))
            plot.append(go.Scatter(name = i, legendgroup= memb,legendgrouptitle={'text':memb +' Cities'}, x=_c['Population'], y=_c[yaxis_plot], mode='markers',
                                       customdata=_c['CityCountry'],
                                       hovertemplate="<b>%{customdata}</b><br>" +'Population: %{x} <br>' + f'{const.UNITS[metric][yaxis_column_name]}: '+'%{y}',
                                      marker={'color':cont_dict[i][1], 'symbol':const.MEMBERS[memb][0],'size':10,'line':dict(width=0.8,
                                            color=const.DISP['background'])}))
            


    fig =go.Figure(data=plot)
    

    fig.update_layout(legend=dict(groupclick="toggleitem"),legend_title_text='',paper_bgcolor= const.DISP['background'],plot_bgcolor=const.DISP['background'])
    fig.add_trace(
        go.Scattergl(
            mode='markers',
            x=city_df['Population'],
            y=city_df[yaxis_plot],
            opacity=1,
            marker=dict(
                symbol='circle-dot',
                color='#FAED26',
                size=11,
                line=dict(
                        color=const.DISP['text'],
                        width=2),
            ),
            showlegend=False,
            hoverinfo='skip'
        )
    )    
    fig.update_xaxes(title='Population', type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(title=const.UNITS[metric][yaxis_column_name])
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest') 
    fig.update_layout(
        legend = dict(
            x=0,
            y=1,
            bgcolor='rgba(255, 255, 255, 0.5)',
        borderwidth=0, font = dict(size = 18, color = const.DISP['text'])),
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY
        ))
    return fig


def create_time_series(dff, axis_type, title, axiscol_name,metric):
    if metric != 'Concentration':
        axis_plot = metric +'_'+axiscol_name
        ytitle = metric
    else:
        axis_plot = axiscol_name
        ytitle = const.UNITS[metric][axiscol_name]
    if axiscol_name == 'Population':
        fig = go.Figure(go.Scatter(x=dff['Year'], y=dff[axis_plot], name = const.UNITS[metric][axiscol_name],customdata=np.stack((dff['Population'],dff[axis_plot]),axis=-1),hovertemplate = '<b>Population:</b> %{customdata[1]} <br><extra></extra>'))
        fig.update_traces(mode='lines+markers')
        fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log',title = ytitle)
    elif metric=='Concentration':
        
        fig = go.Figure(go.Scatter(x=dff['Year'], y=dff[axis_plot], customdata=np.stack((dff['Population'],dff[axis_plot]),axis=-1),name = const.UNITS[metric][axiscol_name],hovertemplate = "<b>" f"{const.UNITS['Concentration'][axiscol_name]}: "+'</b> %{customdata[1]} <br><extra></extra>'))
        fig.update_traces(mode='lines+markers')
        fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log',title = ytitle)
    else:
        fig = go.Figure(go.Bar(x=dff['Year'], y=dff[axis_plot],marker=dict(color =dff['Population'],colorscale= 'Darkmint',colorbar={'title':'Pop'}),customdata=np.stack((dff['Population'],dff[axis_plot]),axis=-1),name = const.UNITS[metric][axiscol_name],hovertemplate = '<b>Population: </b> %{customdata[0]}'+'<b><br>'+ f'{const.UNITS[metric][axiscol_name]}: '+ '</b>%{y}<br><extra></extra>'))
        #fig = go.Figure(go.Scatter(x=dff['Year'], y=dff[axis_plot], name = const.UNITS[metric][axiscol_name],hovertemplate = '<b>'+ f'{const.UNITS[metric][axiscol_name]}: '+ '</b>%{y:.2f}<extra></extra>'))
    
    fig.update_xaxes(showgrid=False)
    
    
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10},paper_bgcolor=const.DISP['background'], plot_bgcolor=const.DISP['background'])
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY
        ))
    fig.add_annotation(x=0, y=0.73, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       bgcolor='rgba(255, 255, 255, 0.5)', text=title)
    return fig
@callback(
    Output('x-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'hoverData'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('CityS', 'value'),
    Input('health-metrics','value'),
    Input('crossfilter-yaxis-columncities', 'value')])
def update_y_timeseries(hoverData, axis_type,city_sel,metric,yaxis):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if metric == 'Concentration':
        plot_axis = 'Population'
    else:
        plot_axis = yaxis
        axis_type = 'Linear'
    city_sel = hoverData['points'][0]['customdata'] if input_id == 'crossfilter-indicator-scatter' else city_sel
    dff = df[df['CityCountry'] == city_sel] 
    country_name = dff['CityCountry'].iloc[0]
    title = '<b>{}</b><br>{}'.format(const.UNITS[metric][plot_axis], country_name)
    return create_time_series(dff, axis_type, title, plot_axis,metric)


@callback(
    Output('y-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'hoverData'),
     Input('crossfilter-yaxis-columncities', 'value'),
     Input('CityS', 'value'),
     ])
def update_x_timeseries(hoverData, yaxis_column_name,city_sel):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    city_sel = hoverData['points'][0]['customdata'] if input_id == 'crossfilter-indicator-scatter' else city_sel
    dff = df[df['CityCountry'] == city_sel] 
    country_name = dff['CityCountry'].iloc[0]
    return create_time_series(dff, 'Linear', country_name,yaxis_column_name,'Concentration')

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