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
    ratings_string = restaurant_data[4][1:-1]
    print(ratings_string)
    ratings_list = ratings_string.split(", ")
    print(ratings_list)
    for rating in ratings_list:
        print(rating[7])
        print(rating.split(": ")[1][:-2])
        ratings[rating[7]] = int(rating.split(": ")[1][:-2])

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

    