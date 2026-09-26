from database import get_session
from models import *
from fastapi import FastAPI
from pydantic import BaseModel
from validation import *


app = FastAPI()


# # PYDANTIC MODELS
# #---------------------------------------------------------------------------------------------------
# # Candidate registration request
# class CandidateRequest(BaseModel):
#     full_name: str
#     username: str
#     email: str
#     password: str
#     phone: str
#     skills: str
#     experience_years: int


# # Candidate login request
# class CandidateLoginRequest(BaseModel):
#     username: str
#     password: str


# # Employee registration request
# class EmployeeRequest(BaseModel):
#     company_name: str
#     username: str
#     email: str
#     password: str
#     phone: str


# # Employee login request
# class EmployeeLoginRequest(BaseModel):
#     username: str
#     password: str


# # Job request
# class JobRequest(BaseModel):
#     employee_id: int
#     title: str
#     description: str
#     location: str
#     job_type: str
#     salary: str


# # Apply job request
# class ApplicationRequest(BaseModel):
#     candidate_id: int
#     job_id: int


# # Update application status request
# class ApplicationStatusRequest(BaseModel):
#     employee_id: int
#     application_id: int
#     status: str

#---------------------------------------------------------------------------------------------------
# Home Page

@app.get("/")
def home():

    return {
        "message": "This is home page"
    }


# CANDIDATE REGISTER PAGE

@app.post("/register_candidate")
def register_candidate(req: CandidateRequest):

    full_name = req.full_name.strip()
    username = req.username.strip()
    email = req.email.strip()
    password = req.password.strip()
    phone = req.phone.strip()
    skills = req.skills.strip()
    experience_years = req.experience_years

    # Check full name
    if full_name == "":
        return {"message": "Full name cannot be empty" }

    # Check username
    if username == "":
        return {"message": "Username cannot be empty"}

    # Check email
    if not is_valid_email(email):
        return {"message": "Invalid email format"}

    # Check phone
    if not is_valid_phone(phone):
        return { "message": "Phone number must be exactly 10 digits"}

    # Check password
    if not is_valid_password(password):
        return {
            "message": "Password must contain at least 8 characters, one letter and one number"
        }

    # Check skills
    if skills == "":
        return { "message": "Skills cannot be empty"}

    # Check experience
    if experience_years < 0:
        return {
            "message": "Experience cannot be negative"
        }

    session = get_session()

    # Check username
    existing_candidate = session.query(Candidate).filter(Candidate.username == username).first()

    if existing_candidate:
        session.close()
        return {
            "message": "Username already exists"
        }

    # Check email
    existing_candidate = session.query(Candidate).filter(Candidate.email == email).first()
    if existing_candidate:
        session.close()
        return {
            "message": "Email already exists"
        }

    # Create candidate
    candidate = Candidate(
        full_name=full_name,
        username=username,
        password=password,
        email=email,
        phone=phone,
        skills=skills,
        experience_years=experience_years
    )

    session.add(candidate)
    session.commit()

    candidate_id = candidate.candidate_id

    session.close()

    return {
        "message": "Candidate registered successfully",
        "candidate_id": candidate_id
    }


# CANDIDATE LOGIN

@app.post("/login_candidate")
def login_candidate(req: CandidateLoginRequest):

    username = req.username.strip()
    password = req.password.strip()

    # Check username
    if username == "":
        return {
            "message": "Username cannot be empty"
        }

    # Check password
    if password == "":
        return {
            "message": "Password cannot be empty"
        }

    session = get_session()

    # Find candidate
    user = session.query(
        Candidate
    ).filter(
        Candidate.username == username,
        Candidate.password == password
    ).first()

    session.close()

    if user:

        return {
            "message": f"Welcome, {user.full_name}!",
            "candidate_id": user.candidate_id,
            "full_name": user.full_name
        }

    return {
        "message": "Invalid username or password."
    }


