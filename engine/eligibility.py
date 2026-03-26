import json
import os

# Load all schemes from JSON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMES_PATH = os.path.join(BASE_DIR, "database", "schemes_data.json")

def load_schemes():
    with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_match_score(scheme, user_data):
    """
    Returns a match score (0–100) and reasons for eligibility.
    """
    score = 0
    max_score = 0
    reasons = []
    blockers = []

    rules = scheme.get("eligibility", {})

    # --- Income Check ---
    if "max_income" in rules:
        max_score += 30
        user_income = int(user_data.get("annual_income", 0))
        if user_income <= rules["max_income"]:
            score += 30
            reasons.append(f"Income ₹{user_income:,} is within limit of ₹{rules['max_income']:,}")
        else:
            blockers.append(f"Income ₹{user_income:,} exceeds limit of ₹{rules['max_income']:,}")

    # --- Age Check ---
    if "min_age" in rules or "max_age" in rules:
        max_score += 20
        user_age = int(user_data.get("age", 0))
        min_ok = user_age >= rules.get("min_age", 0)
        max_ok = user_age <= rules.get("max_age", 200)
        if min_ok and max_ok:
            score += 20
            reasons.append(f"Age {user_age} is within eligible range")
        else:
            blockers.append(f"Age {user_age} not in required range ({rules.get('min_age', '0')}–{rules.get('max_age', 'any')})")

    # --- Gender Check ---
    if "gender" in rules:
        max_score += 20
        user_gender = user_data.get("gender", "").lower()
        if user_gender == rules["gender"].lower() or rules["gender"] == "any":
            score += 20
            reasons.append(f"Gender eligibility matched")
        else:
            blockers.append(f"This scheme is only for {rules['gender']} applicants")

    # --- Caste Check ---
    if "caste" in rules:
        max_score += 20
        user_caste = user_data.get("caste", "general").lower()
        if user_caste in [c.lower() for c in rules["caste"]]:
            score += 20
            reasons.append(f"Caste category {user_caste.upper()} is eligible")
        else:
            blockers.append(f"Caste must be one of: {', '.join(rules['caste']).upper()}")

    # --- Area Type Check ---
    if "area_type" in rules:
        max_score += 10
        user_area = user_data.get("area_type", "urban").lower()
        if user_area in [a.lower() for a in rules["area_type"]]:
            score += 10
            reasons.append(f"{user_area.capitalize()} area is covered under this scheme")
        else:
            blockers.append(f"This scheme is for {'/'.join(rules['area_type'])} areas only")

    # --- Occupation Check ---
    if "occupation" in rules:
        max_score += 15
        user_occupation = user_data.get("occupation", "").lower().replace(" ", "_")
        allowed = [o.lower() for o in rules["occupation"]]
        if user_occupation in allowed:
            score += 15
            reasons.append(f"Occupation '{user_occupation.replace('_', ' ')}' qualifies")
        else:
            blockers.append(f"Occupation must be: {', '.join(rules['occupation'])}")

    # --- State Check ---
    if scheme.get("state") not in ["central", None]:
        max_score += 15
        user_state = user_data.get("state", "").lower().replace(" ", "_")
        scheme_state = scheme["state"].lower()
        if user_state == scheme_state or user_state in scheme_state:
            score += 15
            reasons.append(f"State scheme available in your state")
        else:
            blockers.append(f"This is a {scheme['state'].capitalize()} state scheme only")

    # --- BPL Check ---
    if rules.get("bpl"):
        max_score += 10
        user_bpl = user_data.get("bpl_card", "no").lower()
        if user_bpl == "yes":
            score += 10
            reasons.append("BPL card holder — eligible")
        else:
            blockers.append("BPL card required for this scheme")

    # --- Bank Account Check ---
    if rules.get("bank_account"):
        max_score += 5
        user_bank = user_data.get("has_bank_account", "yes").lower()
        if user_bank == "yes":
            score += 5

    # Normalize score
    if max_score == 0:
        return 50, reasons, blockers  # Neutral if no rules

    final_score = int((score / max_score) * 100)

    # If there are hard blockers, cap at 25% unless it's a general awareness scheme
    if blockers and final_score > 40:
        final_score = 25

    return final_score, reasons, blockers


def find_eligible_schemes(user_data):
    """
    Main function: returns sorted list of schemes with match scores.
    """
    schemes = load_schemes()
    results = []

    for scheme in schemes:
        score, reasons, blockers = calculate_match_score(scheme, user_data)
        results.append({
            "id": scheme["id"],
            "name": scheme["name"],
            "category": scheme["category"],
            "ministry": scheme["ministry"],
            "description": scheme["description"],
            "benefits": scheme["benefits"],
            "documents": scheme["documents"],
            "apply_link": scheme["apply_link"],
            "apply_steps": scheme["apply_steps"],
            "tags": scheme.get("tags", []),
            "match_score": score,
            "reasons": reasons,
            "blockers": blockers,
            "state": scheme.get("state", "central")
        })

    # Sort: highly eligible first
    results.sort(key=lambda x: x["match_score"], reverse=True)

    # Split into eligible (>=50%) and explore (<50%)
    eligible = [r for r in results if r["match_score"] >= 50]
    explore  = [r for r in results if r["match_score"] < 50]

    return eligible, explore


def get_scheme_by_id(scheme_id):
    """Fetch a single scheme by ID."""
    schemes = load_schemes()
    for s in schemes:
        if s["id"] == scheme_id:
            return s
    return None
