from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Cambia esta línea en database.py
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@host.docker.internal:3306/SistemaPrevencionDesercion"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# El inyector de dependencias vital para los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()