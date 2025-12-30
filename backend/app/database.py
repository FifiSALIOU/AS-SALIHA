from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, DisconnectionError
from fastapi import HTTPException, status
import os

from dotenv import load_dotenv

load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER", "tickets_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "tickets_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Ajouter un timeout de connexion pour éviter les blocages
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    connect_args={
        "connect_timeout": 5,  # Timeout de 5 secondes pour la connexion
        "options": "-c statement_timeout=10000"  # Timeout de 10 secondes pour les requêtes
    },
    pool_pre_ping=True,  # Vérifier la connexion avant de l'utiliser
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        # Tester la connexion avant de continuer
        db.execute(text("SELECT 1"))
        yield db
    except (OperationalError, DisconnectionError) as e:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossible de se connecter à la base de données. Vérifiez que PostgreSQL est démarré. Erreur: {str(e)}"
        )
    except Exception as e:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de base de données: {str(e)}"
        )
    finally:
        db.close()


