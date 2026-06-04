"""Backend configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend/ root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Config:
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "short_drama")
    DATABASE_URL: str = (
        f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    JIMENG_API_KEY: str = os.getenv("JIMENG_API_KEY", "")
    JIMENG_API_SECRET: str = os.getenv("JIMENG_API_SECRET", "")
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "")

    TOS_ACCESS_KEY: str = os.getenv("TOS_ACCESS_KEY", "")
    TOS_SECRET_KEY: str = os.getenv("TOS_SECRET_KEY", "")
    TOS_BUCKET: str = os.getenv("TOS_BUCKET", "")
    TOS_ENDPOINT: str = os.getenv("TOS_ENDPOINT", "")
    TOS_REGION: str = os.getenv("TOS_REGION", "cn-beijing")

    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")


config = Config()
