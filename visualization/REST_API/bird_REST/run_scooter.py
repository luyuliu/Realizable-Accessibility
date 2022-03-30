from pymongo import MongoClient

codeString = '''DOMAIN = {
    '''

client = MongoClient("localhost", 27017, maxPoolSize=50)

cols = client.bird_location.list_collection_names()
for todayDate in cols:
    codeString = codeString + "'" + todayDate + "': {'datasource': {" + "'source': '" + todayDate + "'}},"+'''
    '''

codeString=codeString +"}"





codeString = codeString + '''
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

MONGO_DBNAME = 'bird_location'

ALLOW_UNKNOWN=True

PAGINATION_LIMIT = 10000

PAGINATION_DEFAULT = 10000'''

try:
    F = open("C:\\Users\\liu.6544\\Documents\\GitHub\\ScooterBrother\\visualization\\REST_API\\lime_REST\\setting.py","x")
except:
    F = open("C:\\Users\\liu.6544\\Documents\\GitHub\\ScooterBrother\\visualization\\REST_API\\lime_REST\\setting.py","w")
F.write(codeString)

F.close()