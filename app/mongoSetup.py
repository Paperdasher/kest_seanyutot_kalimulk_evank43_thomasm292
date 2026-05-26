from pymongo import MongoClient
import data
import kagglehub
from kagglehub import KaggleDatasetAdapter

client = MongoClient("mongodb://localhost:27017")
mongo = client["tummi"]

mongo.drop_collection("users")
mongo.drop_collection("restaurants")
mongo.drop_collection("reviews")

mongo.create_collection("users")
mongo.create_collection("restaurants")
mongo.create_collection("reviews")

mongo.restaurants.create_index("food_type")
mongo.restaurants.create_index("name")
mongo.reviews.create_index("user")

# Set the path to the file you'd like to load
file_path = "google_maps_restaurants(cleaned).csv"

# Load the latest version
df = kagglehub.dataset_load(
  KaggleDatasetAdapter.PANDAS,
  "beridzeg45/nyc-restaurants",
  file_path,
)

for restaurant_data in df.itertuples(index=False):
    bad_field = False
    for field in restaurant_data:
        if field is None or field == "{}": bad_field = True
    if bad_field: continue

    ratings = {}
    i = 1
    for rating in restaurant_data[4]:
        ratings[str(i)] = int(rating)
        i += 1

    restaurant = data.add_restaurant(
        restaurant_data[1],
        restaurant_data[7],
        restaurant_data[8],
        restaurant_data[6],
        restaurant_data[5],
        "",
        [],
        ratings,
        restaurant_data[0]
    )

    