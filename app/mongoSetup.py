from pymongo import MongoClient
import data
import kagglehub
from kagglehub import KaggleDatasetAdapter

client = MongoClient("mongodb://localhost:27017")
mongo = client["database"]

mongo.drop_collection("users")
mongo.drop_collection("restaurants")
mongo.drop_collection("reviews")

mongo.create_collection("users")
mongo.create_collection("restaurants")
mongo.create_collection("reviews")

# Set the path to the file you'd like to load
file_path = ""

# Load the latest version
df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "beridzeg45/nyc-restaurants",
  file_path,
)

for data in df.itertuples(index=False):
    restaurant = data.add_restaurant(
        data[1],
        [data[7], data[8]],
        data[6],
        data[5],
        "",
        [],
        data[0]
    )

    mongo.restaurants.update_one(
        {"_id": restaurant_id},
        {"link": data[0]},
    )

    ratings = {}
    ratings["5"] = data[4]["Rating 5 "]
    ratings["4"] = data[4]["Rating 4 "]
    ratings["3"] = data[4]["Rating 3 "]
    ratings["2"] = data[4]["Rating 2 "]
    ratings["1"] = data[4]["Rating 1 "]
    data.add_review(
        "",
        restaurant,
        rating
    )
