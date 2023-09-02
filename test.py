import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["conversations"]
id=0
language = "english"
mydict = { "user_id":0, "language1": "Highway 37" }

x = mycol.insert_one(mydict)


# find
myquery = { "address": "Park Lane 38" }
mydoc = mycol.find(myquery)
newvalues = { "$set": { "address": "Canyon 123" } }
add = {"$inc": { "a": 1000 } }