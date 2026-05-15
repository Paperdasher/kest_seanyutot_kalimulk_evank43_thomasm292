from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
mongo = client["database"]

def check_acc(username):
    return mongo.users.find_one({"_id": username}) is not None

def login_acc(username, password):
    userData = mongo.users.find_one({"_id": username}, {"password":1})

    return userData is not None and userData["password"] == password

def create_acc(username, password):
    mongo.users.insert_one({
        "_id": username,
        "password": password
    })