from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
mongo = client["database"]

# -----------------------------------------------------------------------
# User Functions
# -----------------------------------------------------------------------

def check_acc(username):
    return mongo.users.find_one({"_id": username}) is not None

def login_acc(username, password):
    userData = mongo.users.find_one({"_id": username}, {"password": 1})
    return userData is not None and userData["password"] == password

def create_acc(username, password):
    mongo.users.insert_one({
        "_id": username,
        "password": password,
        "reviews": [],
        "wanttotry": []
    })

def get_user(username):
    """Fetch full user document. Useful for profile pages."""
    return mongo.users.find_one({"_id": username})

def get_user_reviews(username):
    """Return list of review IDs for a user's profile."""
    user = mongo.users.find_one({"_id": username}, {"reviews": 1})
    return user.get("reviews", []) if user else []

def get_want_to_try(username):
    """Return user's bucket list of restaurant IDs."""
    user = mongo.users.find_one({"_id": username}, {"wanttotry": 1})
    return user.get("wanttotry", []) if user else []

def add_to_want_to_try(username, restaurant_id):
    """Add a restaurant to a user's bucket list (no duplicates)."""
    mongo.users.update_one(
        {"_id": username},
        {"$addToSet": {"wanttotry": restaurant_id}}
    )

def remove_from_want_to_try(username, restaurant_id):
    """Remove a restaurant from a user's bucket list."""
    mongo.users.update_one(
        {"_id": username},
        {"$pull": {"wanttotry": restaurant_id}}
    )

# -----------------------------------------------------------------------
# Restaurant Functions
# -----------------------------------------------------------------------

def get_all_restaurants():
    """Fetch all restaurants — used to populate the map markers."""
    return list(mongo.restaurants.find())

def get_restaurant(restaurant_id):
    """Fetch a single restaurant by ID — used for restaurant detail pages."""
    return mongo.restaurants.find_one({"_id": restaurant_id})

def add_restaurant(name, location, price, food_type, restaurant_type, schedule):
    """Insert a new restaurant (stretch feature: user-submitted locations)."""
    last = mongo.restaurants.find_one(sort=[("_id", -1)])
    restaurant_id = (last["_id"] + 1) if last else 1

    mongo.restaurants.insert_one({
        "_id": restaurant_id,
        "name": name,
        "location": location,           # (lat, lng) tuple/list
        "price": price,                 # 1-4 scale
        "food_type": food_type,         # e.g. "Chinese", "Mexican"
        "restaurant_type": restaurant_type,  # e.g. "deli", "sit-down", "cart"
        "schedule": schedule,           # list of hours per day
        "reviews": [],
        "rating": [0, 0]               # [sum of ratings, number of ratings]
    })
    return restaurant_id

def filter_restaurants(food_type=None, max_price=None, keyword=None):
    """
    Filter restaurants by food type, price ceiling, or name/cuisine keyword.
    Powers the map filter and search bar.
    """
    query = {}
    if food_type:
        query["food_type"] = food_type
    if max_price:
        query["price"] = {"$lte": max_price}
    if keyword:
        query["$or"] = [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"food_type": {"$regex": keyword, "$options": "i"}}
        ]
    return list(mongo.restaurants.find(query))

def get_top_restaurants(n=10):
    """Return the top N restaurants by average rating."""
    restaurants = get_all_restaurants()
    for r in restaurants:
        total, count = r["rating"][0], r["rating"][1]
        r["avg_rating"] = round(total / count, 2) if count > 0 else 0
    return sorted(restaurants, key=lambda r: r["avg_rating"], reverse=True)[:n]

def get_avg_rating(restaurant_id):
    """Compute average rating from the (sum, count) tuple."""
    r = mongo.restaurants.find_one({"_id": restaurant_id}, {"rating": 1})
    if not r:
        return None
    total, count = r["rating"][0], r["rating"][1]
    return round(total / count, 2) if count > 0 else None

# -----------------------------------------------------------------------
# Review Functions
# -----------------------------------------------------------------------

def get_review(review_id):
    """Fetch a single review by ID."""
    return mongo.reviews.find_one({"_id": review_id})

def get_reviews_for_restaurant(restaurant_id):
    """Fetch all reviews for a restaurant detail page."""
    return list(mongo.reviews.find({"restaurant_id": restaurant_id}))

def add_review(username, restaurant_id, rating, text=""):
    """
    Insert a review and update both the restaurant's and user's review lists.
    """
    last = mongo.reviews.find_one(sort=[("_id", -1)])
    review_id = (last["_id"] + 1) if last else 1

    mongo.reviews.insert_one({
        "_id": review_id,
        "user": username,
        "restaurant_id": restaurant_id,
        "rating": rating,
        "text": text
    })

    # Increment rating sum and count
    mongo.restaurants.update_one(
        {"_id": restaurant_id},
        {
            "$push": {"reviews": review_id},
            "$inc": {"rating.0": rating, "rating.1": 1}
        }
    )
    mongo.users.update_one(
        {"_id": username},
        {"$push": {"reviews": review_id}}
    )
    return review_id

def edit_review(review_id, username, new_rating, new_text=""):
    """Edit a review — only if the requesting user owns it."""
    review = mongo.reviews.find_one({"_id": review_id, "user": username})
    if not review:
        return False  # not found or not the owner

    diff = new_rating - review["rating"]  # adjust sum by the difference; count unchanged

    mongo.reviews.update_one(
        {"_id": review_id},
        {"$set": {"rating": new_rating, "text": new_text}}
    )
    mongo.restaurants.update_one(
        {"_id": review["restaurant_id"]},
        {"$inc": {"rating.0": diff}}
    )
    return True

def delete_review(review_id, username):
    """
    Delete a review and clean up references in restaurant + user docs.
    Returns False if the review doesn't exist or the user doesn't own it.
    """
    review = mongo.reviews.find_one({"_id": review_id, "user": username})
    if not review:
        return False  # not found or not the owner

    mongo.reviews.delete_one({"_id": review_id})
    mongo.restaurants.update_one(
        {"_id": review["restaurant_id"]},
        {
            "$pull": {"reviews": review_id},
            "$inc": {"rating.0": -review["rating"], "rating.1": -1}
        }
    )
    mongo.users.update_one(
        {"_id": username},
        {"$pull": {"reviews": review_id}}
    )
    return True
