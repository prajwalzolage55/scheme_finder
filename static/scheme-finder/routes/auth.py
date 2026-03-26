from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

def get_db():
    from app import mongo
    return mongo.db

# ─── Register ────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        db = get_db()
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not all([name, email, phone, password]):
            flash("All fields are required.", "error")
            return render_template("login.html", mode="register")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("login.html", mode="register")

        if db.users.find_one({"email": email}):
            flash("Email already registered. Please login.", "error")
            return render_template("login.html", mode="register")

        hashed = generate_password_hash(password)
        user_doc = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": hashed,
            "created_at": datetime.utcnow(),
            "profile_complete": False
        }
        result = db.users.insert_one(user_doc)
        session["user_id"] = str(result.inserted_id)
        session["user_name"] = name

        flash("Account created successfully! Let's find your schemes.", "success")
        return redirect(url_for("main.home"))

    return render_template("login.html", mode="register")


# ─── Login ────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        db = get_db()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = db.users.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html", mode="login")

        session["user_id"] = str(user["_id"])
        session["user_name"] = user["name"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("main.home"))

    return render_template("login.html", mode="login")


# ─── Logout ───────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
