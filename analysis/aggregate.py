
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
    daterange = (transfer_tools.daterange(startDate, endDate))
    numberOfTimeSamples = 1

    db_weight = client.streetlight
    col_weight = db_weight["od_stop_2019"]
    rl_weight = (col_weight.find({}))

    weight_dic = {}
    print("weight matrix started.")
    for each_weight in tqdm(rl_weight):
        start_id = each_weight["origin_stop"]
        destination_id = each_weight["destination_stop"]
        try:
            weight_dic[start_id]
        except:
            weight_dic[start_id] = {}

        try:
            weight_dic[start_id][destination_id]
        except:
            weight_dic[start_id][destination_id] = each_weight["normalized_traffic"]

    print("weight matrix finished.")

    for singleDate in (daterange):
        todayDate = singleDate.strftime("%Y%m%d")
        GTFSTimestamp = transfer_tools.find_gtfs_time_stamp(singleDate)
        todaySeconds = atime.mktime(singleDate.timetuple())
        gtfsSeconds = str(transfer_tools.find_gtfs_time_stamp(singleDate))
        db_stops = client.cota_gtfs[gtfsSeconds + "_stops"]

        for i in [8, 12, 18]:
            todayTimestamp = (todaySeconds + i * 60*60/numberOfTimeSamples)
            col_access = client.cota_access_rel[todayDate + "_" + str(int(todayTimestamp))]
            print(todayDate + "_" + str(int(todayTimestamp)))
            rl_access = col_access.find({})
            timeDic = {}
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
                        "timeRT": 0,
                        "timeSC": 0,
                        "weight": 0,
                        "count" : 0,
                        "accessible_count": 0
                    }

                try:
                    timeDic[destinationStop]
                except:
                    rl_stop = db_stops.find_one({"stop_id": destinationStop})
                    timeDic[destinationStop] = {
                        "stopID": destinationStop,
                        "lat": rl_stop["stop_lat"],
                        "lon": rl_stop["stop_lon"],
                        "timeRT": 0,
                        "timeSC": 0,
                        "weight": 0,
                        "count" : 0,
                        "accessible_count": 0
                    }

                try:
                    weight = weight_dic[originStop][destinationStop]
                except:
                    weight = 0
                timeDic[originStop]["timeRT"] += record["timeRT"] * weight
                timeDic[originStop]["timeSC"] += record["timeSC"] * weight
                timeDic[originStop]["weight"] += weight
                timeDic[originStop]["count"] += 1
                timeDic[destinationStop]["accessible_count"] += 1 # The number of stops that can access this stop (origin stop)
            
            insertList = []
            for index, record in timeDic.items():
                if record["weight"] != 0:
                    record["timeRT"] /= record["weight"]
                    record["timeSC"] /= record["weight"]
                insertList.append(record)
            
            client.cota_access_agg["rel_" + todayDate + "_" + str(int(todayTimestamp))].drop()
            client.cota_access_agg["rel_" + todayDate + "_" + str(int(todayTimestamp))].insert_many(insertList)
            print("---------------", todayDate, i, "---------------")
            # print(timeDic)
            

