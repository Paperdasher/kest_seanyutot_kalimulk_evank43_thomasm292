from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
mongo = client["database"]

mongo.drop_collection("users")
mongo.drop_collection("restaurants")
mongo.drop_collection("reviews")

mongo.create_collection("users")
mongo.create_collection("restaurants")
mongo.create_collection("reviews")