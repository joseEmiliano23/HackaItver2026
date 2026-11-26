
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Cargar variables del archivo .env
load_dotenv(BASE_DIR / ".env")

# Directorio de base de datos SQLite
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Si existe DATABASE_URL, utilizarla.
    # De lo contrario, utilizar SQLite.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{DATABASE_DIR / 'logistica-central.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de conexión
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # Configuración de sesiones
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    PERMANENT_SESSION_LIFETIME = 1800
