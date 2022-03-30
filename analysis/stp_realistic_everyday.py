# Aggregate the original realistic OD into realistic STP FOR EACH DAY. Need to first run 1) Dijkstra Solver 2) Revisit Solver

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
    daterange_continuous = list(transfer_tools.daterange(startDate, endDate))
    daterange = []
    for i in daterange_continuous:
        if i.weekday() == 2:
            daterange.append(i)

    numberOfTimeSamples = 1

    budgetList = [i for i in range(0, 121, 5)]
    # for aDateIndex in range(len(daterange)):
    #     aDate = daterange[aDateIndex]
    #     bDate = daterange[aDateIndex + 1]
    #     aggregationObject[aDate] = {}
    # aggregationCountList = [0] * (len(daterange) -1)
    
    for i in [8]:
        insertList = []
        fullObject = {}
        for singleDate in (daterange):
            weekday = singleDate.weekday()
            if weekday != 2:
                continue
            todayDate = singleDate.strftime("%Y%m%d")
            print("---------------", todayDate, "---------------")
            GTFSTimestamp = transfer_tools.find_gtfs_time_stamp(singleDate)
            todaySeconds = atime.mktime(singleDate.timetuple())
            gtfsSeconds = str(transfer_tools.find_gtfs_time_stamp(singleDate))
            db_stops = client.cota_gtfs[gtfsSeconds + "_stops"]

            todayTimestamp = (todaySeconds + i * 60*60/numberOfTimeSamples)
            col_access = client.cota_access_rev[todayDate + "_" + str(int(todayTimestamp))]
            print(todayDate + "_" + str(int(todayTimestamp)))
            rl_access = col_access.find({})
            
            timeDic = {}
            for record in tqdm(rl_access):
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
                        "neverCount": 0 # Number of stops that can never be visited, i.e., missed the last bus.
                    }
                    for budget in budgetList:
                        timeDic[originStop]["PPA_RV_" + str(budget)] = 0
                        timeDic[originStop]["PPA_SC_" + str(budget)] = 0
                        timeDic[originStop]["PPA_RT_" + str(budget)] = 0

                timeDic[originStop]["count"] += 1

                timeRV = record["timeRV"]
                timeSC = record["timeSC"]
                timeRT = record["timeRT"]
                
                if timeRV == None:
                    timeRV = sys.maxsize # If there is no found record for timeRV, then it won't be accessed anywhere, e.g., miss the last bus
                    timeDic[originStop]["neverCount"] += 1
                for budget in budgetList:
                    if timeRV < budget * 60: # If travel time between the stops are smaller than the budget, then it's accessible
                        timeDic[originStop]["PPA_RV_" + str(budget)] += 1
                    if timeSC < budget * 60:
                        timeDic[originStop]["PPA_SC_" + str(budget)] += 1
                    if timeRT < budget * 60:
                        timeDic[originStop]["PPA_RT_" + str(budget)] += 1

            insertList = []
            for stop_id, item in timeDic.items(): # Aggregating
                insertList.append(item)
                
            if insertList != []:
                client.cota_access_daily_agg["REA_" + todayDate + "_" + str(i)].drop()
                client.cota_access_daily_agg["REA_" + todayDate+ "_" + str(i)].insert_many(insertList)
                

