# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 10:47:53 2015

@author: arranda
"""

import xlsxwriter

 # Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook("G:\\A4\\04 Data and tools\\Reports\\EPM Dashboard\\EPM_dashboard_2021_May.xlsx")
worksheet = workbook.add_worksheet()

#Formats
bold = workbook.add_format({'bold': True})
basic = workbook.add_format({'bold': True, 'align':'center', 'border':1})
st_indicator_name = workbook.add_format({'bold': True, 'align':'center', 'border':1, 'font_size':14, 'font_color':'#4F81BD'})
st_group = workbook.add_format({'bold': True,  'align':'center', 'valign':'vcenter', 'border':1, 'rotation':90,'text_wrap':True})
st_country = workbook.add_format({'font_color':'#FFFFFF', 'bg_color': '#1F497D', 'bold': True, 'align':'center', 'valign':'vcenter','border':1})
#Format for the background colours and significance
positive = workbook.add_format({'bg_color': '#C4D79B','align':'center', 'border':1})
negative = workbook.add_format({'bg_color': '#DA9694','align':'center', 'border':1})
no = workbook.add_format({'bold': True, 'align':'center','border':1})

def colAuto(start=0,step=1):
    i=start
    while 1:
        yield i
        i+=step

#General layout
worksheet.set_column(1, 1, 25)
worksheet.set_row(1, 30)

# Start from the first cell below the headers.
row = 1
#Iterator for columns, to reset per line
dynCol = colAuto()
indic=0

# Iterate over the dictionary of data using the order number as parameter
while indic < len(dashboardData): 
    #print(indic)
    indic+=1    
    #assure that the order exists because of removing and adding orders
    if indic in dashboardData:        
        #Countries row
        if indic==1 or indic==10:
            dynCol = colAuto()
            worksheet.write(row, next(dynCol),     "", basic) 
            worksheet.write(row, next(dynCol),     "", st_country) 
            for country in EU28Countries:
                worksheet.write(row, next(dynCol), country, st_country)  
            row += 1        
        
        ID, label, refYear, change, data=dashboardData[indic]        
        #Indicator name
        
        worksheet.merge_range(row, 1,row, len(EU28Countries)+1, label, st_indicator_name)        
        row += 1    
         
        rowLabels=[refYear, str(refYear-1)+"-"+str(refYear)+" change in "+ change, str(refYear-3)+"-"+str(refYear)+" change in "+ change ]    
        for subRow in range(len(rowLabels)):
            #print(str(rowLabels[subRow]))
            # 2 Empty column
            dynCol = colAuto()            
            next(dynCol)
               
            worksheet.write(row, next(dynCol) ,str(rowLabels[subRow]), basic)
            for country in EU28Countries:                
                if country in data:
                    mydata=data[country]
                    #We have three elements, one per row, and per element two positions: [value, style]
                    rowValues=[[str(mydata[0]), basic],[str(mydata[2]),eval(mydata[4])],[str(mydata[5]),eval(mydata[7])]]
                    #print(rowValues)                    
                    worksheet.write(row,next(dynCol) ,rowValues[subRow][0], rowValues[subRow][1])  
                else:
                    worksheet.write(row,next(dynCol),"n.a.", basic)
            row+=1
    
dynCol = colAuto()
worksheet.write(row, next(dynCol),     "", basic) 
worksheet.write(row, next(dynCol),     "", st_country) 
for country in EU28Countries:
    worksheet.write(row, next(dynCol), country, st_country)  



#Summary
summary = workbook.add_worksheet()
summary.set_column(0, 0, 80)
summary.set_column(1,7, 15)

dynCol = colAuto()    
summary.write(0,next(dynCol) ,"indicator" , st_country)

summary.write(0,next(dynCol) ,"Short Positive_Flag" , st_country)
summary.write(0,next(dynCol) ,"Short Negative_Flag" , st_country)
summary.write(0,next(dynCol) ,"Long Positive_Flag" , st_country)
summary.write(0,next(dynCol) ,"Long Negative_Flag" , st_country)


row = 1
#Iterator for columns, to reset per line
indic=0

while indic < len(dashboardData): 
    indic+=1
    if indic in dashboardData:
        dynCol = colAuto()
        ID, label, refYear, change, data=dashboardData[indic]   
        summary.write(row,next(dynCol) ,label, basic)
        short_positive_flags=0
        short_negative_flags=0
        long_positive_flags=0
        long_negative_flags=0
        #Count flags
        for key, value in data.items():
            #Exclude aggregates from the count
            if len(key)==2:
                if value[4]=='positive':
                    short_positive_flags+=1
                if value[4]=='negative':
                    short_negative_flags+=1
                if value[7]=='positive':
                    long_positive_flags+=1
                if value[7]=='negative':
                    long_negative_flags+=1
        summary.write(row,next(dynCol) ,short_positive_flags, basic)
        summary.write(row,next(dynCol) ,(-1)*short_negative_flags, basic)
        summary.write(row,next(dynCol) ,long_positive_flags, basic)
        summary.write(row,next(dynCol) ,(-1)*long_negative_flags, basic)
        
    row += 1



#reporting
reporting = workbook.add_worksheet()
dynCol = colAuto()    
reporting.write(0,next(dynCol) ,"indicator" , st_country)
reporting.write(0,next(dynCol) ,"Country" , st_country)
reporting.write(0,next(dynCol) ,"ref year" , st_country)
reporting.write(0,next(dynCol) ,"Value" , st_country)
reporting.write(0,next(dynCol) ,"flag" , st_country)
reporting.write(0,next(dynCol) ,"short_chg" , st_country)
reporting.write(0,next(dynCol) ,"short_flag" , st_country)
reporting.write(0,next(dynCol) ,"long_chg" , st_country)
reporting.write(0,next(dynCol) ,"long_flag" , st_country)

row = 1
#Iterator for columns, to reset per line
indic=0
reporting.set_column(0, 0, 75)
# Iterate over the dictionary of data using the order number as parameter
while indic < len(dashboardData): 
    indic+=1
    if indic in dashboardData:
        ID, label, refYear, change, data=dashboardData[indic]   
        for country in EU28Countries:
            if country in data:
                mydata=data[country]     
                if str(mydata[1])!='' or  str(mydata[3])!='' or  str(mydata[6])!='':
                    dynCol = colAuto()            
                    reporting.write(row,next(dynCol) ,label, basic)
                    reporting.write(row,next(dynCol) ,country, basic)
                    reporting.write(row,next(dynCol) ,refYear, basic)
                    for number in range(8):
                        if number not in [4,7]:
                            reporting.write(row,next(dynCol) ,str(mydata[number]), basic)
                    row += 1




workbook.close()
