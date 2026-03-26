from flask import Flask, render_template, session, redirect, url_for
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "scheme-finder-secret-key-change-in-production")

# ─── MongoDB Setup ────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI is not set in your .env file!")

app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)

# ─── Verify Connection ────────────────────────────────────────────────────────
with app.app_context():
    if mongo.db is None:
        raise RuntimeError(
            "❌ mongo.db is None — make sure your MONGO_URI includes the "
            "database name, e.g. ...mongodb.net/schemefinder"
        )
    try:
        mongo.db.command("ping")
        print(f"✅ Connected to MongoDB Atlas — database: '{mongo.db.name}'")
    except Exception as e:
        raise RuntimeError(f"❌ Could not reach MongoDB Atlas: {e}")

# ─── Register Blueprints ──────────────────────────────────────────────────────
from routes.auth import auth_bp
from routes.schemes import schemes_bp
from routes.chatbot import chatbot_bp

app.register_blueprint(auth_bp)
app.register_blueprint(schemes_bp)
app.register_blueprint(chatbot_bp)

# ─── Make mongo available to blueprints ───────────────────────────────────────
app.mongo = mongo

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