import glob
from PIL import Image
from datetime import timedelta, date, datetime
# filepaths

breakpointList = [date(2018, 1, 1), date(2018, 5, 1), date(2018, 9, 1), date(
    2019, 1, 1), date(2019, 5, 1), date(2019, 9, 1), date(2020, 1, 1)]
timepointList = [8, 12, 18]
budgetList = [i for i in range(5, 121, 5)]


for j in timepointList:
    for k in budgetList: 
        fp_in = r"D:\Luyu\reliability\serious_reliability\pdfs\REA_project_REA_*_8_10.png"
        fp_out = r"D:\Luyu\reliability\serious_reliability\gifs\REA_" + str(j) + "_" + str(k) + ".gif"

        img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
        img.save(fp=fp_out, format='GIF', append_images=imgs,
                save_all=True, duration=200, loop=0)