# This file is for visualizing the polygon data in GDBs to PDFs.

import multiprocessing
import sys
import arcpy
import csv
import numpy
from datetime import timedelta, date, datetime
arcpy.env.overwriteOutput = True

breakpointList = [date(2018, 1, 1), date(2018, 5, 1), date(2018, 9, 1), date(
    2019, 1, 1), date(2019, 5, 1), date(2019, 9, 1), date(2020, 1, 1), date(2020, 5, 1)]
timepointList = [8, 12, 18]
budgetList = [i for i in range(5, 121, 5)]

# predefined layer with symbology ready. The symobology is unique value. To satisfy the condition, you will need to make a field in the csv file called "tag" and tag = 1 means it's the room of interests. I do this in excel: basically create a new field and set all values to 1 and join. So after joining only the rooms of interests will have the tag=1 flag.
symbologyLayer = r"D:\Luyu\reliability\serious_reliability\symbology.lyrx"

for i in breakpointList:
    for j in timepointList:
        for k in budgetList:
            fileLocation = "REA_project_REA_" + \
                (i.strftime("%Y%m%d")) + "_" + str(j)
            # Visualization mxd. But it will not be saved. Just use it as an intermedium mxd.
            mxd = arcpy.mp.ArcGISProject(
                r"D:\Luyu\reliability\serious_reliability\serious_reliability.aprx")
            # Find the data frame. vis.mxd is blank and created manually in the arcmap, so it will only have one data frame named "Layers"
            df = mxd.listMaps("Host")[0]
            geoGDB = r"D:\Luyu\reliability\serious_reliability\serious_reliability.gdb"
            # arcpy.TableToTable_conversion(crosswalk, geoGDB, 'crosswalk')
            arcpy.env.workspace = geoGDB  # set the gdb as environment to save the long path
            # inputLayer = arcpy.management.MakeFeatureLayer(fileLocation, "raw_layer")
            # interior_space = arcpy.mp.LayerFile(r"D:\Luyu\reliability\serious_reliability\serious_reliability.gdb\\" + fileLocation)

            # Apply the symbology from the symbology layer to the input layer
            print( "normdiff_" + str(k))
            inputLayer = arcpy.ApplySymbologyFromLayer_management(
                fileLocation, symbologyLayer, [["VALUE_FIELD", "#", "normdiff_" + str(k)]])
            # interior_space.showLabels = True # show label on
            arcpy.mp.AddLayer(df, inputLayer)
            mxd.saveACopy(r"D:\Luyu\reliability\serious_reliability\mxds" + "\\" + 
                        fileLocation + ".mxd")  # save a copy just in case
            new_mxd = arcpy.mp.MapDocument(r"D:\Luyu\reliability\serious_reliability\mxds" + "\\" + 
                        fileLocation + ".mxd")
            print(i, j, k)

            arcpy.mp.ExportToPDF(
                new_mxd, r"D:\Luyu\reliability\serious_reliability\pdfs" + "\\" + fileLocation + ".pdf")
            break