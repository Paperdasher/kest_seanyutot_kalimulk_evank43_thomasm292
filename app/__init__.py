# Sean Takahashi, Thomas Mackey, Kalimul Kaif, Evan Khosh
# kest
# SoftDev
# P05
# 2026-06-01

from flask import Flask, render_template, request, flash, url_for, redirect, session, jsonify
import folium
from datetime import datetime

import data

app = Flask(__name__)

app.secret_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for("login"))

    return render_template("home.html", username=session['username'])

@app.route("/api/restaurants")
def get_restaurants():
    restaurants = data.get_all_restaurants()
    for r in restaurants:
        r["_id"] = str(r["_id"])

    return jsonify(restaurants)

@app.route("/api/rating/<int:id>")
def get_avg_rating(id):
    avg = data.get_avg_rating(id)
    return jsonify({"avg": avg})

@app.route("/api/bucket-list")
def get_bucket_list():
    if 'username' not in session:
        return jsonify([])
    user = data.get_user(session['username'])
    return jsonify(user.get("wanttotry", []))

@app.route("/restaurant/<int:id>")
def restaurant_page(id):
    if 'username' not in session:
        return redirect(url_for("login"))

    restaurant = data.get_restaurant(id)
    if not restaurant:
        return "Restaurant not found", 404
    restaurant["price"] = int(restaurant["price"])

    reviews = data.get_non_empty_reviews_for_restaurant(id)
    avg = data.get_avg_rating(id)
    review_count = data.get_review_count(id)

    current_user = data.get_user(session['username'])
    in_bucket = str(id) in current_user.get("wanttotry", [])

    # Check if the logged-in user already left a review for this restaurant
    user_review = data.get_user_review_for_restaurant(id, session['username'])

    # Proposal / removal state
    affirmations = restaurant.get("affirmations", [])
    removal_affirmations = restaurant.get("removal_affirmations", [])

    return render_template(
        "restaurant.html",
        restaurant=restaurant,
        reviews=reviews,
        avg_rating=avg,
        review_count=review_count,
        in_bucket=in_bucket,
        user_review=user_review,
        username=session['username'],
        now=datetime.now(),
        is_proposed=bool(restaurant.get("proposed")),
        affirm_count=len(affirmations),
        user_affirmed=session['username'] in affirmations,
        removal_count=len(removal_affirmations),
        user_affirmed_removal=session['username'] in removal_affirmations,
        required_affirmations=data.REQUIRED_AFFIRMATIONS,
    )

@app.route("/logout")
def logout():
    session.pop('username')
    return redirect(url_for("login"))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for("home"))

    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        if not username or not password:
            return render_template("register.html", error="Missing username or password")

        if data.check_acc(username):
            return render_template("register.html", error="Username already exists")

        data.create_acc(username, password)

        session['username'] = username
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for("home"))

    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        if not username or not password:
            return render_template('login.html', error="Missing username or password")

        if data.login_acc(username, password):
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Username or password is incorrect")

    return render_template('login.html')

@app.route("/profile")
@app.route("/profile/<username>")
def profile(username=None):
    if 'username' not in session:
        return redirect(url_for("login"))

    current_user = data.get_user(session['username'])

    # Decide whose profile to show
    if username:
        page_user = data.get_user(username)
        if not page_user:
            return "User not found", 404
    else:
        page_user = current_user

    is_own_profile = page_user["_id"] == current_user["_id"]

    # Reviews left by this user
    reviews_raw = list(data.get_user_reviews(page_user["_id"]))

    # Attach restaurant name to each review
    reviews = []
    for r in reviews_raw:
        restaurant = data.get_restaurant(r["restaurant_id"])
        reviews.append({
            "_id": str(r["_id"]),
            "restaurant_id": r["restaurant_id"],
            "restaurant_name": restaurant["name"] if restaurant else "Unknown",
            "restaurant_cuisine": restaurant.get("food_type", "") if restaurant else "",
            "rating": r.get("rating", 0),
            "body": r.get("text", ""),
            "created_at": r.get("created_at", ""),
        })

    # Sort newest first
    reviews.sort(key=lambda x: x["created_at"], reverse=True)

    # Bucket list
    bucket_ids = page_user.get("wanttotry", [])  # list of restaurant_id strings
    bucket_list = []
    for rid in bucket_ids:
        try:
            restaurant = data.get_restaurant(int(rid))
            if restaurant:
                bucket_list.append({
                    "_id": rid,
                    "name": restaurant["name"],
                    "cuisine": restaurant.get("food_type", ""),
                    "address": restaurant.get("address", ""),
                    "price": restaurant.get("price", ""),
                    "avg_rating": data.get_avg_rating(int(rid)),
                    "schedule": restaurant.get("schedule", []),
                })
        except Exception:
            continue

    return render_template(
        "profile.html",
        page_user=page_user,
        reviews=reviews,
        bucket_list=bucket_list,
        is_own_profile=is_own_profile,
        current_user=current_user,
    )

