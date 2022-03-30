# Aggregate the original retrospective OD into retrospective STP. Need to first run 1) Dijkstra Solver
import sys
import os
import time
import math
import multiprocessing
import copy
from pymongo import MongoClient
from datetime import timedelta, date, datetime
from math import sin, cos, sqrt, atan2, pi, acos
from tqdm import tqdm
import time as atime
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
import transfer_tools
client = MongoClient('mongodb://localhost:27017/')

if __name__ == "__main__":
    startDate = date(2018, 2, 1)
    endDate = date(2020, 7, 1)
    daterange = list(transfer_tools.daterange(startDate, endDate))
    numberOfTimeSamples = 1

    budgetList = [i for i in range(0, 121, 5)]
    breakpointList = [date(2018, 1, 1), date(2018, 5, 1), date(2018, 9, 1), date(2019, 1, 1), date(2019, 5, 1), date(2019, 9, 1), date(2020, 1, 1), date(2020, 5, 1), date(2020, 9, 1) ]
    aggregationObject = {}
    for aDateIndex in range(len(breakpointList) - 1):
        aDate = breakpointList[aDateIndex]
        bDate = breakpointList[aDateIndex + 1]
        aggregationObject[aDate] = {}
    aggregationCountList = [0] * (len(breakpointList) -1)
    
    for i in [8, 12, 18]:
        insertList = []
        fullObject = {}
        for singleDate in tqdm(daterange):
            weekday = singleDate.weekday()
            if weekday != 2:
                continue
            todayDate = singleDate.strftime("%Y%m%d")
            GTFSTimestamp = transfer_tools.find_gtfs_time_stamp(singleDate)
            todaySeconds = atime.mktime(singleDate.timetuple())
            gtfsSeconds = str(transfer_tools.find_gtfs_time_stamp(singleDate))
            db_stops = client.cota_gtfs[gtfsSeconds + "_stops"]

            todayTimestamp = (todaySeconds + i * 60*60/numberOfTimeSamples)
            col_access = client.cota_access_rel["rel_" + todayDate + "_" + str(int(todayTimestamp))]
            print(todayDate + "_" + str(int(todayTimestamp)))
            rl_access = col_access.find({})
            
            aggregationDate = None
            for aDateIndex in range(len(breakpointList) - 1):
                aDate = breakpointList[aDateIndex]
                bDate = breakpointList[aDateIndex + 1]
                if singleDate >= aDate and singleDate < bDate:
                    aggregationDate = aDate
            
            if aggregationDate == None:
                continue

            timeDic = aggregationObject[aggregationDate]
            for _, item in timeDic.items():
                item["aggTag"] = False

            for record in rl_access:
                if record["visitTagSC"] == False or record["receivingStopID"] == None: # NaN for scheduled.
                    continue
                originStop = record["startStopID"]
                destinationStop = record["receivingStopID"]
                try:
                    timeDic[originStop]
                except:
                    rl_stop = db_stops.find_one({"stop_id": originStop})
                    timeDic[originStop] = {
                        "stopID": originStop,
                        "lat": rl_stop["stop_lat"],
                        "lon": rl_stop["stop_lon"],
                        "count": 0,
                        "aggTag": False
                    }
                    for budget in budgetList:
                        timeDic[originStop]["PPA_RT_" + str(budget)] = 0
                        timeDic[originStop]["PPA_SC_" + str(budget)] = 0

                
                if timeDic[originStop]["aggTag"] == False:
                    timeDic[originStop]["count"] += 1
                    timeDic[originStop]["aggTag"] = True

                timeRT = record["timeRT"]
                timeSC = record["timeSC"]
                for budget in budgetList:
                    if timeRT < budget * 60: # If travel time between the stops are smaller than the budget, then it's accessible
                        timeDic[originStop]["PPA_RT_" + str(budget)] += 1
                    if timeSC < budget * 60:
                        timeDic[originStop]["PPA_SC_" + str(budget)] += 1

        for aDate, item in aggregationObject.items(): # Aggregating
            aggDate = aDate.strftime("%Y%m%d")
            insertList = []
            for stopID, stopItem in item.items(): # For all aggregated stops
                for budget in budgetList: # Divide by the day count to generate the average PPA
                    if stopItem["count"] == 0:
                        continue
                    stopItem["PPA_RT_" + str(budget)] /= stopItem["count"]
                    stopItem["PPA_SC_" + str(budget)] /= stopItem["count"]
                insertList.append(stopItem)
            
            if insertList != []:
                client.cota_access_agg["RET_" + aggDate + "_" + str(i)].drop()
                client.cota_access_agg["RET_" + aggDate+ "_" + str(i)].insert_many(insertList)
            print("---------------", todayDate, date, "---------------")
            

