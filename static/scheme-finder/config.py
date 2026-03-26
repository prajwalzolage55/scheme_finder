import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MONGO_URI  = os.getenv("MONGO_URI", "mongodb://localhost:27017/schemefinder")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
