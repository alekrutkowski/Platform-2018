# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:03:08 2016

@author: arranda
"""
import glob
import os
import os.path
import pandas as pd

yearlistC=['2020','2021']#'2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019',

yearlistL=['2013','2014','2015','2016','2017','2018','2019','2020']#'2005','2006','2007','2008','2009','2010','2011','2012',

#thedir='C:\\Users\\smarkus\\Documents_local\\EUROSTAT_Microdata\\EU_SILC\\data\\'
#thedirD='C:\\Users\\smarkus\\Documents_local\\EUROSTAT_Microdata\\EU_SILC\\Result\\'

thedir = "C:\\Users\\franfab\\microdata\\EUSILC\\unzipped\\"
thedirD = "C:\\Users\\franfab\\microdata\\EUSILC\\result\\"

#subfolders=[ name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) and name!='_merged' ]

# This function merges the four files for each country, every year, for CROSS and LONG
def mergeDHPR(yearlist,folder):
    os.chdir(thedir+folder)
    thedirC=thedir+folder
    clean=pd.DataFrame(columns=['Country','Year','File','Before','After'])
    countries=[ name for name in os.listdir(thedirC) if os.path.isdir(os.path.join(thedirC, name)) and name!='_merged' ]
    #countries=['RO','RS','SE','SI','SK','UK']
    for ctry in countries:
        thedirCC=thedirC+'\\'+ctry
        os.chdir(thedirC+'\\'+ctry)
        years=[ name for name in os.listdir(thedirCC) if os.path.isdir(os.path.join(thedirCC, name)) and name!='_merged' ]
        for year in years:
            os.chdir(thedirCC+'\\'+year)
            filelist = glob.glob("*.csv")
            print(filelist)
            thedirCCY=thedirCC+'\\'+year #
            for file in filelist:
                if "D.csv" in file:
                    template=[['',0,'',0,0]]
                    tmp=pd.DataFrame(template,columns=['Country','Year','File','Before','After'])
                    tmp['Country']=ctry
                    tmp['Year']=year
                    tmp['File']=file
                    d=pd.read_csv(thedirCCY+'\\'+file)      
                    d=d.rename(columns = {'DB010':'YEAR','DB020':'COUNTRY','DB030':'HH_ID' })
                    print('File '+file+' is '+str(len(d))+' long.')
                    tmp['Before']=len(d)
                    d.sort_values("HH_ID", inplace = True)
                    d.drop_duplicates(keep = 'first', inplace = True)
                    tmp['After']=len(d)
                    print('File '+file+' is '+str(len(d))+' long after cleaning.')
                    clean=clean.append(tmp)
                if "H.csv" in file:
                    template=[['',0,'',0,0]]
                    tmp=pd.DataFrame(template,columns=['Country','Year','File','Before','After'])
                    tmp['Country']=ctry
                    tmp['Year']=year
                    tmp['File']=file
                    h=pd.read_csv(thedirCCY+'\\'+file)
                    h=h.rename(columns = {'HB010':'YEAR','HB020':'COUNTRY','HB030':'HH_ID' })
                    print('File '+file+' is '+str(len(h))+' long.')
                    tmp['Before']=len(h)
                    h.sort_values("HH_ID", inplace = True)
                    h.drop_duplicates(keep = 'first', inplace = True)
                    tmp['After']=len(h)
                    print('File '+file+' is '+str(len(h))+' long after cleaning.')
                    clean=clean.append(tmp)
                if "P.csv" in file:
                    template=[['',0,'',0,0]]
                    tmp=pd.DataFrame(template,columns=['Country','Year','File','Before','After'])
                    tmp['Country']=ctry
                    tmp['Year']=year
                    tmp['File']=file
                    p=pd.read_csv(thedirCCY+'\\'+file)
                    p=p.rename(columns = {'PB010':'YEAR','PB020':'COUNTRY','PB030':'PERS_ID' ,'PX030':'HH_ID'})
                    print('File '+file+' is '+str(len(p))+' long.')
                    tmp['Before']=len(p)
                    p.sort_values("PERS_ID", inplace = True)
                    p.drop_duplicates(keep = 'first', inplace = True)
                    tmp['After']=len(p)
                    print('File '+file+' is '+str(len(p))+' long after cleaning.')
                    clean=clean.append(tmp)
                if "R.csv" in file:
                    template=[['',0,'',0,0]]
                    tmp=pd.DataFrame(template,columns=['Country','Year','File','Before','After'])
                    tmp['Country']=ctry
                    tmp['Year']=year
                    tmp['File']=file
                    r=pd.read_csv(thedirCCY+'\\'+file)
                    if folder=='Cross':
                        r=r.rename(columns = {'RB010':'YEAR','RB020':'COUNTRY','RB030':'PERS_ID' ,'RX030':'HH_ID'})
                    if folder=='Long':
                        r=r.rename(columns = {'RB010':'YEAR','RB020':'COUNTRY','RB030':'PERS_ID' ,'RB040':'HH_ID'})
                    print('File '+file+' is '+str(len(r))+' long.')
                    tmp['Before']=len(r)
                    r.sort_values("PERS_ID", inplace = True)
                    r.drop_duplicates(keep = 'first', inplace = True)
                    tmp['After']=len(r)
                    print('File '+file+' is '+str(len(r))+' long after cleaning.')
                    clean=clean.append(tmp)
 
            mess=ctry+" - "+str(year)+" - "+folder+"."
            dh=pd.merge(d,h,on=['YEAR','COUNTRY','HH_ID'], how='outer')
            if (len(d) != len(dh)) and (len(h) != len(dh)):
                print("Problem with DH merge in: "+mess)
            pr=pd.merge(p,r,on=['YEAR','COUNTRY','PERS_ID'], how='outer')
            if len(p)>len(r):
                pr=pr.rename(columns = {'HH_ID_x':'HH_ID'})
                pr=pr.drop(['HH_ID_y'], axis=1)
            else:
                pr=pr.rename(columns = {'HH_ID_y':'HH_ID'})
                pr=pr.drop(['HH_ID_x'], axis=1)                        
            if (len(p) != len(pr)) and (len(r) != len(pr)):
                print("Problem with PR merge in: "+mess)
            
            final=pd.merge(pr,dh,on=['YEAR','COUNTRY','HH_ID'], how='outer')
            final.to_csv(thedirC+'\\_merged\\'+ctry+'_'+year+'.csv')
            print('Final file is '+str(len(final))+' long.')

    clean.to_csv(thedir+folder+'_doublets.csv')        

# This function merges all countries for a year, building the SILC yearly data.
def combinecountries(yearlist,folder,init):
    thedirmerge=thedir+folder+'\\_merged\\'
    os.chdir(thedirmerge)
    filelist = glob.glob("*.csv")
    for year in yearlist:
        print(year)
        yearSILC=pd.DataFrame()
        for file in filelist:
            if year == file[3:7]:
                f=pd.read_csv(thedirmerge+file)
                print('The file '+file+' has '+str(len(f.columns))+' columns.')
                yearSILC=yearSILC.append(f)
        yearSILC.to_csv(thedirD+'SILC_'+init+'_'+str(year)+'_all.csv')
                
# Obsolete      
def clean(yearlist,init):       
    for year in yearlist:
        change='FALSE'
        df=pd.read_csv(thedirD+'SILC_'+init+'_'+str(year)+'_all.csv')
        print(year+' file is opened...')
        col=set(df.columns)
        if 'Unnamed: 0' in col:
            df=df.drop(['Unnamed: 0'], axis=1)
            change='TRUE'
        if 'Unnamed: 0.1' in col:
            df=df.drop(['Unnamed: 0.1'], axis=1)
            change='TRUE'
        lst=sorted(set(df.COUNTRY))
        print(lst)
        if 'GR' in lst:
            df.loc[(df.COUNTRY=='GR'),'COUNTRY']='EL'
            change='TRUE'
        lst=sorted(set(df.COUNTRY))
        print(lst)
        if (change=='TRUE'):
            df.to_csv(thedirD+'SILC_'+init+'_'+year+'_all.csv')
            print(year+' file is saved...')


# This function reports on wrong codes in 'personal' and 'register' files
def check_codes(yearlist,folder):
    os.chdir(thedir+folder)
    thedirC=thedir+folder
    codes=pd.DataFrame(columns=['File','Type','YEAR','COUNTRY','PERS_ID','HH_ID','Dif'])
    countries=[ name for name in os.listdir(thedirC) if os.path.isdir(os.path.join(thedirC, name)) and name!='_merged' ]
    for ctry in countries:
        thedirCC=thedirC+'\\'+ctry
        os.chdir(thedirC+'\\'+ctry)
        years=[ name for name in os.listdir(thedirCC) if os.path.isdir(os.path.join(thedirCC, name)) and name!='_merged' ]
        for year in years:
            os.chdir(thedirCC+'\\'+year)
            filelist = glob.glob("*.csv")
            print(filelist)
            thedirCCY=thedirCC+'\\'+year
            for file in filelist:
                if "P.csv" in file:
                    p=pd.read_csv(thedirCCY+'\\'+file)
                    p=p.rename(columns = {'PB010':'YEAR','PB020':'COUNTRY','PB030':'PERS_ID' ,'PX030':'HH_ID'})
                    p=p[['YEAR','COUNTRY','PERS_ID','HH_ID']]
                    p['Dif']=p.PERS_ID-100*p.HH_ID
                    p=p[(p.Dif<0) | (p.Dif>100)]
                    p['Type']='P'
                    p['File']=file
                    #p.to_csv('D:\\SILC\\Clean\\Codes\\'+file)
                    codes=codes.append(p)
                if "R.csv" in file:
                    r=pd.read_csv(thedirCCY+'\\'+file)
                    if folder=='Cross':
                        r=r.rename(columns = {'RB010':'YEAR','RB020':'COUNTRY','RB030':'PERS_ID' ,'RX030':'HH_ID'})
                    if folder=='Long':
                        r=r.rename(columns = {'RB010':'YEAR','RB020':'COUNTRY','RB030':'PERS_ID' ,'RB040':'HH_ID'})
                    r=r[['YEAR','COUNTRY','PERS_ID','HH_ID']]
                    r['Dif']=r.PERS_ID-100*r.HH_ID
                    r=r[(r.Dif<0) | (r.Dif>100)]
                    r['Type']='R'
                    r['File']=file
                    #r.to_csv('D:\\SILC\\Clean\\Codes\\'+file)
                    codes=codes.append(r)
                    
    codes.to_csv(thedir+'Wrong_codes_'+folder+'.csv')

check_codes(yearlistC,'Cross')    
#check_codes(yearlistL,'Long')
mergeDHPR(yearlistC,'Cross')
#mergeDHPR(yearlistL,'Long')
combinecountries(yearlistC,'Cross','C')
#combinecountries(yearlistL,'Long','L')
#clean(yearlistC,'C')
#clean(yearlistL,'L')
