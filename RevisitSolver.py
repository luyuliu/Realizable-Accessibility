# Revisit the posteriori OD records and find the actual priori performance.
# The reason to revisit the posteriori OD records: Priori route will be always consistent with schedule-based route.
# The results will look similar to DijkstraSolver. Only difference is RV, which represent the priori version of the real-time.

# The code is not parallelized because the memory cost is too large and it is running pretty fast compared to DijkstraSolver.

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
from collections import OrderedDict
import time as atime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import transfer_tools
client = MongoClient('mongodb://localhost:27017/')

db_GTFS = client.cota_gtfs
db_real_time = client.cota_real_time


def revisit(lastMiddleStopID, thisMiddleStopID, originStopID, eachTimestamp, accessDic, arcsDicRT):
    # Revisited Stop's time
    a = 1
    try:
        lastTimeRVa = accessDic[originStopID][lastMiddleStopID]
        lastTimeRV = lastTimeRVa["timeRV"]
    except:
        lastTimeRV = None
    if lastTimeRV == None: # There is no path to the last stop, so the rest of the path will be nonexisting.
        accessDic[originStopID][thisMiddleStopID]["timeRV"] = None
        accessDic[originStopID][thisMiddleStopID]["waitTimeRV"] = None
        accessDic[originStopID][thisMiddleStopID]["busTimeRV"] = None
        accessDic[originStopID][thisMiddleStopID]["lastTripIDRV"] = None
        return None

    lastTime = lastTimeRV + eachTimestamp
    # Should be always consistent with RV
    thisTripTypeSC = accessDic[originStopID][thisMiddleStopID]["lastTripTypeSC"]
    # lastTripTypeSC = accessDic[originStopID][lastMiddleStopID]["lastTripTypeSC"]

    # Walk time stays the same
    accessDic[originStopID][thisMiddleStopID]["walkTimeRV"] = accessDic[originStopID][thisMiddleStopID]["walkTimeSC"]

    if thisTripTypeSC == "walk":
        accessDic[originStopID][thisMiddleStopID]["timeRV"] = accessDic[originStopID][lastMiddleStopID]["timeRV"] + \
            accessDic[originStopID][thisMiddleStopID]["walkTimeSC"] - \
            accessDic[originStopID][lastMiddleStopID]["walkTimeSC"]
        accessDic[originStopID][thisMiddleStopID]["waitTimeRV"] = accessDic[originStopID][lastMiddleStopID]["waitTimeRV"]
        accessDic[originStopID][thisMiddleStopID]["busTimeRV"] = accessDic[originStopID][lastMiddleStopID]["busTimeRV"]

    else:  # "bus"
        try:
            arcsList = arcsDicRT[lastMiddleStopID][thisMiddleStopID]
        except:
            accessDic[originStopID][thisMiddleStopID]["timeRV"] = None
            accessDic[originStopID][thisMiddleStopID]["waitTimeRV"] = None
            accessDic[originStopID][thisMiddleStopID]["busTimeRV"] = None
            accessDic[originStopID][thisMiddleStopID]["lastTripIDRV"] = None
            return None
        else:
            pass

        thisTimeRV = None
        thisWaitTimeRV = None
        thisBusTimeRV = None
        thisLastTripIDRV = None
        for timeGen, eachArc in arcsList.items():
            if timeGen >= lastTime:  # arrival time is earlier than the generating time in the thisMiddleStopID
                thisTimeRV = eachArc["time_rec"] - lastTime
                thisWaitTimeRV = timeGen - lastTime
                thisBusTimeRV = eachArc["bus_time"]
                thisLastTripIDRV = eachArc["trip_id"]
                break
        if thisTimeRV != None:
            lastTimeRV = accessDic[originStopID][lastMiddleStopID]["timeRV"]
            lastWaitTimeRV = accessDic[originStopID][lastMiddleStopID]["waitTimeRV"] 
            lastBusTimeRV = accessDic[originStopID][lastMiddleStopID]["busTimeRV"]
            accessDic[originStopID][thisMiddleStopID]["timeRV"] = lastTimeRV + thisTimeRV
            accessDic[originStopID][thisMiddleStopID]["waitTimeRV"] = lastWaitTimeRV + thisWaitTimeRV
            accessDic[originStopID][thisMiddleStopID]["busTimeRV"] = lastBusTimeRV + thisBusTimeRV
            accessDic[originStopID][thisMiddleStopID]["lastTripIDRV"] = thisLastTripIDRV
        else:
            accessDic[originStopID][thisMiddleStopID]["timeRV"] = None
            accessDic[originStopID][thisMiddleStopID]["waitTimeRV"] = None
            accessDic[originStopID][thisMiddleStopID]["busTimeRV"] = None
            accessDic[originStopID][thisMiddleStopID]["walkTimeRV"] = None
            accessDic[originStopID][thisMiddleStopID]["lastTripIDRV"] = None


    # if accessDic[originStopID][thisMiddleStopID]["timeRV"] > 2000:
    #     print(thisTripTypeSC, originStopID, accessDic[originStopID][thisMiddleStopID]["timeRV"], accessDic[originStopID][thisMiddleStopID]["timeSC"])
    #     for timeGen, eachArc in arcsList.items():
    #         print(lastTime, timeGen, eachArc["time_gen_S"])
    
    # if lastMiddleStopID == "FREOAKE" and thisMiddleStopID == "FRESTUW":
    #     a = 1
    accessDic[originStopID][thisMiddleStopID]["revisitTag"] = True
    return accessDic[originStopID][thisMiddleStopID]["timeRV"]


