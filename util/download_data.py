import urllib.request
import gzip
import glob, os
import os.path
import time
from datetime import date
import shutil, errno

from util.datasetsInfo import *


def download_files_eurostat(file):
    try:
        print("downloading:"+file+"........")
        #Download files from eurostat        
        u = urllib.request.urlopen(baseUrl+file+'.tsv.gz')
        localFile = open(path+file+'.tsv.gz', 'wb')
        localFile.write(u.read())
        localFile.close()        
        #uncompress the file
        f=gzip.open(path+file+'.tsv.gz')
        finalFile = open(path+file+'.tsv', 'wb')
        finalFile.write(f.read())
        finalFile.close()
        f.close()        
        #Transform tsv in csv
        f1 = open(path+file+'.tsv', 'r')
        f2 = open(csv_path+file+'.csv', 'w')
        for line in f1:            
            f2.write(line.replace('\t', ','))            
        f1.close()
        f2.close()
        return ""
    except Exception as e:
        print("================")
        print("ERRROR "+file+":"+str(e))
        return str(e)
 





def download_and_stack(listFiles):  
    cleanFolderZip(path)
    message=""
    for file in listFiles:
        #if 1==1:
        if os.path.isfile(stacked_path+file+'.csv')==False or (time.time()-os.path.getmtime(csv_path+file+'.csv'))>(daysToNotDownload*86400):            
            try:
                message+=download_files_eurostat(file)            
                stack_any_file(file)
                
                #Dataset Information
                dataInfo=getInfo(file)
                print(dataInfo)
                
            except Exception as e:
                print("================")
                print("ERROR in download_and_stack:"+str(e))
                message+="ERROR in download_and_stack:"+str(e)
                print("AY")
                print(message)
    
    return message      
            
            
def cleanFolderZip(folderPath):
    #Clean folder
    os.chdir(folderPath)
    filelist = glob.glob("*.gz")
    for f in filelist:        
        os.remove(f)

def syncFolders(src, dst):    
    src=src[:-1]
    dst=dst[:-1]
    if syncActive:
        if 'stacked' in src:
            #print("NO sync for stacked")
            #return
            os.chdir(src)
            filelist = glob.glob("*.csv")
            #print(filelist)         
            two_days = (time.time()-60*60*1)
            #print(two_days)
            for f in filelist:                 
                #print(f)
#                print(os.path.getmtime(src+"\\"+f))
#                print(two_days)
#                print("---")
                if os.path.getmtime(src+"\\"+f) > two_days:
                    #print(f)
                    subfolder=""        
                    #############Only for production
                    if "_" in f:
                        subfolder=f[0:f.index("_")]
                    
                    a= 'xcopy "' +src+'\\'+f+'" "'+ dst+'\\'+subfolder+'" /s /y /d'
                    print(a)       
                    os.system (a)
            
        else:       
            #xcopy /s:to copy folders and subfolders  /y:Supress promting /d:copy only new/updated files
            a= "xcopy " +src+' "'+ dst+'" /s /y /d'
            print(a)       
            os.system (a)
    else:
        print("********   Sync not active")

def stack_any_file(file):
    try:               
        headers=[]
        a=pd.read_csv(csv_path+file+'.csv')        
        for i in range(len(a.columns)):
            a[a.columns[i]]=a[a.columns[i]].astype(str)  
            a[a.columns[i]]=a[a.columns[i]].str.strip()
            #Clean spaces in years
            headers.append(str(a.columns[i]).strip())
        a.columns=headers
        #Look for the last header before columns to be stacked                
        lastHeader=''       
        for header in headers:                        
            if '\\' in header:
                lastHeader=header
                break
            
        geoCol = headers.index(lastHeader)      
        
        b=a.set_index(headers[:(geoCol+1)])  
        b=b.stack()
        b=b.reset_index() 
        
        newHeaders = headers[:(geoCol)]
        newHeaders.append(lastHeader.split('\\')[0])
        newHeaders.append(lastHeader.split('\\')[1])
        newHeaders.append('values')
        for i in range(len(newHeaders)):
              if newHeaders[i]=='time':
                  newHeaders[i]='year'
                
        b.columns= newHeaders  
         #To remove spaces in dimensions, (needed for ad-hoc module in health hlth_ehis_hc1,hlth_ehis_hc4,earn_ses10_15,...
               
        b=b.set_index(newHeaders[:(geoCol+2)]) 
                
        b['file']=file         
        
        #Split values in numeric value and flag
        #FASTEST OPTION        
        b['value_n']=b['values'].apply(lambda x:str(x).split()[0]) 
        b['flag']=b['values'].apply(lambda x:str(x).split()[1] if len(x.split())>1 else np.nan)
        
        b=b.replace(':', '')        
                
        #Only for production
        #Not to remove blanks in local 
        #e=e[(e.value_n!="") & (e.flag!="") ]
        
        subfolder=""               
        #############Only for production
        #if "_" in file:
         #   subfolder=file[0:file.index("_")]
#        subfolder=file[0:file.index("_")]
#        if not os.path.exists(stacked_path+subfolder):
#            os.makedirs(stacked_path+subfolder)       
        #######################
        b.to_csv(stacked_path+subfolder+file+'.csv')
        
        return b
    except Exception as excp:
        print("================")
        print("ERROR "+file+":"+str(excp))

#syncFolders(stacked_path,stacked_path_p)
