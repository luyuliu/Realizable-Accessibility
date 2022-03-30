import sys
import csv
import numpy
from datetime import timedelta, date, datetime
import time
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')


# breakpointList = [date(2018, 1, 1), date(2018, 5, 1), date(2018, 9, 1), date(
#     2019, 1, 1), date(2019, 5, 1), date(2019, 9, 1), date(2020, 1, 1), date(2020, 5, 1)]

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

dateList = [date(2018,9,1), date(2018,9,8), date(2018,9,22), date(2018,10,6), date(2018,10,13), date(2018,11,3), date(2018,11,24), date(2019,8,31), date(2019,9,7), date(2019,9,21), date(2019,10,5), date(2019,10,26), date(2019,11,9), date(2019,11,23)]
    

jj = 8
budgetList = [i for i in range(5, 121, 5)]

# leftup = [40.0064, -83.016767]
# rightdown = [39.95232, -82.983164]

# leftup2 = [	40.064282, -83.07086]
# rightdown2 = [39.913961, -82.929287]

for eachDate in dateList:
    weekday = eachDate.weekday()
    # inList = [0] * len(budgetList)
    SCList = [0] * len(budgetList)
    RVList = [0] * len(budgetList)
    RTList = [0] * len(budgetList)
    SCdiffRVList = [0] * len(budgetList)
    SCdiffRTList = [0] * len(budgetList)
    RTdiffRVList = [0] * len(budgetList)
    # middleList = [0] * len(budgetList)
    # outList = [0] * len(budgetList)
    count = 0
    # inCount = 0
    # outCount = 0
    # middleCount = 0
    todayDate = eachDate.strftime("%Y%m%d")
    startSecond = int(time.mktime(time.strptime(todayDate, "%Y%m%d")) + jj * 3600)
    col = client.cota_access_football["REV_" + eachDate.strftime("%Y%m%d") + "_" + str(startSecond)]
    # print(eachDate.strftime("%Y%m%d") + "_" + str(startSecond))
    rl = (col.find())
    # print(len(rl), "REA_" + (i.strftime("%Y%m%d")) + "_" + str(j))
    for od in rl:
        count += 1
        # if float(od["lon"]) < rightdown[1] and float(od["lat"]) > rightdown[0] and float(od["lon"]) > leftup[1] and float(od["lat"]) < leftup[0]:
        #     inCount += 1
        # elif float(od["lon"]) < rightdown2[1] and float(od["lat"]) > rightdown2[0] and float(od["lon"]) > leftup2[1] and float(od["lat"]) < leftup2[0]:
        #     middleCount += 1
        # else:
        #     outCount += 1
        
        timeRV = od["timeRV"]
        timeSC = od["timeSC"]
        timeRT = od["timeRT"]

        if timeRV == None:
            timeRV = sys.maxsize
        for ki in range(len(budgetList)):
            budget = budgetList[ki]
            if timeRV < budget * 60: # If travel time between the stops are smaller than the budget, then it's accessible
                RVList[(ki)] += 1
            if timeSC < budget * 60:
                SCList[(ki)] += 1
            if timeRT < budget * 60:
                RTList[(ki)] += 1
    # print(count, inCount,  middleCount, outCount)
    if count == 0:
        continue
    for j in range(len(budgetList)):
        # RVList[j] /= count
        # SCList[j] /= count
        # RTList[j] /= count
        SCdiffRVList[j] = (SCList[j] - RVList[j])/RVList[j]
        SCdiffRTList[j] = (SCList[j] - RTList[j])/RTList[j]
        RTdiffRVList[j] = (RTList[j] - RVList[j])/RVList[j]


    print(SCdiffRVList)
    # print(SCdiffRTList)
    # print(RTdiffRVList)
    print("  ")

                

            