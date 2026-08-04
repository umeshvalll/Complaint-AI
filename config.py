import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "secret-key"
    )

    BASE_DIR = os.path.abspath(
        os.path.dirname(__file__)
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(

        "DATABASE_URL",

        "sqlite:///" + os.path.join(
            BASE_DIR,
            "complaints.db"
        )

    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail Configuration

    MAIL_SERVER = "smtp.gmail.com"

    MAIL_PORT = 587

    MAIL_USE_TLS = True

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    # Gemini API Key

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")