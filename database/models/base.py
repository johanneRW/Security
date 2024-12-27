from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Base for alle modeller
Base = declarative_base()

# Databasekonfiguration
#DATABASE_URL ="mysql+pymysql://user:password@localhost/dbname"
DATABASE_URL = "mysql+pymysql://root:password@db/example"  
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)


