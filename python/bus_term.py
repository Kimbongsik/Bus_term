from bs4 import BeautifulSoup
import xmltodict
import urllib
import requests
import re 
import threading
import datetime

station_servicekey = ""
bus_numberlist =["1112","7000","5100","m5107"]

bus_routeid_list =[]

for i in bus_numberlist:
    route_station_url = "http://openapi.gbis.go.kr/ws/rest/busrouteservice"
    busarrival_station_url = "http://openapi.gbis.go.kr/ws/rest/busarrivalservice"
    serviceKey_string = "?serviceKey="+station_servicekey+"&"

    keyword_parameter = "keyword="+i

    html = requests.get(route_station_url+serviceKey_string+keyword_parameter)

    def response_html():
        if html.status_code == 200:
            html_text = html.text 
            return html_text   
        else:
            print("Error")

    xml_data = response_html()
    soup = BeautifulSoup(xml_data,'lxml')

    find_routeid = soup.find_all("routeid") #1112번의 routeid
    routeid_tag = find_routeid[0].get_text()
    bus_routeid_list.append(routeid_tag)

bus_dict = {}


for i in range(len(bus_numberlist)):
    bus_dict.setdefault(bus_numberlist[i],bus_routeid_list[i])

station_parameter = "routeId="+bus_routeid_list[0]

stationname_url = route_station_url+"/station"+serviceKey_string+station_parameter
html = requests.get(stationname_url)
xml_data = response_html()
soup = BeautifulSoup(xml_data,'lxml')

stationid_list = soup.find_all("stationid")

stationname_list = soup.find_all("stationname")

def callback():
    timer = threading.Timer(10,callback)
    noRes = "4"

    id_list = [] #생명과학대.산업대학 정류장 stationid

    count = 0
    for i in stationname_list:
        i = str(i)
        if i == "<stationname>생명과학대.산업대학</stationname>":
            id_list.append(stationid_list[count])
        count += 1
    
    wanted_stationid = id_list[0].get_text()
    stationid_parameter = "stationId="+wanted_stationid
    stationid_url = busarrival_station_url+"/station"+serviceKey_string+stationid_parameter

    html = requests.get(stationid_url)
    if html.status_code == 200:
            html_text = html.text
    xml_data = html_text 
    soup = BeautifulSoup(xml_data,'lxml')
    
    isfound = soup.find_all("resultcode")
    isfound = isfound[0].get_text()
    if isfound == noRes:
        print("NO BUS NOW")
    else:
        isfound = soup.find_all("routeid")
        print(isfound)
        for i in isfound:
            for name, ids in bus_dict.items():
                if i.get_text() == ids:
                    print("현재 오는 버스는 " + name + " 입니다")
                    print("현재 시간은 " + str(datetime.datetime.now()))
                    f = open(name + ".txt", "a")
                    f.writelines(name + " " + str(datetime.datetime.now()) + "\n")
                    f.close()
    timer.start()

callback()
