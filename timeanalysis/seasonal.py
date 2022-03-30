import sys
import csv
import numpy
from datetime import timedelta, date, datetime
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')


breakpointList = [date(2018, 1, 1), date(2018, 5, 1), date(2018, 9, 1), date(
    2019, 1, 1), date(2019, 5, 1), date(2019, 9, 1), date(2020, 1, 1), date(2020, 5, 1)]
# breakpointList = [date(2019, 9, 1)]
jj = 8
budgetList = [i for i in range(5, 121, 5)]

for i in breakpointList:
    SCList = [0] * len(budgetList)
    RVList = [0] * len(budgetList)
    RTList = [0] * len(budgetList)
    SCdiffRVList = [0] * len(budgetList)
    SCdiffRTList = [0] * len(budgetList)
    RTdiffRVList = [0] * len(budgetList)
    count = 0
    inCount = 0
    outCount = 0
    middleCount = 0
    col = client.cota_access_agg["REA_" + (i.strftime("%Y%m%d")) + "_" + str(jj)]
    rl = list(col.find())
    # print(len(rl), "REA_" + (i.strftime("%Y%m%d")) + "_" + str(j))
    for od in rl:
        count += 1
        for ki in range(len(budgetList)):
            k = budgetList[ki]
            SCList[ki] += od["PPA_SC_" + str(k)] 
            RVList[ki] += od["PPA_RV_" + str(k)] 
            RTList[ki] += od["PPA_RT_" + str(k)] 
            
    # print(count, inCount,  middleCount, outCount)
    for ki in range(len(budgetList)):
        SCdiffRVList[ki] = (SCList[ki] - RVList[ki])/SCList[ki]
        SCdiffRTList[ki] = (SCList[ki] - RTList[ki])/SCList[ki]
        RTdiffRVList[ki] = (RTList[ki] - RVList[ki])/RTList[ki]

    print(SCdiffRVList)
    print(SCdiffRTList)
    print(RTdiffRVList)
    print("  ")

                

            