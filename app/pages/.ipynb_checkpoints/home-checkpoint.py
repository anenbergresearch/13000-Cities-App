import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html, callback,dash_table
import dash_bootstrap_components as dbc
from components import buttons, const,data_prep


dash.register_page(__name__, path='/')

cb =pd.read_csv('./pages/Codebook.csv')
df = data_prep.DFILT
m_limits= {'CO2':15e6,'NO2': 28,'O3':75,'PM':100}

button_group = html.Div(
    [
        buttons.pol_buttons('')],
    className="radio-group",
)
slider = buttons.sliders(df)

graph=dcc.Graph(
            id='welcome-map')

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
    html.H1(children='Exploring Air Pollution and Emissions in 13,000 Cities',style={
                    'textAlign': 'center',
                    'color': const.DISP['text'],'font':'helvetica','font-weight': 'bold'
                    
                }),
    html.Hr(),
    dbc.Tabs([
        
        dbc.Tab(label='Map', tab_id='welcome_map'),
        dbc.Tab(label='Data Codebook', tab_id='codebook'),
        dbc.Tab(label='About', tab_id='about'),
        ],
        id='tabs',
        active_tab='welcome_map'
    ),
    html.Div(id="tab-content", className="p-4"),
    ],fluid=True
)
download= html.Div(
    [
        dbc.Button("Download CSV",
                   href='https://raw.githubusercontent.com/anenbergresearch/app-files/main/unified_data_SR.csv',
                   download='unified_data.csv',
                   external_link=True,
                   outline=True,
                   color='secondary'
                   ),
    ],
    className="d-grid gap-2 col-6 mx-auto"
)

@callback(
    Output('welcome-map', 'figure'),
    [Input('crossfilter-yaxis-column', 'value'),
     Input('crossfilter-year--slider', 'value'),
     ])

def generate_graph(yaxis_column_name,             
                 year_value):
    plot= df.query('Year == @year_value').copy()     
    plot['Text'] = '<b>'+plot['CityCountry'] + '</b><br>'+const.UNITS[yaxis_column_name]+': ' +plot[yaxis_column_name].round(2).astype(str)
    p1 = plot[plot['c40']=='not_c40'].copy()
    p2 = plot[plot['c40']=='c40'].copy()
    fig = go.Figure(data=go.Scattergeo(
            lon = p1['Longitude'],
            lat = p1['Latitude'],
            text = p1['Text'],
            hoverinfo='text',
            name= 'Non-C40 Cities',
            #marker_color = dff['NO2'],
            marker= dict(
                colorscale = 'OrRd',
                cmin = 0,
                size=p1["Population"]/30000,
                sizemode='area',
                line_width=0,
                color = p1[yaxis_column_name],
                symbol = 'circle',
                cmax = m_limits[yaxis_column_name],
                colorbar_title=const.UNITS[yaxis_column_name],
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
                colorscale = 'OrRd',
                cmin = 0,
                size=p2["Population"]/30000,
                sizemode='area',
                line_width=0,
                color = p2[yaxis_column_name],
                symbol = 'star',
                cmax = m_limits[yaxis_column_name],
                colorbar_title=const.UNITS[yaxis_column_name]
            )))
    fig.update_layout(
        geo = dict(
            showland = True,
            landcolor = "#030c54",
            coastlinewidth=0,
            oceancolor = '#022fbe',
            subunitcolor = "rgb(255, 255, 255)",
            countrycolor = "#01013F",
            countrywidth = 0.5,
            showlakes = True,
            lakecolor = '#022fbe',
            showocean=True,
            #showsubunits = True,
            showcountries = True,
            resolution = 50,
        ),
        plot_bgcolor = '#022fbe',
        template = 'simple_white',
    legend_x=0, legend_y=0,
            #title = '13,000 Cities ' +units[yaxis_column_name]+' Concentration in '+str(year_value)+'<br>(Hover for values)'
        )
    
# #     fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')  
    fig.update_layout(legend_title_text='', plot_bgcolor= '#022fbe', paper_bgcolor='white')


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
            return [dbc.Row(dbc.Col(button_group)),dbc.Row(graph),dbc.Row(dbc.Col(slider))]#,dbc.Row(dbc.Col(slider))]
        elif active_tab=='codebook':
            return[dbc.Row(dbc.Stack([dbc.Col(html.H3(children='Download the full dataset here',style={
                    'textAlign': 'center',
                    'color': const.DISP['text'],'font':'helvetica'})),dbc.Col(html.H5(children='See codebook below and the About tab for more information',style={
                    'textAlign': 'center',
                    'color': const.DISP['subtext'],'font':'helvetica'})),dbc.Col(download)])),dbc.Row(dbc.Col(table))]
            
    return "Content coming soon."
    



