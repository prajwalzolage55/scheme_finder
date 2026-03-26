from flask import Flask, render_template, session, redirect, url_for
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "scheme-finder-secret-key-change-in-production")

# ─── MongoDB Setup ────────────────────────────────────────────────────────────
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/schemefinder")
mongo = PyMongo(app)

# ─── Register Blueprints ──────────────────────────────────────────────────────
from routes.auth import auth_bp
from routes.schemes import schemes_bp
from routes.chatbot import chatbot_bp

app.register_blueprint(auth_bp)
app.register_blueprint(schemes_bp)
app.register_blueprint(chatbot_bp)

# ─── Main Routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main_home"))
    return render_template("home.html")

@app.route("/home")
def main_home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ─── Error Handlers ───────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("about.html"), 404

# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
