# This file calcaulte the average # accessible stops (PPA) for a whole quadrimester (4 months aggregation)

import sys
import csv
import numpy
from datetime import timedelta, date, datetime
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')


# breakpointList = [date(2018, 1, 1), date(2018, 5, 1), date(2018, 9, 1), date(
#     2019, 1, 1), date(2019, 5, 1), date(2019, 9, 1), date(2020, 1, 1), date(2020, 5, 1)]
breakpointList = [date(2019, 9, 1)]
jj = 18
budgetList = [i for i in range(5, 121, 5)]

leftup = [40.0064, -83.016767]
rightdown = [39.95232, -82.983164]

leftup2 = [	40.064282, -83.07086]
rightdown2 = [	39.913961, 		-82.929287]

for i in breakpointList:
    inList = [0] * len(budgetList)
    middleList = [0] * len(budgetList)
    outList = [0] * len(budgetList)
    count = 0
    col = client.cota_access_agg["REA_" + (i.strftime("%Y%m%d")) + "_" + str(jj)]
    rl = list(col.find())
    # print(len(rl), "REA_" + (i.strftime("%Y%m%d")) + "_" + str(j))
    for od in rl:
        count += 1
        for ki in range(len(budgetList)):
            k = budgetList[ki]
            inList[ki] += od["PPA_SC_" + str(k)]
            middleList[ki] += od["PPA_RT_" + str(k)] 
            outList[ki] += od["PPA_RV_" + str(k)]
            
    # print(count, inCount,  middleCount, outCount)
    for j in range(len(budgetList)):
        inList[j] /= count
        outList[j] /= count
        middleList[j] /= count

    print(inList)
    print(middleList)
    print(outList)
    print("  ")

                

            