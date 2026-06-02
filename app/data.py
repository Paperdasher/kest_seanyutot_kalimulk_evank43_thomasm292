from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
mongo = client["tummi"]

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
    """Return full review documents written by this user."""
    return list(mongo.reviews.find({"user": username}))

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

def add_restaurant(name, lat, lng, address, price, food_type, schedule, rating, link=""):
    """Insert a new restaurant (stretch feature: user-submitted locations)."""
    last = mongo.restaurants.find_one(sort=[("_id", -1)])
    restaurant_id = (last["_id"] + 1) if last else 1

    mongo.restaurants.insert_one({
        "_id": restaurant_id,
        "name": name,
        "lat": lat,
        "lng": lng,
        "address": address,
        "price": price,                 # 1-4 scale
        "food_type": food_type,         # e.g. "Chinese", "Mexican"
        "schedule": schedule,           # list of hours per day
        "reviews": [],
        # rating is a dict: {"1": count, "2": count, "3": count, "4": count, "5": count}
        "rating": rating,
        "link": link,
        "proposed": False               # confirmed restaurant (not awaiting affirmations)
    })
    return restaurant_id

# -----------------------------------------------------------------------
# Proposal Functions (user-submitted additions / removals)
# -----------------------------------------------------------------------
# A change (adding a new restaurant or removing an existing one) needs this
# many users to affirm it before it takes effect. The proposer counts as the
# first affirmation, so an addition needs the proposer + 4 others.
REQUIRED_AFFIRMATIONS = 5

def add_proposed_restaurant(name, lat, lng, price, food_type, schedule, proposed_by, address=""):
    """
    Insert a user-proposed restaurant. It is added to the database immediately
    so it behaves like a normal restaurant (shows on the map and has its own
    page), but carries a `proposed` flag and a list of affirming usernames
    until it gathers enough affirmations. The proposer automatically affirms
    their own proposal.
    """
    last = mongo.restaurants.find_one(sort=[("_id", -1)])
    restaurant_id = (last["_id"] + 1) if last else 1

    mongo.restaurants.insert_one({
        "_id": restaurant_id,
        "name": name,
        "lat": lat,
        "lng": lng,
        "address": address,
        "price": price,
        "food_type": food_type,
        "schedule": schedule,
        "reviews": [],
        "rating": {},
        "link": "",
        "proposed": True,
        "proposed_by": proposed_by,
        "affirmations": [proposed_by],
    })
    return restaurant_id

def affirm_addition(restaurant_id, username):
    """
    Add a user's affirmation to a proposed restaurant. If the proposal reaches
    REQUIRED_AFFIRMATIONS, it is promoted to a normal restaurant.
    Returns a status dict, or None if the restaurant isn't a pending proposal.
    """
    r = mongo.restaurants.find_one({"_id": restaurant_id})
    if not r or not r.get("proposed"):
        return None

    mongo.restaurants.update_one(
        {"_id": restaurant_id},
        {"$addToSet": {"affirmations": username}}
    )

    r = mongo.restaurants.find_one({"_id": restaurant_id})
    count = len(r.get("affirmations", []))
    if count >= REQUIRED_AFFIRMATIONS:
        mongo.restaurants.update_one(
            {"_id": restaurant_id},
            {
                "$set": {"proposed": False},
                "$unset": {"affirmations": "", "proposed_by": ""}
            }
        )
        return {"count": count, "promoted": True}
    return {"count": count, "promoted": False}

def unaffirm_addition(restaurant_id, username):
    """
    Remove a user's affirmation from a proposed restaurant. If no affirmations
    remain, the proposal is withdrawn (the restaurant is deleted).
    Returns a status dict, or None if the restaurant isn't a pending proposal.
    """
    r = mongo.restaurants.find_one({"_id": restaurant_id})
    if not r or not r.get("proposed"):
        return None

    mongo.restaurants.update_one(
        {"_id": restaurant_id},
        {"$pull": {"affirmations": username}}
    )

    r = mongo.restaurants.find_one({"_id": restaurant_id})
    count = len(r.get("affirmations", []))
    if count == 0:
        mongo.restaurants.delete_one({"_id": restaurant_id})
        return {"count": 0, "withdrawn": True}
    return {"count": count, "withdrawn": False}

def affirm_removal(restaurant_id, username):
    """
    Add a user's affirmation that an existing restaurant should be removed.
    The first affirmation creates the removal proposal. If the proposal reaches
    REQUIRED_AFFIRMATIONS, the restaurant and its reviews are deleted.
    Returns a status dict, or None if the restaurant doesn't exist or is itself
    still a pending addition proposal.
    """
    r = mongo.restaurants.find_one({"_id": restaurant_id})
    if not r or r.get("proposed"):
        return None

    mongo.restaurants.update_one(
        {"_id": restaurant_id},
        {"$addToSet": {"removal_affirmations": username}}
    )

    r = mongo.restaurants.find_one({"_id": restaurant_id})
    count = len(r.get("removal_affirmations", []))
    if count >= REQUIRED_AFFIRMATIONS:
        mongo.reviews.delete_many({"restaurant_id": restaurant_id})
        mongo.restaurants.delete_one({"_id": restaurant_id})
        return {"count": count, "removed": True}
    return {"count": count, "removed": False}

def unaffirm_removal(restaurant_id, username):
    """
    Remove a user's affirmation for a restaurant's removal. If no affirmations
    remain, the removal proposal is cancelled.
    Returns a status dict, or None if the restaurant doesn't exist.
    """
    r = mongo.restaurants.find_one({"_id": restaurant_id})
    if not r:
        return None

    mongo.restaurants.update_one(
        {"_id": restaurant_id},
        {"$pull": {"removal_affirmations": username}}
    )

    r = mongo.restaurants.find_one({"_id": restaurant_id})
    count = len(r.get("removal_affirmations", []))
    if count == 0:
        mongo.restaurants.update_one(
            {"_id": restaurant_id},
            {"$unset": {"removal_affirmations": ""}}
        )
    return {"count": count}

