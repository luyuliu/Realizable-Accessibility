# This file is for visualizing the data in GDBs to PNG. The visualization value is normdiff

import multiprocessing
import sys
import arcpy
import csv
import numpy
from datetime import timedelta, date, datetime
arcpy.env.overwriteOutput = True

breakpointList = [date(2019, 9, 1)]
timepointList = [8]
budgetList = [i for i in range(5, 121, 5)]

# predefined layer with symbology ready. The symobology is unique value. To satisfy the condition, you will need to make a field in the csv file called "tag" and tag = 1 means it's the room of interests. I do this in excel: basically create a new field and set all values to 1 and join. So after joining only the rooms of interests will have the tag=1 flag.
symbologyLayer = r"D:\Luyu\reliability\serious_reliability\buffer_layer_SC.lyr"
symbologyLayer2 = r"D:\Luyu\reliability\serious_reliability\buffer_layer_RV.lyr"

for i in breakpointList:
    for j in timepointList:
        for k in budgetList:
            fileLocation = "HIGBROS_" + str(k) + "_Buffer_SC"
            fileLocation2 = "HIGBROS_" + str(k) + "_Buffer_RV"
            # Visualization mxd. But it will not be saved. Just use it as an intermedium mxd.
            mxd = arcpy.mapping.MapDocument(
                r"D:\Luyu\reliability\serious_reliability\visualization.mxd")
            # Find the data frame. vis.mxd is blank and created manually in the arcmap, so it will only have one data frame named "Layers"
            df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
            geoGDB = r"D:\Luyu\reliability\serious_reliability\PPA.gdb"
            # arcpy.TableToTable_conversion(crosswalk, geoGDB, 'crosswalk')
            arcpy.env.workspace = geoGDB  # set the gdb as environment to save the long path
            # interior_space = arcpy.management.MakeFeatureLayer("interior_space_joined", "interior_space_lyr")
            # interior_space = arcpy.management.MakeFeatureLayer("interior_space_joined", "interior_space_lyr")
            rawLayer = arcpy.mapping.Layer(fileLocation)
            arcpy.ApplySymbologyFromLayer_management(rawLayer, symbologyLayer)
            arcpy.mapping.AddLayer(df, rawLayer)
            rawLayer2 = arcpy.mapping.Layer(fileLocation2)
            arcpy.ApplySymbologyFromLayer_management(rawLayer2, symbologyLayer2)
            arcpy.mapping.AddLayer(df, rawLayer2)
            print(i, j, k)

            arcpy.mapping.ExportToPNG(mxd, r"D:\Luyu\reliability\serious_reliability\pngs\PPA_" + str(k)+ ".png")
            # arcpy.mapping.ExportToPDF(
            #     new_mxd, r"D:\Luyu\reliability\serious_reliability\pdfs" + "\\" + fileLocation + ".pdf")
            del mxd, rawLayer
        # break
