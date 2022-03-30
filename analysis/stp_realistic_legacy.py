# Aggregate the revisited OD records into realistic STP. Need to first run 1) Dijkstra Solver and 2) RevisitSolver 
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
    startDate = date(2018, 3, 8)
    endDate = date(2020, 7, 1)
    daterange = (transfer_tools.daterange(startDate, endDate))
    numberOfTimeSamples = 1

    budgetList = [i for i in range(0, 121, 5)]

    for singleDate in (daterange):
        weekday = singleDate.weekday()
        if weekday != 2:
            continue
        todayDate = singleDate.strftime("%Y%m%d")
        GTFSTimestamp = transfer_tools.find_gtfs_time_stamp(singleDate)
        todaySeconds = atime.mktime(singleDate.timetuple())
        gtfsSeconds = str(transfer_tools.find_gtfs_time_stamp(singleDate))
        db_stops = client.cota_gtfs[gtfsSeconds + "_stops"]

        for i in [8, 12, 18]:
            todayTimestamp = (todaySeconds + i * 60*60/numberOfTimeSamples)
            col_access = client.cota_access_rev[todayDate + "_" + str(int(todayTimestamp))]
            print(todayDate + "_" + str(int(todayTimestamp)))
            rl_access = (col_access.find({}))
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
                        "errorRV": 0,
                        "errorSC": 0
                    }
                    for budget in budgetList:
                        timeDic[originStop]["countRV_" + str(budget)] = 0
                        timeDic[originStop]["countSC_" + str(budget)] = 0

                timeRT = record["timeRV"]
                timeSC = record["timeSC"]
                if timeRT == None:
                    timeDic[originStop]["countRV_" + str(budget)]
                else:
                    for budget in budgetList:
                        if timeRT < budget * 60: # If travel time between the stops are smaller than the budget, then it's accessible 
                            timeDic[originStop]["countRV_" + str(budget)] += 1

                if timeSC == None:
                    timeDic[originStop]["countSC_" + str(budget)]
                else:
                    for budget in budgetList:
                        if timeSC < budget * 60:
                            timeDic[originStop]["countSC_" + str(budget)] += 1
                # print(len(timeDic.items()))
            print(timeDic)
            insertList = []
            for index, record in timeDic.items():
                # print(record)
                insertList.append(record)

            # print((insertList), len(timeDic.items()))
            
            client.cota_access_agg["stpRV_" + todayDate + "_" + str(int(todayTimestamp))].drop()
            client.cota_access_agg["stpRV_" + todayDate + "_" + str(int(todayTimestamp))].insert_many(insertList)
            print("---------------", todayDate, i, "---------------")
            break
        # break
            # print(timeDic)
            

