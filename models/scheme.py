from datetime import datetime

def create_saved_scheme(user_id, scheme_id, scheme_name, match_score):
    return {
        "user_id": user_id,
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "match_score": match_score,
        "saved_at": datetime.utcnow()
    }
