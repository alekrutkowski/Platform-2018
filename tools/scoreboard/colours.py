# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:55:20 2016

@author: badeape
"""
import xlsxwriter
from config.parameters import *
from config.config_scoreboard import *
from util.download_data import * # David's tool



# Data: Datafreme: data,  Scores in columns scoreL and scoreD
def  getColorGroup(row):
    if row['scoreL'] > 1 and row['scoreD']>-1:
        return 'red'
    elif ( (0.5 <row['scoreL'] <= 1)  and row['scoreD'] > -1) or ((-0.5< row['scoreL'] <= 0.5) and row['scoreD']>1):
        return 'orange'
    elif (row['scoreL'] > 0.5 and row['scoreD'] <= -1) :
        return 'yellow'
    elif (row['scoreL'] <= -0.5 and row['scoreD'] > 1) :
        return 'blue'
    elif ( -1 <row['scoreL'] <=-0.5  and row['scoreD'] <=1) or ( -0.5< row['scoreL'] <= 0.5 and row['scoreD']<=-1):
        return 'green'
    elif row['scoreL'] <= -1 and row['scoreD']<=1:
        return 'dark_green'
    elif row['scoreL'] <= 0.5 and row['scoreL'] > -0.5 and row['scoreD']<=1 and row['scoreD'] > -1:
        return 'white'

def getException(row):
    if (-0.5 < row['scoreL'] <= 0.5) and row['scoreD'] >=1 and row['ydiff']>=0 and row['sense']=='pos':
        return 'white'
    elif (-0.5 < row['scoreL'] <= 0.5) and row['scoreD'] >=1 and row['ydiff']<=0 and row['sense']=='neg':
        return 'white'
        
    elif (-1 < row['scoreL'] <= -0.5) and row['scoreD'] >=1 and row['ydiff']>=0 and row['sense']=='pos':
        return 'green'
    elif (-1 < row['scoreL'] <= -0.5) and row['scoreD'] >=1 and row['ydiff']<=0 and row['sense']=='neg':
        return 'green'
        
    elif row['scoreL'] <= -1 and row['scoreD'] >=1 and row['ydiff']>=0 and row['sense']=='pos':
        return 'dark_green'
    elif row['scoreL'] <= -1 and row['scoreD'] >=1 and row['ydiff']<=0 and row['sense']=='neg':
        return 'dark_green'
    else:
        return row['colour']
    
 # Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(localpath+"COLOURS.xlsx")
worksheet = workbook.add_worksheet('All')

# Styles
# Format for the background colours 
red = workbook.add_format({'bg_color': '#FF0000', 'border':1, 'text_wrap': True})
orange = workbook.add_format({'bg_color': '#FF9900', 'border':1, 'text_wrap': True})
yellow = workbook.add_format({'bg_color': '#FFFF00', 'border':1, 'text_wrap': True})
blue = workbook.add_format({'bg_color': '#00CCFF', 'border':1, 'text_wrap': True})
white = workbook.add_format({'border':1, 'text_wrap': True})
green = workbook.add_format({'bg_color': '#66FF66', 'border':1, 'text_wrap': True})
dark_green = workbook.add_format({'bg_color': '#11BB11', 'border':1, 'text_wrap': True})

#Widths and heights
worksheet.set_column(1, 1, 25)
              
data=pd.read_csv(localpath+"SCORES.csv")     
data['colour']=data.apply(getColorGroup, axis=1) 
data['colour1']=data.apply(getException, axis=1)
data['ind'] = 'ID'+data.Order.astype(str)
data = data[['ind','indicator','geo','year','level','scoreL','ydiff','scoreD','category','LabelL','LabelD','colour','colour1']]
data.to_csv(localpath+'SCATTER_check.csv',index=False, float_format='%.3f')   
data = data[['ind','indicator','geo','year','level','scoreL','ydiff','scoreD','category','LabelL','LabelD','colour1']]
data.columns=['ind','indicator','geo','year','level','scoreL','ydiff','scoreD','category','LabelL','LabelD','colour']
data.to_csv(localpath+'SCATTER.csv',index=False, float_format='%.3f') 
    
worksheet.write(1, 1,     "Best performers", dark_green) 
worksheet.write(2, 1,     "Better than average", green) 
worksheet.write(3, 1,     "On average", white ) 
worksheet.write(4, 1,     "Good but deteriorating", blue)
worksheet.write(5, 1,     "Weak but improving", yellow) 
worksheet.write(6, 1,     "To watch", orange) 
worksheet.write(7, 1,     "Critical situations", red) 

  
myCol=2
for myIndicator in set(data['ind']): 
    myRow=1
    worksheet.write(0, myCol, myIndicator, white) 
    for myColor in ['dark_green', 'green', 'white', 'blue', 'yellow', 'orange', 'red']:  
        countries=str(list(data[(data.colour==myColor) & (data.ind==myIndicator)]['geo']))
        countries=countries.replace("[","")
        countries=countries.replace("]","")
        countries=countries.replace("'","")
        worksheet.write(myRow, myCol, countries , eval(myColor))
        myRow+=1
    myCol+=1


for myIndicator in set(data['ind']): 
    worksheet = workbook.add_worksheet(myIndicator)
    worksheet.write(1, 1,     myIndicator) 
    worksheet.write(2, 1,     "Very high") 
    worksheet.write(3, 1,     "High") 
    worksheet.write(4, 1,     "On average") 
    worksheet.write(5, 1,     "Low")
    worksheet.write(6, 1,     "Very low") 
    worksheet.write(1, 2,     "Much higher than average") 
    worksheet.write(1, 3,     "Higher than average") 
    worksheet.write(1, 4,     "On average") 
    worksheet.write(1, 5,     "Lower than average") 
    worksheet.write(1, 6,     "Much lower than average")
        
    myRow=2
    for Row in ['Very low','Low','On average','High','Very high']:
        myCol=2
        for Col in ['Much lower than average','Lower than average','On average','Higher than average','Much higher than average']:
            countries=str(list(data[(data.LabelL==Row) & (data.LabelD==Col) & (data.ind==myIndicator)]['geo']))
            countries=countries.replace("[","")
            countries=countries.replace("]","")
            countries=countries.replace("'","")
            worksheet.write(myRow, myCol, countries)
            myCol+=1
        myRow+=1

       
workbook.close()



