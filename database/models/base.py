from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

# Base for alle modeller
Base = declarative_base()

# Databasekonfiguration
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)


