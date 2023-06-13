# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 09:35:56 2015

@author: arranda
"""

from tools import * 
from util.catalogues import *
from matplotlib import pyplot as plt
#import numpy as np
#import pandas as pd
from matplotlib_venn import venn3, venn3_circles


files=["ilc_lvhl11n","ilc_li02","ilc_pees01n","ilc_mdsd11", "ilc_peps01n"]
download_and_stack(files)

ilc_lvhl11=pd.read_csv(stacked_path+"ilc_lvhl11n.csv") 
ilc_li02=pd.read_csv(stacked_path+"ilc_li02.csv") 
ilc_mddd11=pd.read_csv(stacked_path+"ilc_mdsd11.csv") 
ilc_pees01=pd.read_csv(stacked_path+"ilc_pees01n.csv")  
ilc_peps01=pd.read_csv(stacked_path+"ilc_peps01n.csv")  


countries=['BE','BG','CZ','DK','DE','EE','IE','EL','ES','FR','HR','IT','CY','LV','LT','LU','HU','MT','NL','AT','PL','PT','RO','SI','SK','FI','SE']

for country in countries:
    
    #checks if there are all intersections for the selected year, otherwise downloads data of previous year
    year=2021
    if len(ilc_pees01n[(ilc_pees01n.sex=='T') & (ilc_pees01n.age=='TOTAL') & (ilc_pees01n.unit=='THS_PER')  & (ilc_pees01n.geo==country)  & (ilc_pees01n.year==year) & (ilc_pees01n.value_n.notnull())])<8 :
        year=year-1        
    print(country+"--"+str(year))
    
    mydata=ilc_pees01n[(ilc_pees01n.geo==country) & (ilc_pees01n.year==year) & (ilc_pees01n.unit=='THS_PER') & (ilc_pees01n.age=='TOTAL') & (ilc_pees01n.sex=='T')]
    #mydata=mydata.sort(columns=['indic_il'])
    mydata=mydata.sort_values(by=['indic_il'])
    x=list(mydata['value_n'])
    total_arope=list(ilc_peps01n[(ilc_peps01n.geo==country) & (ilc_peps01n.year==year) & (ilc_peps01n.unit=='THS_PER') & (ilc_peps01n.age=='TOTAL') & (ilc_peps01n.sex=='T')]['value_n'])[0]
    
    arop=ilc_li02[(ilc_li02.geo==country) & (ilc_li02.year==year) & (ilc_li02.unit=='THS_PER') & (ilc_li02.age=='TOTAL') & (ilc_li02.sex=='T')&(ilc_li02.indic_il=="LI_R_MD60")]
    level_arop=int(list(arop['value_n'])[0])
    
    vlwi=ilc_lvhl11n[(ilc_lvhl11n.geo==country) & (ilc_lvhl11n.year==year) & (ilc_lvhl11n.unit=='THS_PER') & (ilc_lvhl11.age=='Y_LT65') & (ilc_lvhl11n.sex=='T')]
    level_vlwi=int(list(vlwi['value_n'])[0])
    
    smd=ilc_mdsd11[(ilc_mdsd11.geo==country) & (ilc_mdsd11.year==year) & (ilc_mdsd11.unit=='THS_PER') & (ilc_mdsd11.age=='TOTAL') & (ilc_mdsd11.sex=='T')]
    level_smsd=int(list(smd['value_n'])[0])
    
    plt.figure(figsize=(8,8))
    v = venn3(subsets=(x[7],x[2],x[6],x[1],x[5],x[0],x[4]), set_labels = ("AROP:"+str(round((100*level_arop/total_arope),1))+ "%\n"+str(level_arop)+ " ths", "(quasi-)jobless HHs:\n"+str(round((100*level_vlwi/total_arope),1))+" %\n "+str(level_vlwi)+ " ths", "SMD:"+str(round((100*level_smsd/total_arope),1))+" %\n "+str(level_smsd)+ " ths"))
   
    v.get_patch_by_id('100').set_color('#000033')
    v.get_patch_by_id('010').set_color('#0000FF')
    v.get_patch_by_id('001').set_color('#0000CC')
    v.get_patch_by_id('110').set_color('#006633')
    v.get_patch_by_id('101').set_color('#006699')
    v.get_patch_by_id('011').set_color('#009966')
    v.get_patch_by_id('111').set_color('#0066FF')
    
   
    v.get_label_by_id('100').set_text(str(round((100*x[7]/total_arope),1))+ "%")
    v.get_label_by_id('010').set_text(str(round((100*x[2]/total_arope),1))+ "%")    
    v.get_label_by_id('110').set_text(str(round((100*x[6]/total_arope),1))+ "%")
    v.get_label_by_id('001').set_text(str(round((100*x[1]/total_arope),1))+ "%")
    v.get_label_by_id('101').set_text(str(round((100*x[5]/total_arope),1))+ "%")
    v.get_label_by_id('011').set_text(str(round((100*x[0]/total_arope),1))+ "%")
    v.get_label_by_id('111').set_text(str(round((100*x[4]/total_arope),1))+ "%")
    
    c = venn3_circles(subsets=(x[7],x[2],x[6],x[1],x[5],x[0],x[4]), linestyle='solid')
    plt.suptitle(country+" - "+ str(year), fontsize=18, fontweight='bold')
    
    plt.annotate(str(int(x[4]))+" ths", xy=v.get_label_by_id('111').get_position() - np.array([0, 0.05]), xytext=(-140,-90),
             ha='center', textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='#ff9933', alpha=1),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',color='gray'))
             
    
    plt.annotate("Total Arope Pop.\n"+str(int(total_arope))+" ths", xy=np.array([0.25, 0.05]), xytext=(85,220),
             ha='center', textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='#006633', alpha=0.5))
    
     
    plt.savefig("G:\\A4\\04 Data and tools\\Reports\\SPPM Country profiles\\type\\venn\\"+country)   
    
      
    plt.close()
    #break
    
    
    
    
    
    
    
    