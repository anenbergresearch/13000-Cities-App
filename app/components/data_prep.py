import pandas as pd
import numpy as np
import json
import pickle
from urllib.request import urlopen

df = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/unified_data_SYK_Apr2025.csv')

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

##Dataframe to be passed to other pages
DFILT = pd.concat([ds,da])

#DFILT['CityCountry'] = DFILT.City + ', ' + DFILT.Country + ' (' +DFILT.ID.apply(int).apply(str) +')'
countries = ['United States','China','India']

col_stats = ['Population','NO2','PM','O3','CO2','PAF_PM','PAF_NO2','PAF_O3','Cases_NO2','Cases_PM','Cases_O3','Rates_NO2','Rates_O3','Rates_PM']

df = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/unified_data_SR-v2.csv')
#df['CO2']= df['CO2']/2000
STATES_DF ={}
##Read US csv from GIT
STATES_DF['United States'] = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/IDtoStateUnited%20States.csv')


GJSON={}
for i in ['India','China']:
    STATES_DF[i] = pd.read_csv('https://raw.githubusercontent.com/anenbergresearch/app-files/main/IDtoState'+i+'.csv')
    url = "https://raw.githubusercontent.com/anenbergresearch/app-files/main/states_" +i.lower()+".geojson"
    response = urlopen(url)
    GJSON[i]= json.loads(response.read())
id_dict={}

with open('./pages/geojs/chinadict.pickle', 'rb') as handle:
    id_dict['China'] = pickle.load(handle)
    
def calculate_change(low,high,df,pol):
    lowb = low+1
    highb = high-1
    ldf= df.query('@low <=Year <=@lowb').groupby('CityCountry')[['Population',pol]].mean()
    hdf = df.query('@highb <=Year <=@high').groupby('CityCountry')[['Population',pol]].mean()
    return ((hdf[pol]-ldf[pol])/ldf[pol])*100

DF_CHANGE = DFILT.query('Year == 2019')[['CityCountry','Latitude','Longitude','Population','C40']].set_index('CityCountry')

for i in ['NO2','PM','O3','CO2']:
    DF_CHANGE[i] = calculate_change(2010,2019,DFILT,i)
DF_CHANGE.reset_index(inplace=True)
def find_stats(dataframe,region):
    me = dataframe.groupby([region,'Year']).mean(numeric_only=True)[col_stats].round(decimals= 2)
    dd = dataframe[[region,'Year','Population','O3','NO2','PM','CO2','PAF_PM','PAF_NO2','PAF_O3','Cases_NO2','Cases_PM','Cases_O3','Rates_NO2','Rates_O3','Rates_PM']].dropna()
    for i in col_stats[1:]:
        me['w_'+i] =dd.groupby([region,'Year']).apply(w_avg,i,'Population')
    me.Population = me.Population.round(decimals=-3)
    me = me.reset_index()
    #me['iso'] = coco.convert(names=me.Country,to='ISO3')

    _ma = dataframe.groupby([region,'Year']).max(numeric_only=True)[col_stats].round(decimals = 2)
    _ma.Population = me.Population
    _ma = _ma.reset_index()

    _mi = dataframe.groupby([region,'Year']).min(numeric_only=True)[col_stats].round(decimals = 2)
    _mi.Population = me.Population
    _mi = _mi.reset_index()
    
    _co = dataframe.groupby([region,'Year']).count()[col_stats]
    _co = _co.reset_index()
    return me,_ma,_mi, _co

MEAN,MAX,MIN,COUNT = find_stats(DFILT,'Country')

DF = {}
MEAN_DF = {}
STATS ={}
col_select = ['ID','City','C40','Year','Population','NO2','PM','O3','CO2','PAF_PM','PAF_NO2','PAF_O3','Cases_NO2','Cases_PM','Cases_O3','Rates_NO2','Rates_O3','Rates_PM']
for i in countries:
    DF[i] = DFILT.query('Country ==@i')[col_select]
    DF[i] = DF[i].merge(STATES_DF[i][['ID','State']], how='left',on='ID')
    if i =='China':
        DF[i] = DF[i][DF[i].State != '자강도']
        DF[i]["State"] = DF[i]["State"].apply(lambda x: id_dict[i][x])
    DF[i]['CityID'] = DF[i].City + ' (' +DF[i].ID.apply(int).apply(str) +')'
    mean, _max, _min,count = find_stats(DF[i],'State')
    STATS[i]={'mean':mean,'min':_min,'max':_max,'count':count}
    MEAN_DF[i] = DF[i].groupby('Year')[col_stats[1:]].mean().reset_index()
    

