# import mysql.connector as ms

# def get_connection():
#     connection = ms.connect(
#         host="localhost",
#         user="job",              
#         password="job@123",      
#         database="jobportal"
#     )
#     print("Connected....")
#     return connection

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
# declarative_base - This is used to create the Base class for models
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+mysqlconnector://job:job%40123@localhost:3306/jobportal",connect_args={"check_same_thread":False})
# Database_url - 
# connection arguments - A dictionary of arguments
LocalSession = sessionmaker(bind=engine,
                            autoflush=True,
                            autocommit=False) # returns a class

Base = declarative_base()
# this returns your base class
def get_session():
    session = LocalSession()
    print("Connected....")
    return session