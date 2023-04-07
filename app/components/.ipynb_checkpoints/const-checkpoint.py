
##Colors for the Cities scatter plot
CITY = [["#58a862","#00e81d"],
["#9466c9","#7905ff"],
["#9b9c3b","#f0f216"],
["#c75a8e","#f20c7a"],
["#c98443","#ff7d03"],
["#cb4f42","#ff260f"],
["#6295cd","#6295cd"]]


##Units for the different inputs
UNITS={'CO2':'CO<sub>2</sub> (tonnes)','NO2': 'NO<sub>2</sub> (ppb)','O3':'O<sub>3</sub> (ppb)','PM': 'PM (μg/m<sup>3</sup>)',"Population":'Population'}

#list of pollutants in the dataframe
POLS = ['O3','PM','NO2','CO2']

#settings for the display
DISP = {
    'background': 'white',
    'text': '#123c69',
    'subtext': '#6a8099'
}

COUNTRY_SCATTER = {'c40':dict(name='C40',color = 'rgba(30, 49, 133,0.9)',symbol='star'),'not_c40':dict(name='Other Cities',color = 'rgba(76, 179, 145,0.8)',symbol='circle')}


def pol_options(value):
    return[{"label": u'NO\u2082', "value": 'NO2'},
                    {"label": u'O\u2083', "value": 'O3'},
                    {"label": u'PM\u2082\u2085', "value": 'PM'},
                    {"label": u'CO\u2082', "value": 'CO2', 'disabled':value}]
def dtype_options(value):
    return [{'label': 'Unweighted', 'value': 'Unweighted'},{'label': 'Population Weighted', 'value': 'Population Weighted','disabled':value}]