# EMPLOYEE REGISTER

@app.post("/register_employee")
def register_employee(req: EmployeeRequest):

    company_name = req.company_name.strip()
    username = req.username.strip()
    email = req.email.strip()
    password = req.password.strip()
    phone = req.phone.strip()

    # Check company name
    if company_name == "":
        return {
            "message": "Company name cannot be empty"
        }

    # Check username
    if username == "":
        return { "message": "Username cannot be empty"}

    # Check email
    if not is_valid_email(email):
        return {
            "message": "Invalid email format"
        }

    # Check phone
    if not is_valid_phone(phone):
        return {
            "message": "Phone number must be exactly 10 digits"
        }

    # Check password
    if not is_valid_password(password):
        return {
            "message": (
                "Password must contain at least "
                "8 characters, one letter and one number"
            )
        }

    session = get_session()

    # Check username
    existing_employee = session.query(
        Employee
    ).filter(
        Employee.username == username
    ).first()

    if existing_employee:

        session.close()

        return {
            "message": "Username already exists"
        }

    # Check email
    existing_employee = session.query(
        Employee
    ).filter(
        Employee.email == email
    ).first()

    if existing_employee:

        session.close()

        return {
            "message": "Email already exists"
        }

    # Create employee
    employee = Employee(
        company_name=company_name,
        username=username,
        password=password,
        email=email,
        phone=phone
    )

    session.add(employee)
    session.commit()

    employee_id = employee.employee_id

    session.close()

    return {
        "message": "Employer registered successfully",
        "employee_id": employee_id
    }


# EMPLOYEE LOGIN

@app.post("/login_employee")
def login_employee(req: EmployeeLoginRequest):

    username = req.username.strip()
    password = req.password.strip()

    # Check username
    if username == "":
        return {
            "message": "Username cannot be empty"
        }

    # Check password
    if password == "":
        return {
            "message": "Password cannot be empty"
        }

    session = get_session()

    # Find employee
    user = session.query(
        Employee
    ).filter(
        Employee.username == username,
        Employee.password == password
    ).first()

    session.close()

    if user:

        return {
            "message": f"Welcome, {user.company_name}!",
            "employee_id": user.employee_id,
            "company_name": user.company_name
        }

    return {
        "message": "Invalid username or password."
    }


# ADD JOB

@app.post("/add_job")
def add_job(req: JobRequest):

    employee_id = req.employee_id
    title = req.title.strip()
    description = req.description.strip()
    location = req.location.strip()
    job_type = req.job_type.strip()
    salary = req.salary.strip()

    # Check title
    if title == "":
        return {
            "message": "Job title cannot be empty"
        }

    # Check description
    if description == "":
        return {
            "message": "Job description cannot be empty"
        }

    # Check location
    if location == "":
        return {
            "message": "Location cannot be empty"
        }

    # Check job type
    valid_job_types = [
        "Full Time",
        "Part Time",
        "Internship",
        "Contract"
    ]

    if job_type not in valid_job_types:
        return {
            "message": "Invalid job type"
        }

    # Check salary
    if salary == "":
        return {
            "message": "Salary cannot be empty"
        }

    session = get_session()

    # Check employee
    employee = session.query(
        Employee
    ).filter(
        Employee.employee_id == employee_id
    ).first()

    if not employee:

        session.close()

        return {
            "message": "Employee not found"
        }

    # Create job
    job = Job(
        employee_id=employee_id,
        title=title,
        description=description,
        location=location,
        job_type=job_type,
        salary=salary
    )

    session.add(job)
    session.commit()

    job_id = job.job_id

    session.close()

    return {
        "message": "Job added successfully",
        "job_id": job_id
    }


# VIEW JOBS

