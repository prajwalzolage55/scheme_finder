from flask import Blueprint, render_template, request, jsonify, session
import os

chatbot_bp = Blueprint("chatbot", __name__)

SYSTEM_PROMPT = """You are SchemeSaathi — a helpful and friendly AI assistant that helps Indian citizens, especially low-income families, understand government welfare schemes.

Your role:
- Help users understand if they are eligible for schemes like PMAY, PM-KISAN, Ayushman Bharat, PMJAY, Ujjwala Yojana, MGNREGA, MUDRA, and many more
- Explain required documents in simple language
- Guide users on how and where to apply
- Answer in the SAME language the user is asking in (Hindi, Marathi, or English)
- Be warm, simple, and supportive — many users may have low literacy

Rules:
- NEVER give legal advice or guarantee outcomes
- If unsure, say so honestly and suggest visiting the nearest CSC or government office
- Keep responses short, clear, and practical — bullet points where helpful
- Do not make up schemes or eligibility criteria

When user asks about eligibility, ask for: income, age, gender, caste, state, occupation if not provided."""


def get_groq_client():
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


@chatbot_bp.route("/chatbot")
def chatbot():
    if "user_id" not in session:
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))
    user_data = session.get("user_data", {})
    return render_template("chatbot.html", user_data=user_data)


@chatbot_bp.route("/api/chat", methods=["POST"])
def chat_api():
    if "user_id" not in session:
        return jsonify({"error": "Please login first"}), 401

    data = request.get_json()
    messages = data.get("messages", [])
    user_data = session.get("user_data", {})

    if not messages:
        return jsonify({"error": "No message provided"}), 400

    # Build context from user profile
    context_lines = []
    if user_data:
        context_lines.append(f"User profile: income=₹{user_data.get('annual_income','unknown')}/year, "
                             f"age={user_data.get('age','?')}, gender={user_data.get('gender','?')}, "
                             f"caste={user_data.get('caste','?')}, state={user_data.get('state','?')}, "
                             f"area={user_data.get('area_type','?')}, occupation={user_data.get('occupation','?')}, "
                             f"bpl={user_data.get('bpl_card','?')}")

    system = SYSTEM_PROMPT
    if context_lines:
        system += "\n\nCurrent user context (use this to personalise responses):\n" + "\n".join(context_lines)

    client = get_groq_client()
    if not client:
        return jsonify({
            "reply": "⚠️ AI assistant is currently unavailable. Please set GROQ_API_KEY in your .env file. "
                     "You can still use the eligibility form and scheme finder above!"
        })

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ← updated from decommissioned llama3-8b-8192
            max_tokens=600,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system},
                *messages
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Sorry, I couldn't process that right now. Error: {str(e)}"})