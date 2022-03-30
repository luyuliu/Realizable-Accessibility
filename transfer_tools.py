from datetime import timedelta, date
import datetime
from pymongo import MongoClient
import time


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


client = MongoClient('mongodb://localhost:27017/')
db_GTFS = client.cota_gtfs
db_time_stamps_set = set()
db_time_stamps = []
db_real_time = client.cota_real_time
db_trip_update = client.trip_update

raw_stamps = db_GTFS.list_collection_names()
for each_raw in raw_stamps:
    each_raw = int(each_raw.split("_")[0])
    db_time_stamps_set.add(each_raw)

for each_raw in db_time_stamps_set:
    db_time_stamps.append(each_raw)
db_time_stamps.sort()


def find_gtfs_time_stamp(single_date):
    today_date = single_date.strftime("%Y%m%d")  # date
    today_seconds = time.mktime(time.strptime(today_date, "%Y%m%d"))
    backup = db_time_stamps[0]
    for each_time_stamp in db_time_stamps:
        if each_time_stamp - today_seconds > 86400:
            return backup
        backup = each_time_stamp
    return db_time_stamps[len(db_time_stamps) - 1]


def convert_to_timestamp(time_string, single_date):
    theTime = time_string.split(":")
    hours = int(theTime[0])
    minutes = int(theTime[1])
    seconds = int(theTime[2])
    total_second = hours * 3600 + minutes * 60 + seconds
    if single_date ==None:
        return total_second

    today_date = single_date.strftime("%Y%m%d")  # date
        
    today_seconds = time.mktime(time.strptime(today_date, "%Y%m%d"))

    return total_second+today_seconds

def convertSeconds(BTimeString):
    time = BTimeString.split(":")
    hours = int(time[0])
    minutes = int(time[1])
    seconds = int(time[2])
    return hours * 3600 + minutes * 60 + seconds

def sortQuery(A):
    return A["seq"]


def find_alt_time(generating_time, route_id, stop_id, today_date, criteria):
    if type(generating_time) is not int:
        return ["no_realtime_trip", "no_realtime_trip", "no_realtime_trip"]
    col_real_time = db_real_time["R" + today_date]
    real_time = -1
    alt_trips_list = list(col_real_time.find(
        {"stop_id": stop_id, "route_id": route_id}))
    alt_trips_list = sorted(alt_trips_list, key=lambda i: (i['time']))
    if len(alt_trips_list) == 0:
        return "no_realtime_trip"
    for index in range(len(alt_trips_list)):
        i_real_time = alt_trips_list[index]["time"]
        if generating_time <= i_real_time + criteria:
            real_time = i_real_time
            real_trip = alt_trips_list[index]["trip_id"]
            real_trip_seq = alt_trips_list[index]["trip_sequence"]
            break
    if real_time == -1:
        return ["no_realtime_trip", "no_realtime_trip", "no_realtime_trip"]
    else:
        return [real_time, real_trip, real_trip_seq]


if __name__ == "__main__":
    # test
    a = find_alt_time("1517666601", 2, "HIGWESS", "20180203", 5)

    print(1517666601, a)