@app.get("/view_jobs")
def view_jobs():

    session = get_session()

    jobs = session.query(
        Job.job_id,
        Job.title,
        Employee.company_name,
        Job.location,
        Job.job_type,
        Job.salary
    ).join(
        Employee,
        Job.employee_id == Employee.employee_id
    ).filter(
        Job.status == "Open"
    ).order_by(
        Job.posted_on.desc()
    ).all()

    session.close()

    if not jobs:
        return {
            "message": "No jobs available."
        }

    result = []

    for job in jobs:

        result.append({
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company_name,
            "location": job.location,
            "job_type": job.job_type,
            "salary": job.salary
        })

    return {
        "jobs": result
    }


# SEARCH JOBS

@app.get("/search_jobs")
def search_jobs(keyword: str):

    keyword = keyword.strip()

    if keyword == "":
        return {
            "message": "Search keyword cannot be empty"
        }

    # Example:
    # keyword = "python"
    # search_value = "%python%"
    #
    # This can match:
    # Python Developer
    # Senior Python Developer
    # Python Backend Developer

    search_value = f"%{keyword}%"

    session = get_session()

    jobs = session.query(
        Job.job_id,
        Job.title,
        Employee.company_name,
        Job.location,
        Job.job_type,
        Job.salary
    ).join(
        Employee,
        Job.employee_id == Employee.employee_id
    ).filter(
        Job.status == "Open"
    ).filter(
        (Job.title.like(search_value)) |
        (Job.location.like(search_value)) |
        (Job.description.like(search_value))
    ).all()

    session.close()

    if not jobs:
        return {
            "message": "No matching jobs found."
        }

    result = []

    for job in jobs:

        result.append({
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company_name,
            "location": job.location,
            "job_type": job.job_type,
            "salary": job.salary
        })

    return {
        "jobs": result
    }


# SORT JOBS

@app.get("/sort_jobs")
def sort_jobs(sort_by: str):

    sort_by = sort_by.strip().lower()

    if sort_by not in ["title", "latest"]:
        return {
            "message": "Invalid sort option. Use title or latest."
        }

    session = get_session()

    # Sort jobs alphabetically by title
    if sort_by == "title":

        jobs = session.query(
            Job.job_id,
            Job.title,
            Employee.company_name,
            Job.location,
            Job.job_type,
            Job.salary
        ).join(
            Employee,
            Job.employee_id == Employee.employee_id
        ).filter(
            Job.status == "Open"
        ).order_by(
            Job.title.asc()
        ).all()

    # Sort jobs by latest posted
    else:

        jobs = session.query(
            Job.job_id,
            Job.title,
            Employee.company_name,
            Job.location,
            Job.job_type,
            Job.salary
        ).join(
            Employee,
            Job.employee_id == Employee.employee_id
        ).filter(
            Job.status == "Open"
        ).order_by(
            Job.posted_on.desc()
        ).all()

    session.close()

    if not jobs:
        return {
            "message": "No jobs available."
        }

    result = []

    for job in jobs:

        result.append({
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company_name,
            "location": job.location,
            "job_type": job.job_type,
            "salary": job.salary
        })

    return {
        "jobs": result
    }


# APPLY FOR JOB

@app.post("/apply_for_job")
def apply_for_job(req: ApplicationRequest):

    candidate_id = req.candidate_id
    job_id = req.job_id

    session = get_session()

    # Check candidate
    candidate = session.query(
        Candidate
    ).filter(
        Candidate.candidate_id == candidate_id
    ).first()

    if not candidate:

        session.close()

        return {
            "message": "Candidate not found"
        }

    # Check job
    job = session.query(
        Job
    ).filter(
        Job.job_id == job_id,
        Job.status == "Open"
    ).first()

    if not job:

        session.close()

        return {
            "message": "Job not found."
        }

    # Check whether candidate already applied
    existing_application = session.query(
        Application
    ).filter(
        Application.job_id == job_id,
        Application.candidate_id == candidate_id
    ).first()

    if existing_application:

        session.close()

        return {
            "message": "You have already applied for this job."
        }

    # Create application
    application = Application(
        job_id=job_id,
        candidate_id=candidate_id,
        status="Applied"
    )

    session.add(application)
    session.commit()

    application_id = application.application_id

    session.close()

    return {
        "message": "Application submitted successfully!",
        "application_id": application_id
    }


