import glob
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta, date, datetime
# filepaths

breakpointList = [date(2019, 9, 1)]
timepointList = [8]
budgetList = [i for i in range(5, 121, 5)]


for i in breakpointList:
    for j in timepointList: 
        fp_out = r"D:\Luyu\reliability\serious_reliability\pngs\PPAs.gif"
        img_list = []
        for k in budgetList:
            fp_int = r"D:\Luyu\reliability\serious_reliability\pngs\PPAt_" + str(k) + ".png"
            fp_in = r"D:\Luyu\reliability\serious_reliability\pngs\PPA_" + str(k) + ".png"
            img = Image.open(fp_in) 
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("D:\\Luyu\\reliability\\serious_reliability\\"+"OpenSans-Regular.ttf", 30)
            # draw.text((x, y),"Sample Text",(r,g,b))
            draw.text((0, 0),"Time budget: " + str(k) + " minutes",(0,0,0), font=font)
            img.save(fp_int)
            img_list.append(fp_int)
        # a = sorted(glob.glob(fp_in))
        # print(name_list)
        img, *imgs = [Image.open(f) for f in img_list]
        img.save(fp=fp_out, format='GIF', append_images=imgs,
                save_all=True, duration=600, loop=0)
    #     break
    # break