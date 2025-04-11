import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html, callback,dash_table,State
import dash_bootstrap_components as dbc
from components import buttons, const,data_prep
import copy

HAQAST = 'assets/HAQAST.png'
MILKEN = 'assets/Milken_Institute_School_of_Public_Health.jpg'

dash.register_page(__name__, path='/')

cb =pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/Codebook.csv')
df = data_prep.DFILT
pc_df = data_prep.DF_CHANGE
conc= {'CO2':15e6,'NO2': 20,'O3':75,'PM':100}
paf = {'CO2':'null','NO2': 25,'O3':20,'PM':40}
cases = {'CO2':'null','NO2': 1000,'O3':100,'PM':1000}
rates = {'CO2':'null','NO2': 100,'O3':40,'PM':110}

m_limits = {'Concentration':conc,'PAF':paf,'Cases':cases,'Rates':rates}
metrics = buttons.health_metrics('home')

#embed = <iframe src="https://gwu.app.box.com/embed/s/d6ld5a691r0nx0do76jvdjx75ou2hx5m?sortColumn=date" width="800" height="550" frameborder="0" allowfullscreen webkitallowfullscreen msallowfullscreen></iframe>
inst_video = html.Iframe(src="https://gwu.app.box.com/embed/s/d6ld5a691r0nx0do76jvdjx75ou2hx5m?sortColumn=date" , style={"height": "550px", "width": "800px"})

button_group = html.Div(
    [
        buttons.pol_buttons('home')],
    className="radio-group",
)
slider = buttons.sliders(df)
vtip= dbc.Tooltip(
                "Open this tab for a walkthrough of the website.",
                target='video',
                is_open =False,
                trigger ='hover focus legacy',
                placement ='top',
                style = {'color':'lightgray'}
            )
graph=dcc.Graph(
            id='welcome-map')
pc_graph=dcc.Graph(
            id='percent-change')

range_slider = dcc.RangeSlider(
    id= 'range',
    value=[2000, 2019],
    step=1,
    marks={i: str(i) for i in range(2000, 2020, 1)}
)
city_drop = html.Div(dcc.Dropdown(
                    id='CitySe',
                    options=sorted(df["CityCountry"].unique()),
                    value='Washington D.C., United States (860)',
                    style ={'color':'#123C69'},
                ),className='single-dropd')
country_drop = dcc.Dropdown(
                    id='CountrySe',
                    options=sorted(df["Country"].unique()),
                    value='United States',
                )
dtable = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in df.columns],
    sort_action="native",
    page_size=10,
    style_table={"overflowX": "auto"},
)

download_button = dbc.Button("Download Filtered CSV", color='secondary')
download_component = dcc.Download()

@callback(
    Output(download_component, "data"),
    Input(download_button, "n_clicks"),
    State(dtable, "derived_virtual_data"),
    prevent_initial_call=True,
)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered_csv.csv")