# VIEW MY APPLICATIONS

@app.get("/my_applications")
def view_my_applications(candidate_id: int):

    session = get_session()

    applications = session.query(
        Application.application_id,
        Job.title,
        Employee.company_name,
        Job.location,
        Application.status,
        Application.applied_on
    ).join(
        Job,
        Application.job_id == Job.job_id
    ).join(
        Employee,
        Job.employee_id == Employee.employee_id
    ).filter(
        Application.candidate_id == candidate_id
    ).order_by(
        Application.applied_on.desc()
    ).all()

    session.close()

    if not applications:

        return {
            "message": "You have not applied for any jobs."
        }

    result = []

    for application in applications:

        result.append({
            "application_id": application.application_id,
            "job": application.title,
            "company": application.company_name,
            "location": application.location,
            "status": application.status,
            "applied_on": application.applied_on
        })

    return {
        "applications": result
    }


# VIEW APPLICATIONS FOR EMPLOYER

@app.get("/view_applications")
def view_applications(
    employee_id: int,
    job_id: int
):

    session = get_session()

    # Check whether the job belongs to this employee
    job = session.query(Job).filter(Job.job_id == job_id,Job.employee_id == employee_id).first()
    if not job:
        session.close()
        return {
            "message": "This job does not belong to your company."
        }

    # Get applications for the selected job
    applications = session.query(
        Application.application_id,
        Candidate.full_name,
        Candidate.email,
        Candidate.phone,
        Candidate.skills,
        Candidate.experience_years,
        Application.status,
        Application.applied_on
    ).join(
        Candidate,
        Application.candidate_id == Candidate.candidate_id
    ).filter(
        Application.job_id == job_id
    ).all()

    session.close()

    if not applications:

        return {
            "message": "No applications found."
        }

    result = []

    for application in applications:

        result.append({
            "application_id": application.application_id,
            "candidate": application.full_name,
            "email": application.email,
            "phone": application.phone,
            "skills": application.skills,
            "experience": application.experience_years,
            "status": application.status,
            "applied_on": application.applied_on
        })

    return {
        "applications": result
    }


# UPDATE APPLICATION STATUS

@app.put("/update_application_status")
def update_application_status(
    req: ApplicationStatusRequest
):

    application_id = req.application_id
    employee_id = req.employee_id
    new_status = req.status.strip()

    valid_statuses = [
        "Applied",
        "Shortlisted",
        "Rejected",
        "Hired"
    ]

    # Check application status
    if new_status not in valid_statuses:

        return {
            "message": (
                "Invalid status. "
                "Use Applied, Shortlisted, "
                "Rejected or Hired."
            )
        }

    session = get_session()

    # Find application belonging to this employee
    application = session.query(
        Application
    ).join(
        Job,
        Application.job_id == Job.job_id
    ).filter(
        Application.application_id == application_id,
        Job.employee_id == employee_id
    ).first()

    if not application:

        session.close()

        return {
            "message": (
                "Application not found "
                "or does not belong to you."
            )
        }

    # Update application status
    application.status = new_status

    # Save changes
    session.commit()

    session.close()

    return {
        "message": "Application status updated successfully!"
    }

#Ols code ......................


# def register_candidate():
#     print("\n" + "=" * 15)
#     print("CANDIDATE REGISTRATION")
#     print("=" * 15)
#     name = get_non_empty_input("Full Name: ")
#     username = get_non_empty_input("Username: ")
#     email = get_valid_email("Email: ")
#     password = get_valid_password("Password: ")
#     phone = get_valid_phone("Phone: ")
#     skills = get_non_empty_input("Skills (example: Python, MySQL): ")
#     experience = get_valid_number("Years of Experience: ")

