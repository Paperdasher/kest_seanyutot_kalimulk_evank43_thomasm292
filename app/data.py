from pymongo import MongoClient
from bson import ObjectId

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

def get_restaurants():
    return list(mongo.restaurants.find({}, {"_id": 1, "name": 1, "rating": 1, "location": 1, "price": 1, "food_type": 1, "restaurant_type": 1, "opens": 1, "closes": 1}))

def get_one_restaurant(id):
    return mongo.restaurants.find_one({"_id": ObjectId(id)})