import sys
import csv
import numpy
from datetime import timedelta, date, datetime
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')


breakpointList = [date(2018, 1, 1), date(2018, 5, 1), date(2018, 9, 1), date(
    2019, 1, 1), date(2019, 5, 1), date(2019, 9, 1), date(2020, 1, 1), date(2020, 5, 1)]
# breakpointList = [date(2019, 9, 1)]
jj = 18
budgetList = [i for i in range(5, 121, 5)]

leftup = [40.0064, -83.016767]
rightdown = [39.95232, -82.983164]

leftup2 = [	40.064282, -83.07086]
rightdown2 = [	39.913961, 		-82.929287]

for i in breakpointList:
    inList = [0] * len(budgetList)
    meanList = [0] * len(budgetList)
    middleList = [0] * len(budgetList)
    outList = [0] * len(budgetList)
    count = 0
    inCount = 0
    outCount = 0
    middleCount = 0
    col = client.cota_access_agg["REA_" + (i.strftime("%Y%m%d")) + "_" + str(jj)]
    rl = list(col.find())
    # print(len(rl), "REA_" + (i.strftime("%Y%m%d")) + "_" + str(j))
    for od in rl:
        count += 1
        if float(od["lon"]) < rightdown[1] and float(od["lat"]) > rightdown[0] and float(od["lon"]) > leftup[1] and float(od["lat"]) < leftup[0]:
            inCount += 1
        elif float(od["lon"]) < rightdown2[1] and float(od["lat"]) > rightdown2[0] and float(od["lon"]) > leftup2[1] and float(od["lat"]) < leftup2[0]:
            middleCount += 1
        else:
            outCount += 1
        for ki in range(len(budgetList)):
            k = budgetList[ki]
            if float(od["lon"]) < rightdown[1] and float(od["lat"]) > rightdown[0] and float(od["lon"]) > leftup[1] and float(od["lat"]) < leftup[0]:
                inList[ki] += (od["PPA_SC_" + str(k)] - od["PPA_RV_" + str(k)])/od["PPA_SC_" + str(k)]
            elif float(od["lon"]) < rightdown2[1] and float(od["lat"]) > rightdown2[0] and float(od["lon"]) > leftup2[1] and float(od["lat"]) < leftup2[0]:
                middleList[ki] += (od["PPA_SC_" + str(k)] - od["PPA_RV_" + str(k)])/od["PPA_SC_" + str(k)]
            else:
                outList[ki] += (od["PPA_SC_" + str(k)] - od["PPA_RV_" + str(k)])/od["PPA_SC_" + str(k)]
            meanList[ki] += (od["PPA_SC_" + str(k)] - od["PPA_RV_" + str(k)])/od["PPA_SC_" + str(k)]
            
    # print(count, inCount,  middleCount, outCount)
    for j in range(len(budgetList)):
        inList[j] /= inCount
        outList[j] /= outCount
        middleList[j] /= middleCount
        meanList[j] /= count

    print(inList)
    print(middleList)
    print(outList)
    print(meanList)
    print("  ")

                

            