#     # Check username
#     cursor.execute(
#         """
#         SELECT candidate_id
#         FROM candidates
#         WHERE username = %s
#         """,
#         (username,)
#     )

#     if cursor.fetchone():
#         print("\nUsername already exists.")
#         return None
#     # Check email
#     cursor.execute(
#         """
#         SELECT candidate_id
#         FROM candidates
#         WHERE email = %s
#         """,
#         (email,)
#     )
#     if cursor.fetchone():
#         print("\nEmail already exists.")
#         return None
#     # Insert candidate
#     cursor.execute(
#         """
#         INSERT INTO candidates
#         (
#             full_name,
#             username,
#             password,
#             email,
#             phone,
#             skills,
#             experience_years
#         )
#         VALUES
#         (%s, %s, %s, %s, %s, %s, %s)
#         """,
#         (
#             name,
#             username,
#             password,
#             email,
#             phone,
#             skills,
#             int(experience)
#         )
#     )
#     connection.commit()
#     print("\nCandidate registered successfully!")
#     return cursor.lastrowid


# def login_candidate():
#     print("\n" + "=" * 15)
#     print("CANDIDATE LOGIN")
#     print("=" * 15)
#     username = get_non_empty_input("Username: ")
#     password = get_non_empty_input("Password: ")
#     cursor.execute(
#         """
#         SELECT candidate_id, full_name
#         FROM candidates
#         WHERE username = %s
#         AND password = %s
#         """,
#         (username, password)
#     )

#     user = cursor.fetchone()
#     if user:
#         print(f"\nWelcome, {user[1]}!")
#         return user[0]
#     print("\nInvalid username or password.")
#     return None

# def register_employee():
#     print("\n" + "=" * 15)
#     print("EMPLOYER REGISTRATION")
#     print("=" * 15)
#     company_name = get_non_empty_input("Company Name: ")
#     username = get_non_empty_input("Username: ")
#     email = get_valid_email("Company Email: ")
#     password = get_valid_password("Password: ")
#     phone = get_valid_phone("Phone: ")

#     # Check username
#     cursor.execute(
#         """
#         SELECT employee_id
#         FROM employees
#         WHERE username = %s
#         """,
#         (username,)
#     )

#     if cursor.fetchone():
#         print("\nUsername already exists.")
#         return None

#     # Check email
#     cursor.execute(
#         """
#         SELECT employee_id
#         FROM employees
#         WHERE email = %s
#         """,
#         (email,)
#     )

#     if cursor.fetchone():
#         print("\nEmail already exists.")
#         return None

#     # Insert employer
#     cursor.execute(
#         """
#         INSERT INTO employees
#         (
#             company_name,
#             username,
#             password,
#             email,
#             phone
#         )
#         VALUES
#         (%s, %s, %s, %s, %s)
#         """,
#         (
#             company_name,
#             username,
#             password,
#             email,
#             phone
#         )
#     )
#     connection.commit()
#     print("\nEmployer registered successfully!")
#     return cursor.lastrowid


# def login_employee():
#     print("\n" + "=" * 15)
#     print("EMPLOYER LOGIN")
#     print("=" * 15)
#     username = get_non_empty_input("Username: ")
#     password = get_non_empty_input("Password: ")
#     cursor.execute(
#         """
#         SELECT employee_id, company_name
#         FROM employees
#         WHERE username = %s
#         AND password = %s
#         """,
#         (username, password)
#     )
#     user = cursor.fetchone()
#     if user:
#         print(f"\nWelcome, {user[1]}!")
#         return user[0]
#     print("\nInvalid username or password.")
#     return None

# def login_or_register():
#     global current_role
#     while True:
#         print("\n" + "=" * 20)
#         print("JOB PORTAL")
#         print("=" * 20)
#         print("1. Candidate Login")
#         print("2. Candidate Register")
#         print("3. Employer Login")
#         print("4. Employer Register")
#         print("5. Exit")
        
