import os
from pathlib import Path


def settings():
    return {
        "DATABASE": os.getenv("DATABASE_PATH", str(Path(__file__).parent / "loja.db")),
        "SECRET_KEY": os.getenv("APP_SECRET"),
        "ADMIN_TOKEN": os.getenv("ADMIN_TOKEN"),
        "DEBUG": os.getenv("APP_DEBUG", "false").lower() == "true",
    }
