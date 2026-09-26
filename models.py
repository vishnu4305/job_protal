from database import Base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey

# create table tablename (col datatypes );
# to create a column in ORM we create a col object using Column
# default, notnull, unique, check, primaryKey, autoincrement


class Candidate(Base): # Create a SQLAlchemy ORM model called Candidate.
    __tablename__ = "candidates" #This Python class represents the existing MySQL candidates table.

    candidate_id = Column(Integer, primary_key=True, autoincrement=True) 
    full_name = Column(String(100), nullable=False) 
    username = Column(String(50), nullable=False, unique=True) 
    password = Column(String(255), nullable=False) 
    email = Column(String(100), nullable=False, unique=True) 
    phone = Column(String(15)) 
    skills = Column(String(255)) 
    experience_years = Column(Integer, default=0) 
    registered_on = Column( TIMESTAMP, server_default="CURRENT_TIMESTAMP" )

# Represents the employees table 
class Employee(Base):
    __tablename__ = "employees" 
    employee_id = Column( Integer, primary_key=True, autoincrement=True )
    company_name = Column( String(100), nullable=False ) 
    username = Column( String(50), nullable=False, unique=True ) 
    password = Column( String(255), nullable=False ) 
    email = Column( String(100), nullable=False, unique=True ) 
    phone = Column( String(15) )


class Job(Base):
    """Represents the jobs table."""
    __tablename__ = "jobs"
    
    job_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    title = Column(String(150), nullable=False)
    description = Column(Text)
    location = Column(String(100))
    job_type = Column(String(50), default="Full Time")
    salary = Column(String(20))
    status = Column(String(10), default="Open")
    posted_on = Column(TIMESTAMP, server_default="current_timestamp")


class Application(Base):
    """Represents the applications table."""
    __tablename__ = "applications"
    
    application_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    status = Column(String(50), default="Not Applied")
    applied_on = Column(TIMESTAMP, server_default="current_timestamp")