#         choice = input("\nEnter your choice: ").strip()
#         if choice == "1":
#             user_id = login_candidate()
#             if user_id:
#                 current_role = "candidate"
#                 return user_id
#         elif choice == "2":
#             user_id = register_candidate()
#             if user_id:
#                 current_role = "candidate"
#                 return user_id
#         elif choice == "3":
#             user_id = login_employee()
#             if user_id:
#                 current_role = "employee"
#                 return user_id
#         elif choice == "4":
#             user_id = register_employee()
#             if user_id:
#                 current_role = "employee"
#                 return user_id
#         elif choice == "5":
#             return None
#         else:
#             print("\nInvalid choice.")

# def add_job(employee_id):
#     print("\n" + "=" * 15)
#     print("ADD JOB")
#     print("=" * 15)

#     title = get_non_empty_input("Job Title: ")
#     description = get_non_empty_input("Job Description: ")
#     location = get_non_empty_input("Location: ")
#     job_type = get_valid_choice(
#         "Job Type (Full Time/Part Time/Internship/Contract): ",
#         [
#             "Full Time",
#             "Part Time",
#             "Internship",
#             "Contract"
#         ]
#     )

#     salary = get_non_empty_input("Salary (example: 6 LPA): ")
#     cursor.execute(
#         """
#         INSERT INTO jobs
#         (
#             employee_id,
#             title,
#             description,
#             location,
#             job_type,
#             salary
#         )
#         VALUES
#         (%s, %s, %s, %s, %s, %s)
#         """,
#         (
#             employee_id,
#             title,
#             description,
#             location,
#             job_type,
#             salary
#         )
#     )
#     connection.commit()
#     print("\nJob added successfully!")


# def view_jobs():
#     cursor.execute(
#         """
#         SELECT
#             j.job_id,
#             j.title,
#             e.company_name,
#             j.location,
#             j.job_type,
#             j.salary
#         FROM jobs j
#         JOIN employees e
#         ON j.employee_id = e.employee_id
#         WHERE j.status = 'Open'
#         ORDER BY j.posted_on DESC
#         """
#     )
#     jobs = cursor.fetchall()
#     if not jobs:
#         print("\nNo jobs available.")
#         return
#     print("\n" + "=" * 100)
#     print(
#         f"{'ID':<5}"
#         f"{'TITLE':<25}"
#         f"{'COMPANY':<20}"
#         f"{'LOCATION':<15}"
#         f"{'TYPE':<15}"
#         f"SALARY"
#     )
#     print("-" * 100)
#     for job in jobs:
#         print(
#             f"{job[0]:<5}"
#             f"{job[1]:<25}"
#             f"{job[2]:<20}"
#             f"{job[3]:<15}"
#             f"{job[4]:<15}"
#             f"{job[5]}"
#         )
# def search_jobs():
#     keyword = get_non_empty_input(
#         "Search job title/location: "
#     )
#     cursor.execute(
#         """
#         SELECT
#             j.job_id,
#             j.title,
#             e.company_name,
#             j.location,
#             j.job_type,
#             j.salary
#         FROM jobs j
#         JOIN employees e
#         ON j.employee_id = e.employee_id
#         WHERE j.status = 'Open'
#         AND (
#             j.title LIKE %s
#             OR j.location LIKE %s
#             OR j.description LIKE %s
#         )
#         """,
#         (
#             f"%{keyword}%",
#             f"%{keyword}%",
#             f"%{keyword}%"
#         )
#     )
#     jobs = cursor.fetchall()
#     if not jobs:
#         print("\nNo matching jobs found.")
#         return
#     print("\nSearch Results")
#     print("-" * 100)
#     for job in jobs:
#         print(
#             f"ID: {job[0]} | "
#             f"Title: {job[1]} | "
#             f"Company: {job[2]} | "
#             f"Location: {job[3]} | "
#             f"Type: {job[4]} | "
#             f"Salary: {job[5]}"
#         )

