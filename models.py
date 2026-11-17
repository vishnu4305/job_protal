from database import Base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Date

class Candidate(Base): # Create a SQLAlchemy ORM model called Candidate.
    __tablename__ = "candidates" 
    candidate_id = Column(Integer, primary_key=True, autoincrement=True) 
    full_name = Column(String(100), nullable=False) 
    username = Column(String(50), nullable=False, unique=True) 
    password = Column(String(255), nullable=False) 
    email = Column(String(100), nullable=False, unique=True) 
    phone = Column(String(15)) 
    skills = Column(String(255)) 
    experience_years = Column(Integer, default=0) 
    registered_on = Column( TIMESTAMP, server_default="CURRENT_TIMESTAMP" )

class Employee(Base):
    __tablename__ = "employees" 
    employee_id = Column( Integer, primary_key=True, autoincrement=True )
    company_name = Column( String(100), nullable=False ) 
    username = Column( String(50), nullable=False, unique=True ) 
    password = Column( String(255), nullable=False ) 
    email = Column( String(100), nullable=False, unique=True ) 
    phone = Column( String(15) )

class Job(Base):
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
    __tablename__ = "applications"
    application_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    status = Column(String(50), default="Not Applied")
    applied_on = Column(TIMESTAMP, server_default="current_timestamp")

class TrackedJob(Base):
    __tablename__ = "tracked_jobs"
    tracked_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=True)   # NULL for external jobs
    company = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    source = Column(String(50), default="Manual")     
    status = Column(String(20), nullable=False, default="Wishlist")
    applied_date = Column(Date)
    notes = Column(String(500))