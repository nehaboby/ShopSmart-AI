
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-this")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///shopsmart.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    AI_MODEL = os.getenv("AI_MODEL", "gpt-4.1-mini")
