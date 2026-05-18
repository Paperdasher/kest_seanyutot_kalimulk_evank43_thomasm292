# Sean Takahashi, Thomas Mackey, Kalimul Kaif, Evan Khosh
# kest
# SoftDev
# P05
# 2026-06-01m

from flask import Flask, render_template, request, flash, url_for, redirect, session
import folium
import jsonify

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
    restaurants = data.get_restaurants()
    for r in restaurants:
        r["_id"] = str(r["_id"])
    return jsonify(restaurants)

@app.route("/restaurant/<id>")
def restaurant_page(id):
    restaurant = data.get_one_restaurant(id)
    reviews = list(data.mongo.reviews.find({"restaurant_id": restaurant["_id"]}, {"_id": 0, "username": 1, "rating": 1, "comment": 1}))
    return render_template("restaurant.html", restaurant=restaurant, reviews=reviews)

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
        # store username and password as a variable
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

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for("login"))

    if request.method == 'POST':
        pass

    return render_template("profile.html", username=session['username'])

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