about_acc = html.Div(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    dcc.Markdown(dangerously_allow_html=True,children = '''
                    - PM<sub>2.5</sub> urban concentrations and disease burdens are from [Southerland et al. (2022)](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(21)00350-8/fulltext). PM<sub>2.5</sub> concentrations are not from the GBD 2019, but are from a higher spatial resolution dataset (1km x 1km) developed by [Hammer et al. (2020)](https://pubs.acs.org/doi/full/10.1021/acs.est.0c01764). The dataset integrates information from satellite-retrieved aerosol optical depth, chemical transport modeling, and ground monitor data. Briefly, multiple AOD retrievals from three satellite instruments (the Moderate Resolution Imaging Spectroradiometer (MODIS), SeaWiFs, and the Multiangle Imaging Spectroradiometer (MISR)) were combined and related to near-surface PM<sub>2.5</sub> concentrations using the GEOS-Chem chemical transport model. Ground-based observations of PM<sub>2.5</sub> were then incorporated using a geographically weighted regression. PM<sub>2.5</sub> concentrations and disease burdens are year-specific.
                    - Ozone (O<sub>3</sub>) urban concentrations and disease burdens are from [Malashock et al. (2022a)](https://iopscience.iop.org/article/10.1088/1748-9326/ac66f3) and [Malashock et al. (2022b)](https://doi.org/10.1016/S2542-5196(22)00260-1). Estimates of ozone seasonal daily maximum 8-hour mixing ratio (OSDMA8) concentrations are from the GBD 2019 (0.1 x 0.1 degree), originally developed by [DeLang et al. (2021)](https://pubs.acs.org/doi/abs/10.1021/acs.est.0c07742). OSDMA8 is calculated as the annual maximum of the six-month running mean of the monthly average daily maximum 8 hour mixing ratio, including through March of the following year to contain the Southern Hemisphere summer. [DeLang et al. (2021)](https://pubs.acs.org/doi/abs/10.1021/acs.est.0c07742) combined ozone ground measurement data with chemical transport model estimates. Output was subsequently downscaled to create fine (0.1 degree) resolution estimates of global surface ozone concentrations from 1990-2017. For the GBD 2019 study, the Institute for Health Metrics and Evaluation (IHME) extrapolated the available estimates for 1990–2017 to 2019 using log-linear trends based on 2008−2017 estimates. We re-gridded ozone data to 1 km (0.0083 degree) resolution to match the spatial resolution of the population estimates. Ozone concentrations and disease burdens are year-specific.
                    - NO<sub>2</sub> urban concentrations and disease burdens are from [Anenberg et al. (2022)](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(21)00255-2/fulltext). NO<sub>2</sub> concentrations (1km x 1km) are those used by the GBD 2020, as NO<sub>2</sub> is a new pollutant included in the GBD after GBD 2019. The dataset was originally developed by [Anenberg et al. (2022)](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(21)00255-2/fulltext) and combines surface NO<sub>2</sub> concentrations for 2010-2012 from a land use regression model with Ozone Monitoring Instrument (OMI) satellite NO<sub>2</sub> columns to scale to different years. NO<sub>2</sub> concentrations and disease burdens are year-specific and were interpolated for the years between 2000 and 2005 and between 2005 and 2010.
                    - CO<sub>2</sub> urban emissions are from Emission Database for Global Atmospheric Research ([EDGAR](https://edgar.jrc.ec.europa.eu/report_2022)). The fossil fuel CO<sub>2</sub> emissions are isolated by adding the annual long cycle CO<sub>2</sub> emissions from [EDGAR v7.0](https://edgar.jrc.ec.europa.eu/dataset_ghg70) for the following sectors: *Power Industry;  Energy for Buildings; Combustion for Manufacturing Industry; Road Transportation; Aviation (landing & take off, climbing & descending, and cruise); Shipping and Railways; Pipelines; and Off-Road Transport.*
                    - Urban built-up area is from the [GHS-SMOD](https://ghsl.jrc.ec.europa.eu/ghs_smod2019.php) dataset. Urban boundaries don’t follow administrative boundaries and include surrounding built-up areas. [Apte et al. (2021)](https://chemrxiv.org/engage/chemrxiv/article-details/60c75932702a9baa0818ce61) show that the urban boundary definition doesn’t influence concentration estimates much.
                    - Population is from the [Worldpop](https://www.worldpop.org/) dataset at ~1km resolution. There’s quite a bit of difference between globally gridded population datasets, and it’s not clear which is the “best” source. A good resource to see how different population datasets compare in different areas of the world is https://sedac.ciesin.columbia.edu/mapping/popgrid/.
                    - Disease burdens (national and, in some cases, subnational) and epidemiologically-derived concentration-response relationships are from the [GBD 2019](http://www.healthdata.org/gbd/2019). We could not find urban disease rates for cities globally, so we don’t account for differences in urban disease rates compared with the national (or sub-national, in some places) average rates that we applied. We used the same concentration-response relationships everywhere in the world.
                    - Uncertainty has been excluded in this data visualization to display temporal trends more clearly. For more information on source and magnitude of uncertainty, see the journal articles linked above. We believe the greatest source of uncertainty is the concentration-response factor, and less uncertainty (though likely still substantial) comes from the concentration estimates, disease rates, and population distribution.

                    '''
                    ),
                ],
                title="More Information",
            ),
        dbc.AccordionItem(
                [
                    dcc.Markdown('''
                    This project was led by the George Washington University Milken Institute School of Public Health with support from NASA, Health Effects Institute, and the Wellcome Trust. Susan Anenberg led the project. Veronica Southerland produced the PM2.5 estimates, Danny Malashock produced the ozone estimates, and Arash Mohegh produced the NO2 estimates. The website was developed by Sara Runkel. Additional contributors include Josh Apte, Jacob Becker, Michael Brauer, Katrin Burkart, Kai-Lan Chang, Owen Cooper, Marissa DeLang, Dan Goldberg, Melanie Hammer, Daven Henze, Perry Hystad, Gaige Kerr, Pat Kinney, Andy Larkin, Randall Martin, Omar Nawaz, Marc Serre, Aaron Van Donkelaar, Jason West and Sarah Wozniak. We also gratefully acknowledge the developers of the input datasets, including satellite observations, pollution concentration, GHS-SMOD urban area, Worldpop population, and GBD disease rates and concentration-response functions. The contents of this website do not necessarily reflect the views of NASA, the Health Effects Institute, or Wellcome Trust.
                
                    '''
                    ),
                ],
                title="Acknowledgements",
            )
        ],
        flush=True,
    ),
)


