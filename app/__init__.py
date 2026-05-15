# Sean Takahashi, Thomas Mackey, Kalimul Kaif, Evan Khosh
# kest
# SoftDev
# P05
# 2026-06-01m

from flask import Flask, render_template, request, flash, url_for, redirect, session
import data

app = Flask(__name__)

app.secret_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for("login"))

    return render_template("home.html", username=session['username'])

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

        account = check_password(username)

        if data.login_acc(username, password):
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Username or password is incorrect")

    return render_template('login.html')

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
