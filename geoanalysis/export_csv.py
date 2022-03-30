
from pymongo import MongoClient
import pandas

client = MongoClient('localhost', 27017)

db_agg = client.cota_access_agg

col_list = db_agg.list_collection_names()

for each_col in col_list:
    rl_agg = list(db_agg[each_col].find())
    docs = pandas.DataFrame(rl_agg)
    docs.pop("_id")
    filename = r"D:\Luyu\reliability\raw"
    docs.to_csv(filename + "\\" + each_col + ".csv", "," ,index=False)