import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.environ["SECRET_KEY"]

ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
DATABASE_URL: str = os.environ["DATABASE_URL"]
TEST_DATABASE_URL: str = os.environ["TEST_DATABASE_URL"]
GEMINI_API_KEY: str = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
