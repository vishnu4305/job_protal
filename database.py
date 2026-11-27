from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+mysqlconnector://job:job%40123@localhost:3306/jobportal", pool_pre_ping=True)
LocalSession = sessionmaker(bind=engine,
                            autoflush=True,
                            autocommit=False) 

Base = declarative_base()
def get_session():
    session = LocalSession()
    return session