def update_restaurant_meta(restaurant_id, food_type=None, schedule=None):
    """
    Update food_type, restaurant_type, and/or schedule for a restaurant.
    Used by the admin fill tool to patch restaurants imported from Kaggle.
    Only fields explicitly passed (not None) are updated.
    """
    updates = {}
    if food_type is not None:
        updates["food_type"] = food_type
    if schedule is not None:
        updates["schedule"] = schedule
    if updates:
        mongo.restaurants.update_one({"_id": restaurant_id}, {"$set": updates})

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
    """Return the top N restaurants by weighted average rating."""
    restaurants = get_all_restaurants()
    for r in restaurants:
        r["avg_rating"] = get_avg_rating_from_doc(r)
    return sorted(restaurants, key=lambda r: r["avg_rating"], reverse=True)[:n]

def get_avg_rating_from_doc(restaurant_doc):
    """
    Compute average rating from a restaurant document's rating dict.
    rating = {"1": count, "2": count, ..., "5": count}
    Returns a float rounded to 1 decimal places, or -1 if no ratings.
    """
    rating = restaurant_doc.get("rating", {})
    total = sum(int(stars) * count for stars, count in rating.items())
    count = sum(rating.values())
    return round(total / count, 1) if count > 0 else 0

def get_avg_rating(restaurant_id):
    """
    Compute average rating by fetching from DB.
    Returns float or None if restaurant not found.
    """
    r = mongo.restaurants.find_one({"_id": restaurant_id}, {"rating": 1})
    if not r:
        return None
    return get_avg_rating_from_doc(r)

def get_review_count(restaurant_id):
    """Return total number of ratings across all star levels."""
    r = mongo.restaurants.find_one({"_id": restaurant_id}, {"rating": 1})
    if not r:
        return 0
    return sum(r.get("rating", {}).values())

# -----------------------------------------------------------------------
# Review Functions
# -----------------------------------------------------------------------

def get_review(review_id):
    """Fetch a single review by ID."""
    return mongo.reviews.find_one({"_id": review_id})

def get_user_review_for_restaurant(review_id, username):
    """Fetch a single review by ID."""
    return mongo.reviews.find_one({"restaurant_id": review_id, "user": username})

def get_reviews_for_restaurant(restaurant_id):
    """Fetch all reviews for a restaurant detail page."""
    return list(mongo.reviews.find({"restaurant_id": restaurant_id}))

def get_non_empty_reviews_for_restaurant(restaurant_id):
    """Fetch all non empty text reviews for a restaurant detail page."""
    reviews = get_reviews_for_restaurant(restaurant_id)
    return [r for r in reviews if r.get("text")]

def add_review(username, restaurant_id, rating, text=""):
    """
    Insert a review and update both the restaurant's and user's review lists.
    rating must be an integer 1-5.
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

    # Increment the count for this star level in the rating dict
    star_key = str(rating)
    mongo.restaurants.update_one(
        {"_id": restaurant_id},
        {
            "$push": {"reviews": review_id},
            "$inc": {f"rating.{star_key}": 1}
        }
    )
    mongo.users.update_one(
        {"_id": username},
        {"$push": {"reviews": review_id}}
    )
    return review_id

def edit_review(review_id, username, new_rating, new_text=""):
    """
    Edit a review — only if the requesting user owns it.
    Updates the restaurant's rating dict by decrementing the old star bucket
    and incrementing the new one.
    """
    review = mongo.reviews.find_one({"_id": review_id, "user": username})
    if not review:
        return False  # not found or not the owner

    old_star_key = str(review["rating"])
    new_star_key = str(new_rating)

    mongo.reviews.update_one(
        {"_id": review_id},
        {"$set": {"rating": new_rating, "text": new_text}}
    )

    # Only touch the DB if the star rating actually changed
    if old_star_key != new_star_key:
        mongo.restaurants.update_one(
            {"_id": review["restaurant_id"]},
            {"$inc": {
                f"rating.{old_star_key}": -1,
                f"rating.{new_star_key}": 1
            }}
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

    star_key = str(review["rating"])

    mongo.reviews.delete_one({"_id": review_id})
    mongo.restaurants.update_one(
        {"_id": review["restaurant_id"]},
        {
            "$pull": {"reviews": review_id},
            "$inc": {f"rating.{star_key}": -1}
        }
    )
    mongo.users.update_one(
        {"_id": username},
        {"$pull": {"reviews": review_id}}
    )
    return True

# -----------------------------------------------------------------------
# Admin / Fill Tool Helpers
# -----------------------------------------------------------------------

def get_unfilled_restaurants(fields=("food_type", "schedule")):
    """
    Return restaurants that are missing data for any of the given fields.
    A field is considered 'missing' if it is falsy (empty string, empty list, None).
    Used by the admin fill tool to find restaurants still needing manual entry.
    """
    query = {"$or": [{field: {"$in": [None, "", []]}} for field in fields]}
    return list(mongo.restaurants.find(query))

def get_fill_progress():
    """
    Return a summary dict for the admin fill tool:
      total       — total restaurant count
      filled      — restaurants with both food_type and schedule set
      remaining   — restaurants still needing at least one field
    """
    total = mongo.restaurants.count_documents({})
    remaining = len(get_unfilled_restaurants())
    return {
        "total": total,
        "filled": total - remaining,
        "remaining": remaining
    }