# def sort_jobs():
#     print("\nSort Jobs By")
#     print("1. Title")
#     print("2. Latest Posted")
#     choice = input(
#         "Enter choice: "
#     ).strip()
#     if choice == "1":
#         column = "j.title"
#     elif choice == "2":
#         column = "j.posted_on"
#     else:
#         print("\nInvalid choice.")
#         return
#     query = f"""
#         SELECT
#             j.job_id,
#             j.title,
#             e.company_name,
#             j.location,
#             j.job_type,
#             j.salary
#         FROM jobs j
#         JOIN employees e
#         ON j.employee_id = e.employee_id
#         WHERE j.status = 'Open'
#         ORDER BY {column} ASC
#     """
#     cursor.execute(query)
#     jobs = cursor.fetchall()
#     if not jobs:
#         print("\nNo jobs available.")
#         return
#     print("\nSorted Jobs")
#     print("-" * 100)
#     for job in jobs:
#         print(
#             f"ID: {job[0]} | "
#             f"{job[1]} | "
#             f"{job[2]} | "
#             f"{job[3]} | "
#             f"{job[4]} | "
#             f"{job[5]}"
#         )


# def apply_for_job(candidate_id):

#     job_id = get_valid_number("Enter Job ID: ")
#     job_id = int(job_id)
#     # Check job
#     cursor.execute(
#         """
#         SELECT job_id
#         FROM jobs
#         WHERE job_id = %s
#         AND status = 'Open'
#         """,
#         (job_id,)
#     )
#     if not cursor.fetchone():
#         print("\nJob not found.")
#         return

#     # Check duplicate application
#     cursor.execute(
#         """
#         SELECT application_id
#         FROM applications
#         WHERE job_id = %s
#         AND candidate_id = %s
#         """,
#         (job_id,candidate_id)
#     )

#     if cursor.fetchone():
#         print(
#             "\nYou have already applied "
#             "for this job."
#         )
#         return
#     # Insert application
#     cursor.execute(
#         """
#         INSERT INTO applications
#         (
#             job_id,
#             candidate_id,
#             status
#         )
#         VALUES
#         (%s, %s, %s)
#         """,
#         (
#             job_id,
#             candidate_id,
#             "Applied"
#         )
#     )
#     connection.commit()
#     print("\nApplication submitted successfully!")


# def view_my_applications(candidate_id):
#     cursor.execute(
#         """
#         SELECT
#             a.application_id,
#             j.title,
#             e.company_name,
#             j.location,
#             a.status,
#             a.applied_on
#         FROM applications a
#         JOIN jobs j
#         ON a.job_id = j.job_id
#         JOIN employees e
#         ON j.employee_id = e.employee_id
#         WHERE a.candidate_id = %s
#         ORDER BY a.applied_on DESC
#         """,
#         (candidate_id,)
#     )
#     applications = cursor.fetchall()
#     if not applications:
#         print("\nYou have not applied for any jobs.")
#         return
#     print("\nMy Applications")
#     print("-" * 100)
#     for app in applications:
#         print(f"Application ID : {app[0]}")
#         print(f"Job            : {app[1]}")
#         print(f"Company        : {app[2]}")
#         print(f"Location       : {app[3]}")
#         print(f"Status         : {app[4]}")
#         print(f"Applied On     : {app[5]}")
#         print("-" * 100)

