# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 14:14:31 2018

@author: arranda
"""
from util.download_data import *
from util.tools import *

#Configuration
cod_comp=['GDHI','COMPEMP','COMPSLFEMP','NETPROPINC','OTCURTRANS','TAXINC','SOCBEN']
EU27=['AT','BE','BG','CY','CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK','EU27_2020', 'EA19']

components={}
components['GDHI']=['B6G','RECV'] #'Gross disposable household income'
components['COMPEMP']=['D1','RECV'] # Compensation of employees
components['COMPSLFEMP']=['B2A3G','PAID'] #Gross operating surplus and mixed income
components['NETPROPINC_1']=['D4','RECV'] #'Net property income'
components['NETPROPINC_2']=['D4','PAID']
components['OTCURTRANS_1']=['D7','RECV'] #	'Other current transfers'
components['OTCURTRANS_2']=['D7','PAID']
components['TAXINC']=['D5','PAID'] #	'Taxes on income'
components['SOCBEN_1']=['D62','RECV'] #'Net social benefits'
components['SOCBEN_2']=['D62','PAID']
components['SOCBEN_3']=['D61','RECV']
components['SOCBEN_4']=['D61','PAID']

#time could be 'year' or 'quarter'
def read_data(time, currency,defl):
    if time=='year':
        download_and_stack(['nasa_10_nf_tr', 'nama_10_gdp'])
        nominal_gdhi=pd.read_csv(stacked_path+'nasa_10_nf_tr.csv')
        nominal_gdhi=nominal_gdhi[(nominal_gdhi.year > 1999)]  
        deflator= pd.read_csv(stacked_path+'nama_10_gdp.csv')  
        deflator=deflator[(deflator.year > 1999)]                       
    elif time=='quarter':     
        download_and_stack(['nasq_10_nf_tr', 'namq_10_gdp'])
        nominal_gdhi=pd.read_csv(stacked_path+'nasq_10_nf_tr.csv')        
        nominal_gdhi=nominal_gdhi[nominal_gdhi.s_adj =='NSA']
        #nominal_gdhi=nominal_gdhi[nominal_gdhi.s_adj =='SCA']
        nominal_gdhi=nominal_gdhi[nominal_gdhi['year'].str[0:1]=='2']
        deflator= pd.read_csv(stacked_path+'namq_10_gdp.csv')
        deflator=deflator[deflator.s_adj =='NSA']
        #deflator=deflator[deflator.s_adj =='SCA']
        deflator=deflator[deflator['year'].str[0:1]=='2' ]
    else:
        print("ERROR, wrong time parameter for read_data function")
    
    nominal_gdhi=nominal_gdhi[(nominal_gdhi.sector =='S14_S15')&(nominal_gdhi.unit==currency)&(nominal_gdhi.geo.isin(EU27)) ]    
    deflator=deflator[(deflator.unit ==defl)&(deflator.na_item =='P31_S14_S15')&(deflator.geo.isin(EU27))]
    return [nominal_gdhi,deflator]
    
def prepare_components(data):
    data['component']='None'
    for i in components.keys():        
        data.loc[(data.na_item==components[i][0]) & (data.direct==components[i][1]), 'component']=i        
    data=data[data.component!='None']
    data=data[['geo','year','value_n', 'component']]
    
    x=data.set_index(['year','geo','component'])
    x=x.unstack()
    x.columns=x.columns.get_level_values(1)
    x=x.reset_index()
    x['NETPROPINC']=x['NETPROPINC_1']-x['NETPROPINC_2']
    x['OTCURTRANS']=x['OTCURTRANS_1']-x['OTCURTRANS_2']
    x['TAXINC']=-1*x['TAXINC']
    x['SOCBEN']=x['SOCBEN_1']-x['SOCBEN_2']+x['SOCBEN_3']-x['SOCBEN_4']
    return x
    
def growth(group):    
    for i in cod_comp:
        if i =='GDHI':
            group['GDHI_growth']=100*group['GDHI'].pct_change()            
        else:
            group[i+'_contribution']=100*(group[i]-group[i].shift(1))/group['GDHI'].shift(1)
    return group   

def quarterlyGrowth(group):    
    for i in cod_comp:
        if i =='GDHI':
            #group['GDHI_growth']=100*group['GDHI'].pct_change(periods=4)    
            group['GDHI_growth']=100*(group['GDHI']-group['GDHI'].shift(4))/group['GDHI'].shift(4)
        else:
            group[i+'_contribution']=100*(group[i]-group[i].shift(4))/group['GDHI'].shift(4)
    return group 

def deflate(data, deflator):
    deflator['deflator']=deflator['value_n']
    deflator=deflator[['geo','year','deflator']]
    realData=pd.merge(data, deflator, on=['geo','year'])    
    for i in cod_comp:
        realData[i]=100*realData[i]/realData['deflator']
    return realData
    
def prepareFile(file, indicator):
    file=file.set_index(['year','geo'])
    file=file.stack()
    file=file.reset_index()
    file.columns=['year','geo','component','value_n']
    file['indicator']=indicator
    return file
 
def reIndex(group):
    a=group[group.year==2008]['ratio']    
    group['value_n']=100*group['ratio']/float(a.iloc[0]) # was float(a) => FutureWarning: Calling float on a single element Series is deprecated and will raise a TypeError in the future. Use float(ser.iloc[0]) instead
    return group

def reIndexQuarterly(group):
    a=group[group.year.isin(['2012Q1','2012Q2','2012Q3','2012Q4'])]['ratio'].mean()    
    group['value_n']=100*group['ratio']/float(a.iloc[0]) # was float(a) => FutureWarning: Calling float on a single element Series is deprecated and will raise a TypeError in the future. Use float(ser.iloc[0]) instead
    return group

def GDHI_per_capita(realData, time, column):
    #download population data
    # Read population nama_10_pe
    if time=='year':
        download_and_stack(['nama_10_pe'])
        POP=pd.read_csv(stacked_path+'nama_10_pe.csv')
        POP = POP[(POP.unit=='THS_PER') & (POP.na_item=='POP_NC') & (POP.geo.isin(EU27))]        
    elif time=='quarter':
        download_and_stack(['namq_10_pe'])
        POP=pd.read_csv(stacked_path+'namq_10_pe.csv')
        POP = POP[(POP.unit=='THS_PER') & (POP.na_item=='POP_NC') & (POP.s_adj=='NSA')  & (POP.geo.isin(EU27))]        
        #POP = POP[(POP.unit=='THS_PER') & (POP.na_item=='POP_NC') & (POP.s_adj=='SCA')  & (POP.geo.isin(EU27))]
    POP = POP[['geo','year','value_n','flag']]
    POP.columns=['geo','year','pop','pflag']
    realData=realData[['geo','year',column]]
    final=pd.merge(POP, realData, on=['geo','year'])
    final['ratio']=final[column]/final['pop']  
    return final      
     
def yearlyGDHI():    
    #Flow year   
    data, deflator= read_data('year','CP_MNAC','PD10_NAC')
    data=prepare_components(data)
    #Nominal growth
    dataGrowth=(data.sort_values(by=['year'])).groupby('geo').apply(growth)
    #real data
    realData= deflate(data, deflator)
    #real Data growth
    realDataGrowth=(realData.sort_values(by=['year'])).groupby('geo').apply(growth)    
    
    #Prepare and save files
    final= prepareFile(dataGrowth, 'nominal')
    final=pd.concat([final, prepareFile(realDataGrowth, 'real')], ignore_index=True) # final=final.append(prepareFile(realDataGrowth, 'real')) # https://stackoverflow.com/a/75956237
    final.to_csv(calculated_path+'GDHI_a.csv',index=False, float_format='%.3f')
    
    #Calculate indicator for scoreboard
    #Real non-adjusted based in NAC GDHI per capita and indexed
    per_capita=GDHI_per_capita(realData, 'year', 'GDHI')
    per_capita=per_capita.groupby('geo').apply(reIndex)
    per_capita.to_csv(calculated_path+'real_GDHI_a_per_capita_index.csv',index=False, float_format='%.3f')

def quarterlyGDHI(): 
    #Flow quarter
    data, deflator=read_data('quarter','CP_MNAC','PD10_NAC')
    data=prepare_components(data)
    #Nominal growth
    dataGrowth=(data.sort_values(by=['year'])).groupby('geo').apply(quarterlyGrowth)
    #real data
    realData= deflate(data, deflator)
    #real Data growth
    realDataGrowth=(realData.sort_values(by=['year'])).groupby('geo').apply(quarterlyGrowth)
    
    #Prepare and save files
    final= prepareFile(dataGrowth, 'nominal')
    final=pd.concat([final, prepareFile(realDataGrowth, 'real')], ignore_index=True) # final=final.append(prepareFile(realDataGrowth, 'real')) # https://stackoverflow.com/a/75956237
    final.to_csv(calculated_path+'GDHI_q.csv',index=False, float_format='%.3f')
    #final.to_csv(calculated_path+'GDHI_q_SCA.csv',index=False, float_format='%.3f')
    
    #Calculate quarterly indicator similar to the one used in the JER scoreboard
    #Real non-adjusted based in NAC GDHI per capita and indexed
    per_capita=GDHI_per_capita(realData, 'quarter', 'GDHI')
    per_capita=per_capita.groupby('geo').apply(reIndexQuarterly)
    per_capita.to_csv(calculated_path+'real_GDHI_q_per_capita_index.csv',index=False, float_format='%.3f')
    #per_capita.to_csv(calculated_path+'real_GDHI_q_per_capita_index_SCA.csv',index=False, float_format='%.3f')

#Real non-adjusted GDHI per capita in EU annual and quarterly
def GDHI_EUR_per_capita():
    for my_time in ['year', 'quarter']: 
        data, deflator= read_data(my_time,'CP_MEUR','PD10_EUR')
        #filter to have only GDHI
        data=data[(data.na_item=='B6G') & (data.direct=='RECV')]
        #Deflate
        deflator['deflator']=deflator['value_n']
        deflator=deflator[['geo','year','deflator']]
        realData=pd.merge(data, deflator, on=['geo','year'])          
        realData['value_n']=100*realData['value_n']/realData['deflator']
        per_capita=GDHI_per_capita(realData, my_time, 'value_n')
        per_capita['gdhi']=per_capita['value_n']
        per_capita['value_n']=per_capita['ratio']*1000
        per_capita.to_csv(calculated_path+'real_GDHI_'+my_time+'_per_capita_EUR.csv',index=False, float_format='%.3f')

# yearlyGDHI()
quarterlyGDHI()
GDHI_EUR_per_capita()

#TO DO: PRODUCE QUARTERLY GDHI SCA
#comment in/out NSA and SCA quarterly calculations or create "switch"
#New functions to be developed for SCA
#Problem: some MS and EU have only NSA population -> use NSA population for those?