table= html.Div(
    [
        html.H4("Data Codebook"),
        html.P(id="data_table"),
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in cb.columns],
            data=cb.to_dict("records"),
            style_cell=dict(textAlign="left"),
        ),
    ]
)

layout = dbc.Container([
    html.H1(children='Urban Air Quality Explorer',style={
                    'textAlign': 'center',
                    'color': const.DISP['text'],'font':'helvetica','font-weight': 'bold'     
                }),
    html.Hr(),
    dbc.Tabs([
        
        dbc.Tab(label='Map', tab_id='welcome_map',style={'font-color':'blue'}),
        
        dbc.Tab(label='Percent Change', tab_id='percent_change'),
        dbc.Tab(label='Data Codebook', tab_id='codebook'),
        dbc.Tab(label='Data Download', tab_id='download'),
        dbc.Tab(label='Video Walkthrough',tab_id='inst_video', id ='video'),
        dbc.Tab(label='About', tab_id='about'),
        ],
        id='tabs',
        active_tab='welcome_map'
    ),
    html.Div(id="tab-content", className="p-4"),
    html.Hr(),
    dbc.Row(vtip),
    dbc.Row([dbc.Col(html.Img(src=MILKEN, height="70px"),width=3),dbc.Col(html.Img(src=HAQAST, height="70px"),width=3)],justify="center")
    ],fluid=True
)

#Creates dropdown list based on selected country
@callback(
    Output("CitySe", "options"),
    Output("CitySe", "value"),
    Input("CountrySe", "value")
)
def chained_callback_city(country):

    dff = copy.deepcopy(df)
    if country is not None:
        dff = dff.query("Country == @country")
    return sorted(dff["CityCountry"].unique()),None

##Filter data table
@callback(
    Output(dtable, "data"),
    [Input('range', "value"),
    Input('CountrySe', "value"),
    Input('CitySe', "value")],
)
def update_table(slider_value, country,city):
    if city == None:
        dff =df.query('Country==@country')
    else:
        dff =df.query('CityCountry==@city')
    dff = dff[dff.Year.between(slider_value[0], slider_value[1])]
    return dff.to_dict("records")


download= html.Div(
    [
        dbc.Button("Download Full CSV",
                   href='https://raw.githubusercontent.com/anenbergresearch/app-files/main/unified_data_SR.csv',
                   download='unified_data.csv',
                   id = 'download_full',
                   external_link=True,
                   color='secondary'
                   ),
    ],
    className="d-grid gap-2"
)

tt= dbc.Tooltip(
                "Download the full, unfiltered dataset here. Download data filtered by country, city and/or year in the data download tab. See codebook below and about page for more information.",
                target='download_full',
                #is_open =True,
                trigger ='hover focus legacy',
                placement ='top',
                style = {'color':'lightgray'}
            )


##Deactivates CO2 if anything but concentration is selected and vice-versa
@callback(
    [Output('health-metricshome','options',allow_duplicate=True),
    Output('crossfilter-yaxis-columnhome','options',allow_duplicate=True)],
    [Input('crossfilter-yaxis-columnhome', 'value'),
    Input('health-metricshome', 'value'),
    Input('crossfilter-yaxis-columnhome', 'options'),
    Input('health-metricshome', 'options')],
    prevent_initial_call=True,
    )
def trigger_function(yaxis_col,data_type,yaxis,dtype):
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id =='crossfilter-yaxis-columnhome':
        if yaxis_col == 'CO2':
            dtype = const.metric_options(True)
        else:
            dtype = const.metric_options(False)
            
    elif input_id == 'health-metricshome':
        if data_type !='Concentration':
            yaxis = const.pol_options(True)
        else:
            yaxis = const.pol_options(False)
    return dtype,yaxis

