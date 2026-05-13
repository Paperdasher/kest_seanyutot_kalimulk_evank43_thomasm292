# Sean Takahashi, Thomas Mackey, Kalimul Kaif, Evan Khosh
# kest
# SoftDev
# P05
# 2026-06-01m

from flask import Flask, render_template, request, flash, url_for, redirect, session


app = Flask(__name__)

app.secret_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"


@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
