import re
from datetime import datetime, timedelta
import os
import json

def extract_transport(directionData):
    '''extract result data from json: drive mode == tansit & not walking'''
    # step 1 : get the data - actual arrival_time, departure_time, duration
    arrival_time = covert_time24(directionData['routes'][0]['legs'][0]['arrival_time']['text'])
    departure_time = covert_time24(directionData['routes'][0]['legs'][0]['departure_time']['text'])
    distance = directionData['routes'][0]['legs'][0]['distance']['text']
    duration = directionData['routes'][0]['legs'][0]['duration']['text']

    # step 2: get the data - how many changes
    changes = len(directionData['routes'][0]['legs'][0]['steps'])

    # step 3: get the detailed changes
    route = []
    for x in directionData['routes'][0]['legs'][0]['steps']:
        route.append(x['duration']['text']+"-"+x['html_instructions'])

    detailedroute = "\n".join(str(x) for x in route)
    comments = " "
    return arrival_time, departure_time, distance, duration, changes, detailedroute, comments

def covert_time24(stime):
    '''format am/pm time to 24 hour'''
    Rstring = stime.rstrip().lower()[-2:]
    if Rstring == "am" or Rstring == "pm":
        in_time = datetime.strptime(stime.strip(), "%I:%M%p")
        out_time = datetime.strftime(in_time, "%H:%M")
    else:
        out_time = stime
    return out_time


def extract_driveWalk(directionData, definetime):
    '''extract result data from json: drive mode == driving | drive mode == tansit & Walking'''
    # step 1 : get the data - actual duration
    distance = directionData['routes'][0]['legs'][0]['distance']['text']
    duration = directionData['routes'][0]['legs'][0]['duration']['text']

    # step 2: caculate the arrivel time and depature time according to the arrival time
    arrival_time, departure_time = convert_duration(duration, definetime)

    # step 3: get the data - how many changes
    changes = 0

    # step 4: get the detailed changes
    detailedroute = directionData['routes'][0]['summary']

    # step5: if walking to place, then extract warning data
    if len("".join(directionData['routes'][0]['warnings'])):
        comments = "".join(directionData['routes'][0]['warnings']).strip().split()[0]
    else:
        comments = " "

    return arrival_time, departure_time, distance, duration, changes, detailedroute, comments
    
def convert_duration(duration, definetime):
    '''cacaulate duration time when result data did not have arrive time and departure time: 
    duration =="1 hour 38 minutes" ||  "38 minutes"'''
    #  step1: covert duration to datetime timedelta
    str1 = [int(x) for x in re.findall(r'\d+', duration)]
    if len(str1) == 2:
        duration = timedelta(hours=str1[0])+ timedelta(minutes=str1[1])
    elif len(str1) == 1:
        duration = timedelta(minutes=str1[0])
    else:
        pass
    
    # step2: caculate the arrive time and departure time. Given time is setting as arrive time. 
    searchtime = searchtime_coding(definetime)
    stime = datetime.fromtimestamp(searchtime*1000/1e3) 
    dtime = stime - duration
    arrival_time = f"{stime.hour}:{stime.minute}"
    departure_time = f"{dtime.hour}:{dtime.minute}"

    return arrival_time, departure_time

def searchtime_coding(definetime):
    '''process the searchtim: using the original data to meet the url's requirement'''
    try:      
        searchtime = int(definetime.timestamp())  # time data is normal
    except:
        if definetime==definetime and type(definetime)==str and len(definetime.strip()): # time data seems normal, but actually has blank() space before or after   
            searchtime = int(datetime.strptime(definetime.strip(), '%d/%m/%Y %H:%M:%S').timestamp())
        
        searchtime = int(datetime.now().timestamp()) # 1. time data just blank() space 2. time data nan 

    return searchtime

from os import listdir
from os.path import isfile, join


if __name__ == "__main__":
    # get all the json files in current working folder. 
    for path, dir_list, file_list in os.walk(fr"{os.path.abspath(os.getcwd())}\testdata"): 
        for filename in file_list:
            filepath = os.path.join(path,filename)
            
            with open(filepath) as json_data: # process the json file
                directionData = json.load(json_data)
                if len(directionData ['routes']):
                    if 'arrival_time' in list(directionData['routes'][0]['legs'][0].keys()):
                        result = extract_transport(directionData)
                    elif directionData['routes'][0]['legs']:
                        result = extract_driveWalk(directionData, '28/02/2022 17:40:00')
                else:
                    result = ["", "", "", "", "", "", 'errors']
                json_data.close()
                print(result)