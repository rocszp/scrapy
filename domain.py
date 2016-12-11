'''
Created on 2016年5月9日

@author: heguofeng
'''

import requests
import _thread
import threading
import csv
from datetime import datetime, date, time

import re
from flask.testsuite import catch_stderr

import ssl
import socket

class domainsprider():
    
    def __init__(self):
        self.list=[]
        self.csvfile=open('domain.csv', 'w', newline='')
        fieldnames = ['title', 'domainname',"email","isHttps","notAfter"]
        self.writer = csv.DictWriter(self.csvfile, fieldnames=fieldnames)
        self.writer.writeheader()
        pass
    
    def spride(self,url):
        self.list=[]
        r=requests.get(url)
        html=r.text.encode(r.encoding).decode("utf-8")
        DomainTitle=re.findall(r'(?<=/Html/site_)[\S]*\stitle\=[\S]*(?=\starget)',html)
        
        print(DomainTitle)
        
        for i in range(0,len(DomainTitle)):
            item=DomainTitle[i]
            r=item.replace('.html" title='," ")
            r=r.replace("'","")
            l=r.split(" ")
            dict={"domainname":l[0],
                  "title":l[1]}
    
            self.list.append(dict)
            #try:
            
            t=(i,)
           
            
            _thread.start_new_thread(self.getnotAfter,t)
            #except:
            #   print( "Error: unable to start thread")
            #self.list[i].append(self.ishttps(self.list[i][0]))
            #print(r)
        running=True   
        while running:
            running=False
            for i in range(0,len(self.list)):
                if((self.list[i]).get("isHttps")==None):
                    running=True
                    
        print(self.list)   
        
    
    def ishttps(self,i):
        url="https://www."+self.list[i]["domainname"]
        try:
            r=requests.get(url)
            if r.status_code==200:
                (self.list[i])["isHttps"]=True
                print(self.list[i])
        except Exception:
            (self.list[i])["isHttps"]=False
            return
        finally:
            if (self.list[i])["isHttps"]:
                self.getnotAfter(i)
        #(self.list[i])["isHttps"]=False
        return 
        
    def getnotAfter(self,i):    
        hostname="www."+self.list[i]["domainname"]
        try:
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
            s.connect((hostname, 443))
            (self.list[i])["isHttps"]=True
            cert = s.getpeercert() 
            dt = datetime.strptime(cert['notAfter'], "%b  %d %H:%M:%S %Y GMT")
            (self.list[i])['notAfter']=dt.strftime("%Y/%m/%d")
        except ssl.CertificateError:
            (self.list[i])["isHttps"]=True
        except: 
            (self.list[i])["isHttps"]=False
        
        self.getContact(i)
        #print(self.list[i])    
        return
        
    def getContact(self,i):
        url="http://whois.chinaz.com/"+(self.list[i])["domainname"]
        try:
            r=requests.get(url)
            #html=r.text.encode(r.encoding).decode("utf-8")
            email=re.findall(r'(?<=\<span\>)[\S]*@[\S]*(?=\</span\>)',r.text)
            (self.list[i])["email"]=email[0]
        except:
            pass
        
        return
        
    def savelist(self):   
        try:
            for i in range(0,len(self.list)):
                self.writer.writerow(self.list[i])
        except:
            print("Error:!!!")
            print(self.list[i])
        return
    
    def close(self):
        self.csvfile.close()

    def getPages(self,url):
        r=requests.get(url)
        html=r.text.encode(r.encoding).decode("utf-8")
        #<div class="ListPageWrap">
        pages=re.findall(r'(?<=\<div\sclass=\"ListPageWrap\"\>).*(?=\</div\>)',html)
        pageno=re.findall(r'\d+',pages[0])
        max=0
        for item in pageno:
            if int(item)>max:
                max=int(item)
        print(max)
        return max        
    
    def changetime(self):
        csvfile=open('domainr.csv', 'r', newline='')
        reader = csv.DictReader(csvfile)
        csvfilet=open('domaint.csv', 'w', newline='')
        fieldnames = ['title', 'domainname',"email","isHttps","notAfter"]
        writer = csv.DictWriter(csvfilet, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row["notAfter"]!="" :
                dt = datetime.strptime(row["notAfter"], "%b  %d %H:%M:%S %Y GMT")
                row["notAfter"]=dt.strftime("%Y/%m/%d")
            print(row)
            writer.writerow(row)
                
        csvfilet.close()
        csvfile.close()
      

                
    

if __name__ == '__main__':
    
    
    
    ds=domainsprider()
    
    
    #url="http://top.chinaz.com/diqu/index_ShangHai.html"
    url="http://top.chinaz.com/hangye/index_shopping.html"
    pages=ds.getPages(url)

    
    ds.spride(url)
    ds.savelist()
    for i in range(2,pages+1):
        print(i)
        #url="http://top.chinaz.com/diqu/index_ShangHai_"+str(i)+".html"
        url="http://top.chinaz.com/hangye/index_shopping_"+str(i)+".html"
        ds.spride(url)
        ds.savelist()
    
    
    ds.close()
    
    
    #ds.savelist()
    