# def view_applications(employee_id):
#     job_id = get_valid_number("Enter Job ID: ")
#     job_id = int(job_id)
#     # Check job ownership
#     cursor.execute(
#         """
#         SELECT job_id
#         FROM jobs
#         WHERE job_id = %s
#         AND employee_id = %s
#         """,
#         (job_id,employee_id)
#     )
#     if not cursor.fetchone():
#         print(
#             "\nThis job does not belong "
#             "to your company."
#         )
#         return
#     cursor.execute(
#         """
#         SELECT
#             a.application_id,
#             c.full_name,
#             c.email,
#             c.phone,
#             c.skills,
#             c.experience_years,
#             a.status,
#             a.applied_on
#         FROM applications a
#         JOIN candidates c
#         ON a.candidate_id = c.candidate_id
#         WHERE a.job_id = %s
#         """,
#         (job_id,)
#     )
#     applications = cursor.fetchall()
#     if not applications:
#         print("\nNo applications found.")
#         return
#     print("\nApplications")
#     print("=" * 100)

#     for app in applications:
#         print(f"Application ID : {app[0]}")
#         print(f"Candidate      : {app[1]}")
#         print(f"Email          : {app[2]}")
#         print(f"Phone          : {app[3]}")
#         print(f"Skills         : {app[4]}")
#         print(f"Experience     : {app[5]} years")
#         print(f"Status         : {app[6]}")
#         print(f"Applied On     : {app[7]}")
#         print("-" * 100)
        
        
# def update_application_status(employee_id):

#     application_id = get_valid_number("Enter Application ID: ")
#     application_id = int(application_id)
#     new_status = get_valid_choice(
#         "Status (Applied/Shortlisted/Rejected/Hired): ",
#         ["Applied","Shortlisted","Rejected","Hired"]
#     )
#     # Check application belongs to employer
#     cursor.execute(
#         """
#         SELECT a.application_id
#         FROM applications a
#         JOIN jobs j
#         ON a.job_id = j.job_id
#         WHERE a.application_id = %s
#         AND j.employee_id = %s
#         """,
#         (application_id,employee_id)
#     )
#     if not cursor.fetchone():
#         print(
#             "\nApplication not found "
#             "or does not belong to you.")
#         return
#     cursor.execute(
#         """
#         UPDATE applications SET status = %s WHERE application_id = %s
#         """,
#         (new_status,application_id)
#     )
#     connection.commit()
#     print("\nApplication status updated successfully!")


# def candidate_menu(candidate_id):
#     while True:
#         print("\n" + "=" * 20)
#         print("CANDIDATE MENU")
#         print("=" * 20)

#         print("1. View Jobs")
#         print("2. Search Jobs")
#         print("3. Apply for Job")
#         print("4. Sort Jobs")
#         print("5. View My Applications")
#         print("6. Logout")

#         choice = input("\nEnter choice: ").strip()
#         if choice == "1":
#             view_jobs()
#         elif choice == "2":
#             search_jobs()
#         elif choice == "3":
#             apply_for_job(candidate_id)
#         elif choice == "4":
#             sort_jobs()
#         elif choice == "5":
#             view_my_applications(candidate_id)
#         elif choice == "6":
#             print("\nLogged out.")
#             break
#         else:
#             print("\nInvalid choice.")
# def employer_menu(employee_id):
#     while True:
#         print("\n" + "=" * 20)
#         print("EMPLOYER MENU")
#         print("=" * 20)

#         print("1. Add Job")
#         print("2. View Applications")
#         print("3. Update Application Status")
#         print("4. Logout")
#         choice = input("\nEnter choice: ").strip()
#         if choice == "1":
#             add_job(employee_id)
#         elif choice == "2":
#             view_applications(employee_id)
#         elif choice == "3":
#             update_application_status(employee_id)
#         elif choice == "4":
#             print("\nLogged out.")
#             break
#         else:
#             print("\nInvalid choice.")

# def main():

#     global current_user_id
#     global current_role
#     current_user_id = login_or_register()
#     if current_user_id is None:
#         print("\nThank you for using Job Portal.")
#         return
#     if current_role == "candidate":
#         candidate_menu(current_user_id)
#     elif current_role == "employee":
#         employer_menu(current_user_id)   
#     cursor.close()
#     connection.close()
#     print("\nDatabase connection closed.")

# main()