def revisitSolver():
    db_access = client.cota_access_rel
    # startDate = date(2018, 3, 15)
    # endDate = date(2019, 2, 5)
    startDate = date(2019, 9, 5)
    endDate = date(2019, 9, 11)
    startDate = date(2019, 5, 9)
    endDate = date(2019, 5, 15)
    walkingDistanceLimit = 700
    timeDeltaLimit = 480 * 60 # Extend the query limit to guarantee there is no missing trips, because there will be a lot of missing trips.
    walkingSpeed = 1.4
    sampleRate = 20
    daterange = (transfer_tools.daterange(startDate, endDate))

    for singleDate in (daterange):
        weekday = singleDate.weekday()
        # if weekday != 2:
        #     continue
        todayDate = singleDate.strftime("%Y%m%d")
        GTFSTimestamp = transfer_tools.find_gtfs_time_stamp(singleDate)
        todaySeconds = atime.mktime(singleDate.timetuple())
        gtfsSeconds = str(transfer_tools.find_gtfs_time_stamp(singleDate))
        todayTimestampList = []

        for i in [8]:
        # for i in list(range(6,24)):
            # if i == 8 or i == 12 or i == 18:
            #     continue
            todayTimestampList.append(todaySeconds + i * 60*60)

        for eachTimestamp in todayTimestampList:
            # if eachTimestamp < 1542214800: # Restart point
            #     continue
            print("-----", todayDate, "-----",
                  int(eachTimestamp), "----- Start")
            col_stops = db_GTFS[str(GTFSTimestamp) + "_stops"]
            col_stop_times = db_GTFS[str(GTFSTimestamp) + "_stop_times"]
            col_real_times = db_real_time["R" + todayDate]
            rl_stop_times_rt = list(col_real_times.find(
                {"time": {"$gt": eachTimestamp, "$lt": eachTimestamp + timeDeltaLimit}}))  # Real-time
            rl_stops = col_stops.find({})
            
            accessDic = {}
            # col_access = db_access["rel_" + todayDate + "_" + str(int(eachTimestamp))]
            col_access = db_access["add_" + todayDate + "_" + str(int(eachTimestamp))]
            rl_access = (col_access.find({}))

            stopsDic = {}
            timeListByStopRT = {}
            timeListByTripRT = {}
            arcsDicRT = {}
            for eachStop in rl_stops:
                stopsDic[eachStop["stop_id"]] = eachStop

            for eachTime in rl_stop_times_rt:
                stopID = eachTime["stop_id"]
                tripID = eachTime["trip_id"]
                try:
                    timeListByStopRT[stopID]
                except:
                    timeListByStopRT[stopID] = []

                timeListByStopRT[stopID].append(eachTime)

                try:
                    timeListByTripRT[tripID]
                except:
                    timeListByTripRT[tripID] = []

                timeListByTripRT[tripID].append(eachTime)

            for eachTripID, eachTrip in timeListByTripRT.items():
                if len(eachTrip) < 2:
                    continue
                for index in range(0, len(eachTrip)-1):
                    generatingStopID = eachTrip[index]["stop_id"]
                    receivingStopID = eachTrip[index + 1]["stop_id"]
                    try:
                        arcsDicRT[generatingStopID]
                    except:
                        arcsDicRT[generatingStopID] = {}

                    try:
                        arcsDicRT[generatingStopID][receivingStopID]
                    except:
                        arcsDicRT[generatingStopID][receivingStopID] = {}

                    timeGen = eachTrip[index]["time"]  # RT time
                    timeRec = eachTrip[index + 1]["time"]  # RT time
                    timeGenS = eachTrip[index]["scheduled_time"]
                    timeRecS = eachTrip[index + 1]["scheduled_time"]

                    try:
                        arcsDicRT[generatingStopID][receivingStopID][timeGen]
                    except:
                        arcsDicRT[generatingStopID][receivingStopID][timeGen] = {
                            'time_gen': timeGen, 'time_rec': timeRec, 'bus_time': - timeGen + timeRec, "trip_id": eachTripID, "time_gen_S": timeGenS}

            # Sort the arcsDics with OrderedDic.
            def return_time_gen(e):
                return e[0]
            for startStopID, startStop in arcsDicRT.items():
                for endStopID, endStop in startStop.items():
                    arcsDicRT[startStopID][endStopID] = OrderedDict(
                        sorted(endStop.items(), key=return_time_gen))


            for eachOD in tqdm(rl_access):
                originStopID = eachOD["startStopID"]
                destinationStopID = eachOD["receivingStopID"]
                if destinationStopID == None:
                    destinationStopID = originStopID

                # if eachOD["timeRT"] > 99999 or eachOD["timeSC"] > 99999:
                #     continue

                try:
                    accessDic[originStopID]
                except:
                    accessDic[originStopID] = {}

                eachOD["revisitTag"] = False
                eachOD["timeRV"] = None
                eachOD["walkTimeRV"] = None
                eachOD["waitTimeRV"] = None
                eachOD["busTimeRV"] = None
                eachOD["lastTripIDRV"] = None
                accessDic[originStopID][destinationStopID] = eachOD

            for originStopID, ODs in tqdm(accessDic.items()):
                try:
                    accessDic[originStopID][originStopID]
                except:
                    accessDic[originStopID][originStopID] = {
                        "startStopID": originStopID,
                        "receivingStopID": originStopID,
                        "timeRT": 0,
                        "walkTimeRT": 0,
                        "busTimeRT": 0,
                        "waitTimeRT": 0,
                        "generatingStopIDRT": None,
                        "lastTripIDRT": None,
                        "lastTripTypeRT": None,
                        "transferCountRT": 0,
                        "visitTagRT": True,
                        "timeSC": 0,
                        "walkTimeSC": 0,
                        "busTimeSC": 0,
                        "waitTimeSC": 0,
                        "generatingStopIDSC": None,
                        "lastTripIDSC": None,
                        "lastTripTypeSC": None,
                        "transferCountSC": 0,
                        "visitTagSC": True
                    }

                try:
                    accessDic[originStopID][originStopID]["stop_lat"]
                except:
                    accessDic[originStopID][originStopID]["stop_lat"] = stopsDic[originStopID]["stop_lat"]
                    accessDic[originStopID][originStopID]["stop_lon"] = stopsDic[originStopID]["stop_lon"]

                # Initialization
                accessDic[originStopID][originStopID]["revisitTag"] = True
                accessDic[originStopID][originStopID]["timeRV"] = 0
                accessDic[originStopID][originStopID]["walkTimeRV"] = 0
                accessDic[originStopID][originStopID]["waitTimeRV"] = 0
                accessDic[originStopID][originStopID]["busTimeRV"] = 0

                for destinationStopID, eachOD in ODs.items():
                    lastStopID = destinationStopID
                    if lastStopID == None:
                        continue
                    if accessDic[originStopID][lastStopID]["generatingStopIDSC"] == None: # There is no link between the origin and this destination according to schedule.
                        continue

                    trajectoryList = []  # Store the stopIDs that have not been revisited along the trajectory
                    trajectoryDebugList = []

                    while(lastStopID != originStopID):
                        try:
                            thisRevisitTag = accessDic[originStopID][lastStopID]["revisitTag"]
                        except:
                            break
                        if thisRevisitTag == True:  # the previous stop has been revisited.
                            break
                        trajectoryList.insert(0, lastStopID)
                        trajectoryDebugList.insert(0, False)
                        # Move to the prior stop
                        lastStopID = accessDic[originStopID][lastStopID]["generatingStopIDSC"]

                    for thisMiddleStopIDIndex in range(len(trajectoryList)):
                        thisMiddleStopID = trajectoryList[thisMiddleStopIDIndex]
                        lastMiddleStopID = accessDic[originStopID][thisMiddleStopID]["generatingStopIDSC"]

                        # Revisit the link between the two sebsequent stops

                        # Debug
                        
                        timeRV = revisit(lastMiddleStopID, thisMiddleStopID,
                                         originStopID, eachTimestamp, accessDic, arcsDicRT)
                        try:
                            trajectoryDebugList[thisMiddleStopIDIndex] = [int(accessDic[originStopID][thisMiddleStopID]["timeRV"]), int(accessDic[originStopID][thisMiddleStopID]["walkTimeRV"]), int(
                                accessDic[originStopID][thisMiddleStopID]["waitTimeRV"]), int(accessDic[originStopID][thisMiddleStopID]["busTimeRV"]), int(accessDic[originStopID][thisMiddleStopID]["timeSC"]), int(accessDic[originStopID][thisMiddleStopID]["walkTimeSC"]), int(
                                accessDic[originStopID][thisMiddleStopID]["waitTimeSC"]), int(accessDic[originStopID][thisMiddleStopID]["busTimeSC"])]
                        except:
                            pass
                        

                        # lastTimeRV = accessDic[originStopID][lastMiddleStopID]["timeRV"]
                        # thisTripTypeSC = accessDic[originStopID][thisMiddleStopID]["lastTripTypeSC"]
                        # print(lastMiddleStopID, lastTimeRV, thisTripTypeSC)
                        

            
            for originStopID, ODs in tqdm(accessDic.items()):
                insertList = []
                for destinationStopID, eachOD in ODs.items():
                    insertList.append(eachOD)
                client.cota_access_rev[todayDate + "_" +
                                    str(int(eachTimestamp))].insert_many(insertList)
            print("-----", todayDate, "-----",
                  int(eachTimestamp), "-----", len(insertList))

            # break
        # break


if __name__ == "__main__":
    revisitSolver()
