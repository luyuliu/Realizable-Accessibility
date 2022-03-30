from pymongo import MongoClient
import os


def generateSettingFile(databaseName):
    codeString = '''DOMAIN = {
    '''

    client = MongoClient("localhost", 27017, maxPoolSize=50)

    cols = client[databaseName].list_collection_names()
    for todayDate in cols:
        codeString = codeString + "'" + todayDate + "': {'datasource': {" + "'source': '" + todayDate + "'}},"+'''
        '''

    codeString=codeString +"}"





    codeString = codeString + '''
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

MONGO_DBNAME = "'''+databaseName+'''"

X_DOMAINS='*'

ALLOW_UNKNOWN=True

PAGINATION_LIMIT = 10000

PAGINATION_DEFAULT = 10000'''

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "setting.py"
    abs_file_path = os.path.join(script_dir, rel_path)

    try:
        F = open(abs_file_path,"x")
    except:
        F = open(abs_file_path,"w")
    F.write(codeString)

    F.close()
    print("Setting files generated.")

if __name__ == '__main__':
    pass