@callback(
    Output('welcome-map', 'figure'),
    [Input('crossfilter-yaxis-columnhome', 'value'),
     Input('crossfilter-year--slider', 'value'),
     Input('health-metricshome','value')
     ])

def generate_graph(yaxis_column_name,             
                 year_value,metric):
    plot= df.query('Year == @year_value').copy()  
    if metric != 'Concentration':
        axis_plot = metric +'_'+yaxis_column_name
    else:
        axis_plot = yaxis_column_name
    plot['Text'] = '<b>'+plot['CityCountry'] + '</b><br>'+const.UNITS[metric][yaxis_column_name]+': ' +plot[axis_plot].round(2).astype(str)
    p1 = plot[plot['C40']==False].copy().dropna(subset=[axis_plot])
    p2 = plot[plot['C40']==True].copy().dropna(subset=[axis_plot])
    fig = go.Figure(data=go.Scattergeo(
            lon = p1['Longitude'],
            lat = p1['Latitude'],
            text = p1['Text'],
            hoverinfo='text',
            opacity = 0.8,
            name= 'Non-C40 Cities',
            #marker_color = dff['NO2'],
            marker= dict(
                colorscale = const.CS[metric],
                cmin = 0,
                #size=p1["Population"]/30000,
                #sizemode='area',
                line_width=0,
                color = p1[axis_plot],
                symbol = 'circle',
                cmax = m_limits[metric][yaxis_column_name],
                colorbar_title=dict(text= const.UNITS[metric][yaxis_column_name],side='right'),
                #showscale=False
            )))
    #fig.update_layout(legend=dict(groupclick="toggleitem"))
    fig.add_trace(go.Scattergeo(
            lon = p2['Longitude'],
            lat = p2['Latitude'],
            text = p2['Text'],
            hoverinfo='text',
            name= 'C40 Cities',
            #opacity = 0.8,
            #marker_color = dff['NO2'],
            marker= dict(
                colorscale = const.CS[metric],
                cmin = 0,
                #size=p2["Population"]/30000,
                #sizemode='area',
                size = 11,
                line_width=1,
                line_color='white',
                color = p2[axis_plot],
                symbol = 'star',
                cmax = m_limits[metric][yaxis_column_name],
                colorbar_title=dict(text= const.UNITS[metric][yaxis_column_name],side='right')
            )))
    fig.update_layout(
        legend = dict(bgcolor=const.DISP['fades'],
        bordercolor=const.DISP['text'],
        borderwidth=2, font = dict(size = 18, color = 'white')),
        geo = dict(
            showland = True,
            landcolor = const.MAP_COLORS['lake'],
            coastlinewidth=0,
            oceancolor = const.MAP_COLORS['ocean'],
            subunitcolor = "rgb(255, 255, 255)",
            countrycolor = const.MAP_COLORS['land'],
            countrywidth = 0.5,
            showlakes = True,
            lakecolor = const.MAP_COLORS['ocean'],
            showocean=True,
            #showsubunits = True,
            showcountries = True,
            resolution = 50,
        ),
        plot_bgcolor = 'white',
        template = 'simple_white',
    legend_x=0, legend_y=0.5,
            #title = '13,000 Cities ' +units[yaxis_column_name]+' Concentration in '+str(year_value)+'<br>(Hover for values)'
        )
    ##fig.update_layout(coloraxis_colorbar_x=-0.15)
# #     fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')  
    fig.update_layout(legend_title_text='Click to isolate cities', plot_bgcolor= 'white', paper_bgcolor='white', )
    fig.update_geos(showframe=False)
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY   
        ))
    #f#ig.update_traces(customdata=dff['CityCountry'])
    
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig

@callback(
    Output('percent-change', 'figure'),
    [Input('crossfilter-yaxis-columnhome', 'value'),
     ])
