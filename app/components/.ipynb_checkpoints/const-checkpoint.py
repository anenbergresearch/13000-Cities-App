
##Colors for the Cities scatter plot
CITY = [["#58a862","#00e81d"],
["#9466c9","#7905ff"],
["#9b9c3b","#f0f216"],
["#c75a8e","#f20c7a"],
["#c98443","#ff7d03"],
["#cb4f42","#ff260f"],
["#6295cd","#6295cd"]]

MAP_COLORS= {'ocean':'#d7e8fc','land':'#123c69','lake':'white'}
#'#1e324a' '#d7e8fc' #FFF0C3
COLORSCALE =  [[0, '#21b504'],[0.5,'#fff70a'],
                              [1,'#c70f02']] #'RdYlGn_r'
CS ={'Concentration':[[0, '#21b504'],[0.5,'#fff70a'],
                              [1,'#c70f02']],'Rates':'YlOrRd',
                              'Cases':'YlOrRd','PAF':'YlOrRd'}
##Units for the different inputs
UNITS_conc={'CO2':'CO<sub>2</sub> (tonnes)','NO2': 'NO<sub>2</sub> (ppb)','O3':'O<sub>3</sub> (ppb)','PM': 'PM<sub>2.5</sub> (μg/m<sup>3</sup>)',"Population":'Population'}

UNITS_PAF ={'NO2': 'NO<sub>2</sub> (Population Attributable Fraction %)','O3':'O<sub>3</sub> (Population Attributable Fraction %)','PM': 'PM<sub>2.5</sub> (Population Attributable Fraction %)',"Population":'Population'}

UNITS_R ={'NO2': 'NO<sub>2</sub> (Attributable Pediatric Asthma Incidence/100K)','O3':'O<sub>3</sub> (Attributable Premature Deaths)','PM': 'PM<sub>2.5</sub> (Attributable Premature Deaths/100K)',"Population":'Population'}

UNITS_C = {'NO2': 'NO<sub>2</sub> (Attributable Pediatric Asthma Incidence)','O3':'O<sub>3</sub> (Attributable Premature Deaths)','PM': 'PM<sub>2.5</sub> (Attributable Premature Deaths)',"Population":'Population'}


UNITS = {'Concentration':UNITS_conc,'PAF':UNITS_PAF,'Rates':UNITS_R,'Cases':UNITS_C}


UNITS_PC={'CO2':'Change in CO<sub>2</sub> (%)','NO2': 'Change in NO<sub>2</sub> (%)','O3':'Change in O<sub>3</sub> (%)','PM': 'Change in PM<sub>2.5</sub> (%)'}

#list of pollutants in the dataframe
POLS = ['O3','PM','NO2','CO2']

#settings for the display
DISP = {
    'background': 'white',
    'text': '#033c5a',
    'subtext': '#708090',
    'fades': '#6A8099',
}

FONTSIZE = 19
FONTFAMILY = 'Lato'
MEMBERS ={'Global Covenant of Mayors':['x','#76dfca'],'Breathe Life 2030':['star-triangle-up','#59a8d7'],'Climate Mayors (US ONLY)':['triangle-down','#3a6de5'],'Carbon Neutral Cities Alliance ':['diamond-wide','#ffa907'],'Resilient Cities Network':['hourglass','#d05d19'],'C40':['star','#ff0056']}

COUNTRY_SCATTER = {True:dict(name='C40',color = 'rgba(30, 49, 133,0.9)',symbol='star'),False:dict(name='Other Cities',color = 'rgba(76, 179, 145,0.8)',symbol='circle')}


def pol_options(value):
    return[{"label": u'NO\u2082', "value": 'NO2'},
                    {"label": u'O\u2083', "value": 'O3'},
                    {"label": u'PM\u2082\u2085', "value": 'PM'},
                    {"label": u'CO\u2082', "value": 'CO2', 'disabled':value}]
def dtype_options(value):
    return [{'label': 'Unweighted', 'value': 'Unweighted'},{'label': 'Population Weighted', 'value': 'Population Weighted','disabled':value}]

def metric_options(value):
    return[{"label": 'Concentration', "value": 'Concentration'},
                    {"label": 'PAF', "value": 'PAF','disabled':value},
                    {"label": 'Cases', "value": 'Cases','disabled':value},
                    {"label": 'Rates', "value": 'Rates', 'disabled':value}]