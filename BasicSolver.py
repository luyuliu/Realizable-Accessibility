from datetime import timedelta, date
import datetime
from pymongo import MongoClient
import time

class BasicSolver:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db_GTFS = self.client.cota_gtfs
        self.db_time_stamps_set = set()
        self.db_time_stamps = []
        self.db_real_time = self.client.cota_real_time
        self.db_trip_update = self.client.trip_update
        self.calculate_gtfs_timestamp()

    def calculate_gtfs_timestamp(self):
        self.raw_stamps = self.db_GTFS.list_collection_names()
        for each_raw in self.raw_stamps:
            each_raw = int(each_raw.split("_")[0])
            self.db_time_stamps_set.add(each_raw)

        for each_raw in self.db_time_stamps_set:
            self.db_time_stamps.append(each_raw)
        self.db_time_stamps.sort()
        return self.db_time_stamps
        
    def test(self):
        print(self.db_trip_update)

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)
    
    @staticmethod
    def daterangeStatic(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def find_gtfs_time_stamp(self, single_date):
        today_date = single_date.strftime("%Y%m%d")  # date
        today_seconds = time.mktime(time.strptime(today_date, "%Y%m%d"))
        backup = self.db_time_stamps[0]
        for each_time_stamp in self.db_time_stamps:
            if each_time_stamp - today_seconds > 86400:
                return backup
            backup = each_time_stamp
        return self.db_time_stamps[len(self.db_time_stamps) - 1]


    def convert_to_timestamp(self, time_string, single_date):
        theTime = time_string.split(":")
        hours = int(theTime[0])
        minutes = int(theTime[1])
        seconds = int(theTime[2])
        total_second = hours * 3600 + minutes * 60 + seconds

        today_date = single_date.strftime("%Y%m%d")  # date
            
        today_seconds = time.mktime(time.strptime(today_date, "%Y%m%d"))

        return total_second+today_seconds

    def convertSeconds(self, BTimeString):
        time = BTimeString.split(":")
        hours = int(time[0])
        minutes = int(time[1])
        seconds = int(time[2])
        return hours * 3600 + minutes * 60 + seconds

    def sortQuery(self, A):
        return A["seq"]


    def find_alt_time(self, generating_time, route_id, stop_id, today_date, criteria):
        if type(generating_time) is not int:
            return ["no_realtime_trip", "no_realtime_trip", "no_realtime_trip"]
        col_real_time = self.db_real_time["R" + today_date]
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
