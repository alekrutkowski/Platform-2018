# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 16:12:41 2016

@author: arranda
"""

import pandas as pd
import  numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

#Load data and configuration
CtryList=['AT','BE','BG','CY', 'CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK','UK']
path='G:\\A4\\04 Data and tools\\Reports\\EPM_SPPM_analysis\\'


#Each of the arrays contain [cut-off point, std threshold]
test_set=[[0.025,1],[0.05,1],[0.075,1], [0.1,1], [0.075,0.75], [0.1,0.75]]
result= pd.DataFrame(columns=('dashboard','IndicatorID', 'description', 'Change','sense','years', 'cut-off/SD','threshold',  'nr data points', 'pct_green flags', 'pct_red flags', 'pct_total flags'))
    
for myDashboard in [True, False]:
    checkRuleOfThumb=True
    for mySet in test_set:
        #parameters
        cut_off=mySet[0]
        stadDev=mySet[1]    
        isEPM=myDashboard    
        
        if isEPM:
            #EPM
            catalogue=pd.read_csv('\\\\net1.cec.eu.int\\EMPL\\A\\A4\\04 Data and tools\\catalogues\\catalogue - EPM_dashboard.csv')
            a=pd.read_csv('\\\\s-empl-py-stat1\\eurostat$\\Data\\merged\\EPM_dashboard.csv')
            longPeriod=3
            changesGap=['1y','3y']
        else:
            #SPPM
            catalogue=pd.read_csv('\\\\net1.cec.eu.int\\EMPL\\A\\A4\\04 Data and tools\\catalogues\\catalogue - SPMM_dashboard.csv')
            a=pd.read_csv('\\\\s-empl-py-stat1\\eurostat$\\Data\\merged\\SPMM_dashboard.csv')
            longPeriod=7
            changesGap=['1y','3y']
        
        catalogue=catalogue.set_index(['IND_CODE'])
        
        #Filter the data: last 10 years, no breaks, only EU countries
        
        a=a[a.geo.isin(CtryList)]
        a=a[a.year>2005]
        #Calculate changes
        a=a.sort_values(by=['year'])
        a['change_1y_pp'] = a.groupby(['IndicatorID','geo'])['value_n'].diff(1)
        a['change_1y_%'] = a.groupby(['IndicatorID','geo'])['value_n'].pct_change(periods=1)*100
        
        #TODO change column names to make them generic
        a['change_3y_pp'] = a.groupby(['IndicatorID','geo'])['value_n'].diff(longPeriod)
        a['change_3y_%'] = a.groupby(['IndicatorID','geo'])['value_n'].pct_change(periods=longPeriod)*100
        
         
        a=a[a.flag!='b'] 
        b=a.sort_values(by=['IndicatorID','geo'])
        
        #Create the distribution of absolute values
        for type_chg in ['1y_pp','1y_%','3y_pp','3y_%']:
            b['change_'+type_chg+'_abs']=b['change_'+type_chg].abs()   
        
        # Per indicator
        for ind in catalogue.index:    
            #get Indicator
            myIndicator=b[b.IndicatorID==ind]
            #HGet the type of change and the senseof the indicator
            myChange= catalogue.loc[ind]['change']
            mySense= catalogue.loc[ind]['sense']
            myDescription=catalogue.loc[ind]['Indicator']
        
            #Create a 1y distribution and a 3y distribution
            dist_1y=''
            dist_3y=''
            if myChange=='pp':
                dist_1y=pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_1y_pp_abs', 'change_1y_pp'])
                dist_3y=pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_3y_pp_abs','change_3y_pp'])
            elif myChange=='%':
                dist_1y=pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_1y_%_abs','change_1y_%'])
                dist_3y=pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_3y_%_abs','change_3y_%'])
            else:
                print("Wrong change type in configuration")
            
            #print(ind)
            #print(dist_1y['change_1y_'+myChange+'_abs'].kurtosis())
            
        #TODO define if the distributions are going to grow over the years or we are going to have only
        # 10 years distributions
        #For the SILC long-term distribution is going to be only based in 3 years?
          
            for years in changesGap:
                #print(years)
                columnName='change_'+years+'_'+myChange+'_abs'
                distribution=eval('dist_'+years)
                distribution=distribution[~distribution[columnName].isnull()]
        #        plt.figure()
        #        plt.title(myDescription+" "+years)
        #        distribution[columnName].hist(bins=30)
        #        plt.savefig(path+'histograms\\abs_'+ind+'_'+years+'.png')
                #Copy special indicators
                if ind=='ID10' and myDashboard and years=='1y':
                    ind10=distribution.copy()
                if ind=='ID6' and not myDashboard and years=='1y':
                    ind6=distribution.copy()
        
                #Remove the outliers defined by the cut off point
                myCutPoint=distribution[columnName].quantile([1-cut_off]).iloc[0]
                distribution=distribution[distribution[columnName]<myCutPoint]
                #Calculate std
                myStd=distribution[columnName].std()*stadDev
                
                #Evaluation in the full distribution
                completeDistribution=eval('dist_'+years)
                completeDistribution=completeDistribution[~completeDistribution[columnName].isnull()]
                columnName='change_'+years+'_'+myChange
                if mySense=='pos':
                    pct_red=100*len(completeDistribution[completeDistribution[columnName]<(-1)*myStd])/len(completeDistribution)
                    pct_green=100*len(completeDistribution[completeDistribution[columnName]>myStd])/len(completeDistribution)
                elif mySense=='neg':
                    pct_green=100*len(completeDistribution[completeDistribution[columnName]<(-1)*myStd])/len(completeDistribution)
                    pct_red=100*len(completeDistribution[completeDistribution[columnName]>myStd])/len(completeDistribution)
                
                pct_total=pct_red+pct_green            
                result.loc[len(result)]=[myDashboard, ind, myDescription, myChange, mySense, years, str(100*cut_off)+" "+str(stadDev), myStd,len(completeDistribution), pct_green, pct_red, pct_total]
                
                #Check rule of thumb
                if checkRuleOfThumb:                
                    myRule=0
                    if years=='1y' and myChange=='pp':
                        myRule=0.5
                    elif  myChange=='%':
                        myRule=5
                    elif years!='1y':
                        myRule=1
                        
                    
                    if mySense=='pos':
                        pct_red=100*len(completeDistribution[completeDistribution[columnName]<(-1)*myRule])/len(completeDistribution)
                        pct_green=100*len(completeDistribution[completeDistribution[columnName]>myRule])/len(completeDistribution)
                    elif mySense=='neg':
                        pct_green=100*len(completeDistribution[completeDistribution[columnName]<(-1)*myRule])/len(completeDistribution)
                        pct_red=100*len(completeDistribution[completeDistribution[columnName]>myRule])/len(completeDistribution)
                    
                    pct_total=pct_red+pct_green
                
                    result.loc[len(result)]=[myDashboard, ind, myDescription, myChange, mySense, years, 'rule', myRule,len(completeDistribution), pct_green, pct_red, pct_total]
               
        checkRuleOfThumb=False
                
        #        plt.figure()
        #        plt.title(myDescription+" "+years)
        #        completeDistribution[columnName].hist(bins=30)
        #        plt.savefig(path+'histograms\\total_'+ind+'_'+years+'.png')
    result.to_csv(path+'analysis.csv', index=False)    


plt.figure()         
plt.title("AROP for pop. in (quasi-) jobless households")  
ind6['change_1y_pp_abs'].hist(bins=35, range=[0,17.5])
plt.savefig(path+'\\test6.png')
plt.figure()  
plt.title("Inac. & part-time  due to pers.fam.respons.")
ind10['change_1y_pp_abs'].hist(bins=40, range=[0,2])
plt.savefig(path+'\\test10.png')
    

#ANALYSIS
labels=[ '2.5% 1SD', '5% 1SD',  '7.5% 1SD',  '10% 1SD','7.5% 0.75SD','10% 0.75SD','rule of thumb']
a=pd.read_csv(path+'analysis.csv') 
a=a[a.IndicatorID!='ID27']   

y1=a[a.years=='1y']
y1=pd.DataFrame(y1, columns=['dashboard', 'IndicatorID','cut-off/SD','pct_total flags'])
y1_table=pd.pivot_table(y1, values='pct_total flags', index=['dashboard', 'IndicatorID'],columns=['cut-off/SD',], aggfunc=np.sum)
y1_2=pd.DataFrame(y1_table, columns=[ '2.5 1', '5.0 1',  '7.5 1',  '10.0 1','7.5 0.75','10.0 0.75','rule'])
plt.figure()
ax1=y1_2.plot.box()
ax1.set_ylim([0,100])
xtickNames=ax1.set_xticklabels(labels)
plt.setp(xtickNames, rotation=45, fontsize=8)
plt.title("% of 1-year changes flagged EPM+SPPM")

y1=a[(a.years=='1y') & (a.dashboard==True)]
y1=pd.DataFrame(y1, columns=['dashboard', 'IndicatorID','cut-off/SD','pct_total flags'])
y1_table=pd.pivot_table(y1, values='pct_total flags', index=['dashboard', 'IndicatorID'],columns=['cut-off/SD',], aggfunc=np.sum)
y1_2=pd.DataFrame(y1_table, columns=[ '2.5 1', '5.0 1',  '7.5 1',  '10.0 1','7.5 0.75','10.0 0.75','rule'])
plt.figure()
ax1=y1_2.plot.box()
ax1.set_ylim([0,100])
xtickNames=ax1.set_xticklabels(labels)
plt.setp(xtickNames, rotation=45, fontsize=8)
plt.title("% of 1-year changes flagged EPM")

y1=a[(a.years=='1y') & (a.dashboard==False)]
y1=pd.DataFrame(y1, columns=['dashboard', 'IndicatorID','cut-off/SD','pct_total flags'])
y1_table=pd.pivot_table(y1, values='pct_total flags', index=['dashboard', 'IndicatorID'],columns=['cut-off/SD',], aggfunc=np.sum)
y1_2=pd.DataFrame(y1_table, columns=[ '2.5 1', '5.0 1',  '7.5 1',  '10.0 1','7.5 0.75','10.0 0.75','rule'])
plt.figure()
ax1=y1_2.plot.box()
ax1.set_ylim([0,100])
xtickNames=ax1.set_xticklabels(labels)
plt.setp(xtickNames, rotation=45, fontsize=8)
plt.title("% of 1-year changes flagged SPPM")

y3=a[(a.years=='3y') & (a.dashboard==True)]
y3=pd.DataFrame(y3, columns=['dashboard', 'IndicatorID','cut-off/SD','pct_total flags'])
y3_table=pd.pivot_table(y3, values='pct_total flags', index=['dashboard', 'IndicatorID'],columns=['cut-off/SD',], aggfunc=np.sum)
y3_2=pd.DataFrame(y3_table, columns=[ '2.5 1', '5.0 1',  '7.5 1',  '10.0 1','7.5 0.75','10.0 0.75','rule'])
plt.figure()
ax1=y3_2.plot.box()
ax1.set_ylim([0,100])
xtickNames=ax1.set_xticklabels(labels)
plt.setp(xtickNames, rotation=45, fontsize=8)
plt.title("% of 3-year changes flagged EPM")

y7=a[(a.years=='3y') & (a.dashboard==False)]
y7=pd.DataFrame(y7, columns=['dashboard', 'IndicatorID','cut-off/SD','pct_total flags'])
y7_table=pd.pivot_table(y7, values='pct_total flags', index=['dashboard', 'IndicatorID'],columns=['cut-off/SD',], aggfunc=np.sum)
y7_2=pd.DataFrame(y7_table, columns=[ '2.5 1', '5.0 1',  '7.5 1',  '10.0 1','7.5 0.75','10.0 0.75','rule'])
plt.figure()
ax1=y7_2.plot.box()
ax1.set_ylim([0,100])
xtickNames=ax1.set_xticklabels(labels)
plt.setp(xtickNames, rotation=45, fontsize=8)
plt.title("% of 7-year changes flagged SPPM")


#Calculate the standard deviation   
    
#    print(ind)
#    print(b[b.IndicatorID==ind].std())
#    plt.figure()
#    b[b.IndicatorID==ind]['change'].hist(bins=50)
#    plt.figure()
#    b[b.IndicatorID==ind]['change_abs'].hist(bins=50)
##    plt.figure()
##    b[b.IndicatorID==ind]['change_%'].hist(bins=50)
##    plt.figure()
##    b[b.IndicatorID==ind]['change_%_abs'].hist(bins=50)
#    break
    


