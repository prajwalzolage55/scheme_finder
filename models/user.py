from datetime import datetime

def create_user(name, email, phone, password_hash):
    return {
        "name": name,
        "email": email.lower().strip(),
        "phone": phone,
        "password": password_hash,
        "created_at": datetime.utcnow(),
        "profile_complete": False,
        "last_search": None
    }

def create_user_profile(user_id, profile_data):
    return {
        "user_id": user_id,
        "annual_income": int(profile_data.get("annual_income", 0)),
        "age": int(profile_data.get("age", 0)),
        "gender": profile_data.get("gender", ""),
        "caste": profile_data.get("caste", "general"),
        "state": profile_data.get("state", ""),
        "area_type": profile_data.get("area_type", "urban"),
        "occupation": profile_data.get("occupation", ""),
        "bpl_card": profile_data.get("bpl_card", "no"),
        "has_bank_account": profile_data.get("has_bank_account", "yes"),
        "updated_at": datetime.utcnow()
    }
