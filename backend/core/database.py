import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


URL_LOCAL = "mysql+pymysql://root:@host.docker.internal:3306/SistemaPrevencionDesercion"

URL_LOCAL = "mysql+pymysql://root:@localhost:3306/SistemaPrevencionDesercion"
SQLALCHEMY_DATABASE_URL = URL_LOCAL


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", URL_LOCAL)


is_remote = "aivencloud.com" in SQLALCHEMY_DATABASE_URL
connect_args = {"ssl": {}} if is_remote else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()