@app.route("/bucket-list/add/<restaurant_id>", methods=["POST"])
def add_to_bucket(restaurant_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401

    current_user = data.get_user(session["username"])

    # Validate restaurant exists
    try:
        restaurant = data.get_restaurant(int(restaurant_id))
    except Exception:
        return jsonify({"error": "Invalid restaurant id"}), 400

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    bucket = current_user.get("wanttotry", [])
    if restaurant_id in bucket:
        return jsonify({"message": "Already in bucket list"}), 200

    data.add_to_want_to_try(current_user["_id"], restaurant_id)
    return jsonify({"message": "Added to bucket list", "restaurant_id": restaurant_id}), 200

@app.route("/bucket-list/remove/<restaurant_id>", methods=["POST"])
def remove_from_bucket(restaurant_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401

    current_user = data.get_user(session["username"])
    data.remove_from_want_to_try(current_user["_id"], restaurant_id)
    return jsonify({"message": "Removed from bucket list", "restaurant_id": restaurant_id}), 200

@app.route("/review/add/<int:restaurant_id>", methods=["POST"])
def add_review(restaurant_id):
    if "username" not in session:
        return redirect(url_for("login"))
    rating = int(request.form.get("rating", 0))
    body = request.form.get("body", "").strip()
    if rating < 1 or rating > 5:
        flash("Please select a rating.", "danger")
        return redirect(url_for("restaurant_page", id=restaurant_id))
    data.add_review(session["username"], restaurant_id, rating, body)
    return redirect(url_for("restaurant_page", id=restaurant_id))

@app.route("/review/delete/<review_id>", methods=["POST"])
def delete_review(review_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        review_id_int = int(review_id)
    except ValueError:
        return jsonify({"error": "Invalid review id"}), 400
    deleted = data.delete_review(review_id_int, session["username"])
    if deleted:
        return jsonify({"message": "deleted"})
    return jsonify({"error": "Unauthorized"}), 403

@app.route("/review/edit/<int:review_id>", methods=["POST"])
def edit_review(review_id):
    if "username" not in session:
        return redirect(url_for("login"))
    new_rating = int(request.form.get("rating", 0))
    new_text = request.form.get("body", "").strip()
    restaurant_id = int(request.form.get("restaurant_id", 0))
    if new_rating < 1 or new_rating > 5:
        flash("Please select a rating.", "danger")
        return redirect(url_for("restaurant_page", id=restaurant_id))
    data.edit_review(review_id, session["username"], new_rating, new_text)
    return redirect(url_for("restaurant_page", id=restaurant_id))

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# -----------------------------------------------------------------------
# Community proposals: add / remove restaurants (5-user affirmation)
# -----------------------------------------------------------------------

@app.route("/propose", methods=["GET", "POST"])
def propose_restaurant():
    """
    GET  — show the propose form. A `lat`/`lng` query (dropped from the home
           map) pre-fills the location; the form lets the user adjust the pin
           and enter name, price, food_type, and schedule.
    POST — create the proposed restaurant (proposer auto-affirms) and redirect
           to its restaurant page.
    """
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        food_type = request.form.get("food_type", "").strip()

        try:
            lat = float(request.form.get("lat", ""))
            lng = float(request.form.get("lng", ""))
        except (TypeError, ValueError):
            lat = lng = None

        try:
            price = int(request.form.get("price", 0))
        except (TypeError, ValueError):
            price = 0

        if not name or lat is None or lng is None or price < 1 or price > 4:
            return render_template(
                "propose.html",
                days=DAYS,
                lat=request.form.get("lat", ""),
                lng=request.form.get("lng", ""),
                error="Please drop a pin and fill in the name and price.",
            )

        # Build schedule list: one "HH:MM-HH:MM" entry per day, or "" if closed/unknown
        schedule = []
        for day in DAYS:
            if request.form.get(f"closed_{day}"):
                schedule.append("")
            else:
                open_time = request.form.get(f"open_{day}", "").strip()
                close_time = request.form.get(f"close_{day}", "").strip()
                schedule.append(f"{open_time}-{close_time}" if open_time and close_time else "")

        new_id = data.add_proposed_restaurant(
            name, lat, lng, price, food_type or None,
            schedule if any(schedule) else [], session["username"]
        )
        flash("Proposal submitted! It needs 4 more users to affirm it.", "success")
        return redirect(url_for("restaurant_page", id=new_id))

    # GET
    return render_template(
        "propose.html",
        days=DAYS,
        lat=request.args.get("lat", ""),
        lng=request.args.get("lng", ""),
        error=None,
    )

@app.route("/restaurant/<int:id>/affirm", methods=["POST"])
def affirm_addition(id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = data.affirm_addition(id, session["username"])
    if result is None:
        return jsonify({"error": "Not a pending proposal"}), 400
    return jsonify(result)

@app.route("/restaurant/<int:id>/unaffirm", methods=["POST"])
def unaffirm_addition(id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = data.unaffirm_addition(id, session["username"])
    if result is None:
        return jsonify({"error": "Not a pending proposal"}), 400
    return jsonify(result)

@app.route("/restaurant/<int:id>/affirm-removal", methods=["POST"])
def affirm_removal(id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = data.affirm_removal(id, session["username"])
    if result is None:
        return jsonify({"error": "Cannot propose removal for this restaurant"}), 400
    return jsonify(result)

@app.route("/restaurant/<int:id>/unaffirm-removal", methods=["POST"])
def unaffirm_removal(id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401
    result = data.unaffirm_removal(id, session["username"])
    if result is None:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(result)

# -----------------------------------------------------------------------
# Admin: Restaurant Fill Tool
# -----------------------------------------------------------------------

@app.route("/admin/fill-restaurants")
def fill_restaurants():
    """
    Landing page for the admin fill tool.
    Shows overall progress and redirects to the first unfilled restaurant.
    """
    progress = data.get_fill_progress()
    unfilled = data.get_unfilled_restaurants()

    # Build the first unfilled restaurant's ID to link to
    next_id = unfilled[0]["_id"] if unfilled else None

    return render_template(
        "fill_restaurants.html",
        progress=progress,
        next_id=next_id,
        days=DAYS
    )

@app.route("/admin/fill-restaurants/<int:restaurant_id>", methods=['GET', 'POST'])
def fill_restaurant(restaurant_id):
    """
    GET  — show the fill form for this restaurant.
    POST — save food_type, restaurant_type, and schedule, then redirect to the next unfilled one.
    """
    restaurant = data.get_restaurant(restaurant_id)
    if not restaurant:
        flash("Restaurant not found.", "error")
        return redirect(url_for("fill_restaurants"))

    if request.method == 'POST':
        action = request.form.get("action", "save_next")

        food_type      = request.form.get("food_type", "").strip()
        restaurant_type = request.form.get("restaurant_type", "").strip()

        # Build schedule list: one entry per day in "HH:MM-HH:MM" format, or "" if closed
        schedule = []
        for day in DAYS:
            closed = request.form.get(f"closed_{day}")
            if closed:
                schedule.append("")
            else:
                open_time  = request.form.get(f"open_{day}", "").strip()
                close_time = request.form.get(f"close_{day}", "").strip()
                schedule.append(f"{open_time}-{close_time}" if open_time and close_time else "")

        data.update_restaurant_meta(
            restaurant_id,
            food_type=food_type or None,
            schedule=schedule if any(schedule) else None
        )

        if action == "save_quit":
            flash(f"Saved {restaurant['name']}. Progress stored — you can resume any time.", "success")
            return redirect(url_for("fill_restaurants"))

        # Find the next unfilled restaurant after this one
        unfilled = data.get_unfilled_restaurants()
        remaining_ids = [r["_id"] for r in unfilled if r["_id"] != restaurant_id]

        if remaining_ids:
            return redirect(url_for("fill_restaurant", restaurant_id=remaining_ids[0]))
        else:
            flash("All restaurants filled! Great work.", "success")
            return redirect(url_for("fill_restaurants"))

    # GET — also fetch next/prev for navigation
    unfilled = data.get_unfilled_restaurants()
    unfilled_ids = [r["_id"] for r in unfilled]
    progress = data.get_fill_progress()

    # Determine position in unfilled queue
    try:
        pos = unfilled_ids.index(restaurant_id)
        prev_id = unfilled_ids[pos - 1] if pos > 0 else None
        next_id = unfilled_ids[pos + 1] if pos < len(unfilled_ids) - 1 else None
    except ValueError:
        # This restaurant is already filled — still allow editing
        pos, prev_id, next_id = None, None, None

    return render_template(
        "fill_restaurant.html",
        restaurant=restaurant,
        progress=progress,
        days=DAYS,
        prev_id=prev_id,
        next_id=next_id,
        pos=pos,
        total_unfilled=len(unfilled_ids)
    )

@app.route("/admin/fill-restaurants/skip/<int:restaurant_id>")
def skip_restaurant(restaurant_id):
    """Skip the current restaurant and move to the next unfilled one."""
    unfilled = data.get_unfilled_restaurants()
    unfilled_ids = [r["_id"] for r in unfilled]
    try:
        pos = unfilled_ids.index(restaurant_id)
        next_id = unfilled_ids[pos + 1] if pos < len(unfilled_ids) - 1 else None
    except ValueError:
        next_id = unfilled_ids[0] if unfilled_ids else None

    if next_id:
        return redirect(url_for("fill_restaurant", restaurant_id=next_id))
    flash("No more unfilled restaurants.", "info")
    return redirect(url_for("fill_restaurants"))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