def generate_pcgraph(yaxis_column_name):
    plot =data_prep.DF_CHANGE
    plot['Text'] = '<b>'+plot['CityCountry'] + '</b><br>'+const.UNITS_PC[yaxis_column_name]+': ' +plot[yaxis_column_name].round(2).astype(str)
    p1 = plot[plot['C40']==False].copy().dropna()
    p2 = plot[plot['C40']==True].copy().dropna()
    fig = go.Figure(data=go.Scattergeo(
            lon = p1['Longitude'],
            lat = p1['Latitude'],
            text = p1['Text'],
            hoverinfo='text',
            name= 'Non-C40 Cities',
            #marker_color = dff['NO2'],
            marker= dict(
                colorscale = [[0, '#072aed'],[0.5,'white'],
                              [1,'#c70f02']], #'RdBu_r',
                cmin = -50,
                #size=p1["Population"]/30000,
                #sizemode='area',
                line_width=0,
                color = p1[yaxis_column_name],
                symbol = 'circle',
                cmax = 50,
                colorbar_title=dict(text=const.UNITS_PC[yaxis_column_name],side='right'),
                #showscale=False
            )))
    #fig.update_layout(legend=dict(groupclick="toggleitem"))
    fig.add_trace(go.Scattergeo(
            lon = p2['Longitude'],
            lat = p2['Latitude'],
            text = p2['Text'],
            hoverinfo='text',
            name= 'C40 Cities',
            #marker_color = dff['NO2'],
            marker= dict(
                colorscale = [[0, 'blue'],[0.5,'white'],
                              [1,'red']],#'RdBu_r',
                cmin = -50,
                #size=p2["Population"]/30000,
                #sizemode='area',
                size = 11,
                line_width=1,
                line_color = 'white',
                color = p2[yaxis_column_name],
                symbol = 'star',
                cmax = 50,
                colorbar_title=dict(text=const.UNITS_PC[yaxis_column_name],side='right'),
            )))
    fig.update_layout(
        legend = dict(bgcolor=const.DISP['fades'],
        bordercolor=const.DISP['text'],
        borderwidth=2, font = dict(size = 18, color = 'white')),
        geo = dict(
            showland = True,
            landcolor = const.MAP_COLORS['lake'],
            coastlinewidth=0,
            oceancolor = const.MAP_COLORS['ocean'],
            subunitcolor = const.MAP_COLORS['land'],
            countrycolor = const.MAP_COLORS['land'],
            countrywidth = 0.5,
            showlakes = True,
            lakecolor = const.MAP_COLORS['ocean'],
            showocean=True,
            #showsubunits = True,
            showcountries = True,
            resolution = 50,
        ),
        plot_bgcolor = 'white',
        template = 'simple_white',
    legend_x=0, legend_y=0.5,
            #title = '13,000 Cities ' +units[yaxis_column_name]+' Concentration in '+str(year_value)+'<br>(Hover for values)'
        )
    
# #     fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')  
    fig.update_layout(coloraxis_colorbar_x=-0.15,legend_title_text='Click to isolate cities', plot_bgcolor= 'white', paper_bgcolor='white')
    fig.update_geos(showframe=False)
    fig.update_layout(
        font=dict(
        size=const.FONTSIZE,
        family = const.FONTFAMILY
        ))
    #f#ig.update_traces(customdata=dff['CityCountry'])
    
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig



@callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)

def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    
    if active_tab is not None:
        if active_tab == "about":
            return [dbc.Row(dbc.Col(about_acc))]
        elif active_tab == "welcome_map":
            return [dbc.Row([dbc.Col(button_group),dbc.Col(),dbc.Col(metrics,className="radio-group")]),dbc.Row(graph),dbc.Row(dbc.Col(slider))]#,dbc.Row(dbc.Col(slider))]
        elif active_tab == "percent_change":
            return [dbc.Row(html.H4(children='Percent Change in Concentration between 2010-2011 and 2018-2019',style={
                    'textAlign': 'center',
                    'color': const.DISP['text'],'font-weight':'bold'})),dbc.Row(dbc.Col(button_group)),dbc.Row(pc_graph)]
        elif active_tab=='download':
            return dbc.Stack([dbc.Row(html.H5(children='Select the country, city and/or year range to download filtered dataset (button below table)',style={
                    'textAlign': 'center',
                    'color': const.DISP['text'],'font':'helvetica'})),dbc.Row([dbc.Col(country_drop, width=5),dbc.Col(city_drop)]),dbc.Row(range_slider),dbc.Row(dtable),dbc.Row(download_button),dbc.Row(download_component)],gap=2)
        elif active_tab == 'inst_video':
            return [dbc.Row([inst_video], justify="center")]
        elif active_tab=='codebook':
            return [dbc.Row(dbc.Stack([dbc.Row(download),dbc.Row(),dbc.Row(tt),dbc.Row(html.Hr()),dbc.Row(dbc.Col(table))],gap=2))]
            
    return "Content coming soon."
    



