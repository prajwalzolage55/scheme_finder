from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from engine.eligibility import find_eligible_schemes, get_scheme_by_id

schemes_bp = Blueprint("schemes", __name__)

def get_db():
    from app import mongo
    return mongo.db

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ─── User Input Form ──────────────────────────────────────────────────────────
@schemes_bp.route("/form")
@login_required
def form():
    return render_template("form.html")


# ─── Results Dashboard ────────────────────────────────────────────────────────
@schemes_bp.route("/results", methods=["POST"])
@login_required
def results():
    db = get_db()
    user_data = {
        "annual_income": request.form.get("annual_income", 0),
        "age":           request.form.get("age", 25),
        "gender":        request.form.get("gender", "").lower(),
        "caste":         request.form.get("caste", "general").lower(),
        "state":         request.form.get("state", "").lower().replace(" ", "_"),
        "area_type":     request.form.get("area_type", "urban").lower(),
        "occupation":    request.form.get("occupation", "").lower().replace(" ", "_"),
        "bpl_card":      request.form.get("bpl_card", "no").lower(),
        "has_bank_account": request.form.get("has_bank_account", "yes").lower()
    }

    # Save search to DB
    from datetime import datetime
    db.searches.insert_one({
        "user_id": session.get("user_id"),
        "user_data": user_data,
        "timestamp": datetime.utcnow()
    })

    # Update session for chatbot context
    session["user_data"] = user_data

    eligible, explore = find_eligible_schemes(user_data)
    return render_template("results.html", eligible=eligible, explore=explore, user_data=user_data)


# ─── Scheme Detail ────────────────────────────────────────────────────────────
@schemes_bp.route("/scheme/<scheme_id>")
@login_required
def scheme_detail(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        return redirect(url_for("main.home"))

    user_data = session.get("user_data", {})

    # Get match score
    from engine.eligibility import calculate_match_score
    score, reasons, blockers = calculate_match_score(scheme, user_data)

    return render_template("scheme_detail.html", scheme=scheme, score=score,
                           reasons=reasons, blockers=blockers)


# ─── Document Checklist ───────────────────────────────────────────────────────
@schemes_bp.route("/checklist/<scheme_id>")
@login_required
def checklist(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        return redirect(url_for("main.home"))
    return render_template("checklist.html", scheme=scheme)


# ─── Application Guide ────────────────────────────────────────────────────────
@schemes_bp.route("/guide/<scheme_id>")
@login_required
def guide(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        return redirect(url_for("main.home"))
    return render_template("guide.html", scheme=scheme)
