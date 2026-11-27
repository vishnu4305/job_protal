from database import get_session
from models import *
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import date
from validation import *
from tracker import router as tracker_router, sync_tracker
from pwdlib import PasswordHash

app = FastAPI(title="Job Portal")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# PASSWORD HASHING (Argon2)
password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Return an Argon2 hash for a plain-text password."""
    return password_hasher.hash(password)

def verify_password(password: str, stored_password: str) -> bool:
    if stored_password.startswith("$argon2"):
        return password_hasher.verify(password, stored_password)
    return password == stored_password


def is_argon2_hash(stored_password: str) -> bool:
    return stored_password.startswith("$argon2")

def get_cookie_id(request: Request, cookie_name: str):
    value = request.cookies.get(cookie_name)
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None

app.include_router(tracker_router)

class CandidateRequest(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    phone: str
    skills: str
    experience_years: int

class CandidateLoginRequest(BaseModel):
    username: str
    password: str

class EmployeeRequest(BaseModel):
    company_name: str
    username: str
    email: str
    password: str
    phone: str

class EmployeeLoginRequest(BaseModel):
    username: str
    password: str

class JobRequest(BaseModel):
    employee_id: int
    title: str
    description: str
    location: str
    job_type: str
    salary: str

class ApplicationRequest(BaseModel):
    candidate_id: int
    job_id: int

class ApplicationStatusRequest(BaseModel):
    employee_id: int
    application_id: int
    status: str

@app.get("/")
def home(request: Request):
    session = get_session()
    try:
        jobs = session.query(
            Job, Employee.company_name
        ).join(Employee, Job.employee_id == Employee.employee_id).filter(
            Job.status == "Open"
        ).order_by(Job.posted_on.desc()).limit(6).all()
        return templates.TemplateResponse(
            request=request, name="index.html",
            context={
                "jobs": jobs,
                "total_jobs": session.query(Job).filter(Job.status == "Open").count(),
                "total_candidates": session.query(Candidate).count(),
                "total_companies": session.query(Employee).count(),
            }
        )
    finally:
        session.close()

@app.post("/register_candidate")
def register_candidate(req: CandidateRequest):
    full_name = req.full_name.strip()
    username = req.username.strip()
    email = req.email.strip()
    password = req.password.strip()
    phone = req.phone.strip()
    skills = req.skills.strip()
    experience_years = req.experience_years
    if full_name == "":    # Check full name
        return {"message": "Full name cannot be empty" }
    if username == "":     # Check username
        return {"message": "Username cannot be empty"}
    if not is_valid_email(email):# Check email
        return {"message": "Invalid email format"}
    if not is_valid_phone(phone):# Check phone
        return { "message": "Phone number must be exactly 10 digits"}
    if not is_valid_password(password):# Check password
        return { "message": "Password must contain at least 8 characters, one letter and one number"}
    if skills == "":   # Check skills
        return { "message": "Skills cannot be empty"}
    if experience_years < 0:# Check experience
        return { "message": "Experience cannot be negative"}
    session = get_session()

    
    existing_candidate = session.query(Candidate).filter(Candidate.username == username).first()
    if existing_candidate:
        session.close()
        return {
            "message": "Username already exists"
        }
    existing_candidate = session.query(Candidate).filter(Candidate.email == email).first()
    if existing_candidate:
        session.close()
        return {"message": "Email already exists"}
    candidate = Candidate(
        full_name=full_name,
        username=username,
        password=hash_password(password),
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
    if username == "":
        return {"message": "Username cannot be empty"}
    if password == "":
        return {"message": "Password cannot be empty"}
    session = get_session()
    user = session.query(Candidate).filter(Candidate.username == username).first()
    if not user or not verify_password(password, user.password):
        user = None
    if user:
        if not is_argon2_hash(user.password):
            user.password = hash_password(password)
            session.commit()
        response_data = {
            "message": f"Welcome, {user.full_name}!",
            "candidate_id": user.candidate_id,
            "full_name": user.full_name
        }
    else:
        response_data = None
    session.close()
    if response_data:
        return response_data
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
    if company_name == "":
        return {"message": "Company name cannot be empty"}
    if username == "":
        return { "message": "Username cannot be empty"}
    if not is_valid_email(email):
        return {"message": "Invalid email format" }
    if not is_valid_phone(phone):
        return {"message": "Phone number must be exactly 10 digits"}
    if not is_valid_password(password):
        return {
            "message": (
                "Password must contain at least "
                "8 characters, one letter and one number"
            )
        }
    session = get_session()
    existing_employee = session.query(Employee).filter(Employee.username == username).first()
    if existing_employee:
        session.close()
        return {
            "message": "Username already exists"
        }
    existing_employee = session.query(Employee).filter(Employee.email == email).first()
    if existing_employee:
        session.close()
        return {
            "message": "Email already exists"
        }
    employee = Employee(
        company_name=company_name,
        username=username,
        password=hash_password(password),
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
    if username == "":
        return {
            "message": "Username cannot be empty"
        }
    if password == "":
        return {
            "message": "Password cannot be empty"
        }
    session = get_session()
    user = session.query(Employee).filter(Employee.username == username).first()
    if not user or not verify_password(password, user.password):
        user = None
    if user:
        if not is_argon2_hash(user.password):
            user.password = hash_password(password)
            session.commit()
        response_data = {
            "message": f"Welcome, {user.company_name}!",
            "employee_id": user.employee_id,
            "company_name": user.company_name
        }
    else:
        response_data = None
    session.close()
    if response_data:
        return response_data
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
    if title == "":
        return {
            "message": "Job title cannot be empty"
        }
    if description == "":
        return {
            "message": "Job description cannot be empty"
        }
    if location == "":
        return {
            "message": "Location cannot be empty"
        }
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
    if salary == "":
        return {
            "message": "Salary cannot be empty"
        }
    session = get_session()
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
    if sort_by == "title":
        jobs = session.query(
            Job.job_id,
            Job.title,
            Employee.company_name,
            Job.location,
            Job.job_type,
            Job.salary
        ).join(Employee,Job.employee_id == Employee.employee_id).filter(Job.status == "Open").order_by(Job.title.asc()).all()
    else:
        jobs = session.query(
            Job.job_id,
            Job.title,
            Employee.company_name,
            Job.location,
            Job.job_type,
            Job.salary
        ).join(Employee, Job.employee_id == Employee.employee_id).filter(Job.status == "Open").order_by(Job.posted_on.desc()).all()
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
    candidate = session.query(Candidate ).filter( Candidate.candidate_id == candidate_id).first()
    if not candidate:
        session.close()
        return {
            "message": "Candidate not found"
        }
    job = session.query( Job ).filter(
        Job.job_id == job_id,
        Job.status == "Open"
    ).first()
    if not job:
        session.close()
        return {
            "message": "Job not found."
        }
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
    application = Application(
        job_id=job_id,
        candidate_id=candidate_id,
        status="Applied"
    )
    session.add(application)
    sync_tracker(session, candidate_id, job_id, "Applied")
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
    job = session.query(Job).filter(Job.job_id == job_id,Job.employee_id == employee_id).first()
    if not job:
        session.close()
        return {
            "message": "This job does not belong to your company."
        }
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
    if new_status not in valid_statuses:
        return {
            "message": (
                "Invalid status. "
                "Use Applied, Shortlisted, "
                "Rejected or Hired."
            )
        }
    session = get_session()
    application = session.query(Application).join(Job, Application.job_id == Job.job_id).filter(
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
    application.status = new_status
    sync_tracker(session, application.candidate_id, application.job_id, new_status)
    session.commit()
    session.close()
    return {
        "message": "Application status updated successfully!"
    }

#HTML FRONTEND ROUTES
@app.get("/jobs")
def jobs_page(request: Request, keyword: str = "", location: str = "", job_type: str = "", company: str = ""):
    session = get_session()
    try:
        query = session.query(Job, Employee.company_name).join(
            Employee, Job.employee_id == Employee.employee_id
        ).filter(Job.status == "Open")
        if keyword.strip():
            term = f"%{keyword.strip()}%"
            query = query.filter((Job.title.like(term)) | (Job.description.like(term)))
        if location.strip():
            query = query.filter(Job.location.like(f"%{location.strip()}%"))
        if job_type.strip():
            query = query.filter(Job.job_type == job_type.strip())
        if company.strip():
            query = query.filter(Employee.company_name == company.strip())
        jobs = query.order_by(Job.posted_on.desc()).all()
        candidate_id = get_cookie_id(request, "candidate_id")
        applied_job_ids = set()
        saved_job_ids = set()
        if candidate_id:
            applied_job_ids = {row[0] for row in session.query(Application.job_id).filter(
                Application.candidate_id == candidate_id
            ).all()}
            saved_job_ids = {row[0] for row in session.query(TrackedJob.job_id).filter(
                TrackedJob.candidate_id == candidate_id,
                TrackedJob.job_id.isnot(None), TrackedJob.status == "Wishlist"
            ).all()}
        return templates.TemplateResponse(
            request=request, name="jobs.html",
            context={"jobs": jobs, "keyword": keyword, "location": location,
                     "job_type": job_type.strip(), "company": company.strip(),
                     "applied_job_ids": applied_job_ids, "saved_job_ids": saved_job_ids}
        )
    finally:
        session.close()
# CATEGORIES PAGE 
@app.get("/categories")
def categories_page(request: Request):
    session = get_session()
    try:
        rows = session.query(Job.job_type, func.count(Job.job_id)).filter(
            Job.status == "Open"
        ).group_by(Job.job_type).all()
        counts = {job_type: total for job_type, total in rows if job_type}
        names = ["Full Time", "Part Time", "Internship", "Contract"]
        names += sorted(t for t in counts if t not in names)
        categories = [{"name": n, "open_jobs": counts.get(n, 0)} for n in names]
        return templates.TemplateResponse(
            request=request, name="categories.html", context={"categories": categories}
        )
    finally:
        session.close()
@app.get("/companies")
def companies_page(request: Request):
    session = get_session()
    try:
        rows = session.query(
            Employee.company_name, func.count(Job.job_id)
        ).outerjoin(
            Job, (Job.employee_id == Employee.employee_id) & (Job.status == "Open")
        ).group_by(Employee.employee_id, Employee.company_name).all()
        companies = sorted(
            [{"name": name, "open_jobs": total} for name, total in rows],
            key=lambda c: (-c["open_jobs"], c["name"].lower())
        )
        return templates.TemplateResponse(
            request=request, name="companies.html", context={"companies": companies}
        )
    finally:
        session.close()

# ABOUT AND CONTACT PAGES
@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html", context={})

@app.get("/contact")
def contact_page(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html", context={})

@app.get("/job/{job_id}")
def job_details(request: Request, job_id: int, application_message: str = ""):
    session = get_session()
    try:
        result = session.query(Job, Employee.company_name).join(
            Employee, Job.employee_id == Employee.employee_id
        ).filter(Job.job_id == job_id, Job.status == "Open").first()
        if not result:
            return templates.TemplateResponse(
                request=request, name="job_details.html",
                context={"job": None, "message": "Job not found or no longer available."},
                status_code=404
            )
        job, company_name = result
        candidate_id = get_cookie_id(request, "candidate_id")
        already_applied = False
        is_saved = False
        if candidate_id:
            already_applied = session.query(Application).filter(
                Application.job_id == job_id, Application.candidate_id == candidate_id
            ).first() is not None
            is_saved = session.query(TrackedJob).filter(
                TrackedJob.job_id == job_id, TrackedJob.candidate_id == candidate_id,
                TrackedJob.status == "Wishlist"
            ).first() is not None
        return templates.TemplateResponse(
            request=request, name="job_details.html",
            context={"job": job, "company_name": company_name,
                     "message": None, "application_message": application_message,
                     "already_applied": already_applied, "is_saved": is_saved}
        )
    finally:
        session.close()

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"message": None})

@app.post("/register")
def register_candidate_html(
    request: Request,
    full_name: str = Form(...), username: str = Form(...), email: str = Form(...),
    password: str = Form(...), phone: str = Form(...), skills: str = Form(...),
    experience_years: int = Form(0)
):
    session = get_session()
    try:
        full_name, username = full_name.strip(), username.strip()
        email, phone, skills = email.strip(), phone.strip(), skills.strip()
        message = None
        if not full_name or not username or not skills:
            message = "Please complete all required fields."
        elif not is_valid_email(email):
            message = "Invalid email address."
        elif not is_valid_phone(phone):
            message = "Phone number must contain exactly 10 digits."
        elif not is_valid_password(password):
            message = "Password must contain at least 8 characters, one letter and one number."
        elif experience_years < 0:
            message = "Experience cannot be negative."
        elif session.query(Candidate).filter(Candidate.username == username).first():
            message = "Username already exists."
        elif session.query(Candidate).filter(Candidate.email == email).first():
            message = "Email already exists."
        if message:
            return templates.TemplateResponse(request=request, name="register.html", context={"message": message}, status_code=400)
        candidate = Candidate(
            full_name=full_name, username=username, email=email,
            password=hash_password(password), phone=phone, skills=skills,
            experience_years=experience_years
        )
        session.add(candidate)
        session.commit()
        return RedirectResponse("/login?registered=1", status_code=303)
    finally:
        session.close()

@app.get("/login")
def candidate_login_page(request: Request):
    if request.query_params.get("registered"):
        message = "Registration successful. Please log in."
    elif request.query_params.get("reset"):
        message = "Password updated successfully. Please log in."
    else:
        message = None
    return templates.TemplateResponse(request=request, name="login.html", context={"message": message})

@app.post("/login")
def candidate_login_html(request: Request, username: str = Form(...), password: str = Form(...)):
    session = get_session()
    try:
        candidate = session.query(Candidate).filter(Candidate.username == username.strip()).first()
        if not candidate or not verify_password(password, candidate.password):
            return templates.TemplateResponse(request=request, name="login.html", context={"message": "Invalid username or password."}, status_code=401)
        if not is_argon2_hash(candidate.password):
            candidate.password = hash_password(password)
            session.commit()
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(
            key="candidate_id",
            value=str(candidate.candidate_id),
        )
        return response
    finally:
        session.close()

@app.get("/logout")
def candidate_logout(request: Request):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("candidate_id")
    return response

@app.get("/dashboard")
def candidate_dashboard(request: Request):
    candidate_id = get_cookie_id(request, "candidate_id")
    if not candidate_id:
        return RedirectResponse("/login", status_code=303)
    session = get_session()
    try:
        candidate = session.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        if not candidate:
            return RedirectResponse("/login", status_code=303)
        applications = session.query(
            Application, Job.title, Job.location, Job.salary, Employee.company_name
        ).join(Job, Application.job_id == Job.job_id).join(
            Employee, Job.employee_id == Employee.employee_id
        ).filter(Application.candidate_id == candidate_id).order_by(Application.applied_on.desc()).all()
        tracked_jobs = session.query(TrackedJob).filter(
            TrackedJob.candidate_id == candidate_id
        ).order_by(TrackedJob.tracked_id.desc()).all()
        tracker_summary = {"Wishlist": 0, "Applied": 0, "Interview": 0, "Offer": 0, "Rejected": 0}
        for tracked in tracked_jobs:
            if tracked.status in tracker_summary:
                tracker_summary[tracked.status] += 1
        return templates.TemplateResponse(
            request=request, name="dashboard.html",
            context={"candidate": candidate, "applications": applications,
                     "total_applications": len(applications), "tracked_jobs": tracked_jobs,
                     "tracker_summary": tracker_summary, "total_tracked": len(tracked_jobs)}
        )
    finally:
        session.close()

@app.post("/job/{job_id}/apply")
def apply_job_html(request: Request, job_id: int):
    candidate_id = get_cookie_id(request, "candidate_id")
    if not candidate_id:
        return RedirectResponse("/login", status_code=303)
    session = get_session()
    try:
        candidate = session.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        job = session.query(Job).filter(Job.job_id == job_id, Job.status == "Open").first()
        if not candidate or not job:
            return RedirectResponse("/jobs", status_code=303)
        existing = session.query(Application).filter(
            Application.job_id == job_id, Application.candidate_id == candidate_id
        ).first()
        if existing:
            message = "You have already applied for this job."
        else:
            application = Application(job_id=job_id, candidate_id=candidate_id, status="Applied")
            session.add(application)
            sync_tracker(session, candidate_id, job_id, "Applied")
            session.commit()
            message = "Application submitted successfully!"
        from urllib.parse import quote
        return RedirectResponse(f"/job/{job_id}?application_message={quote(message)}", status_code=303)
    finally:
        session.close()
@app.get("/tracker")
def tracker_page(request: Request, status: str = ""):
    candidate_id = get_cookie_id(request, "candidate_id")
    if not candidate_id:
        return RedirectResponse("/login", status_code=303)
    session = get_session()
    try:
        query = session.query(TrackedJob).filter(TrackedJob.candidate_id == candidate_id)
        if status:
            query = query.filter(TrackedJob.status == status)
        tracked_jobs = query.order_by(TrackedJob.tracked_id.desc()).all()
        all_rows = session.query(TrackedJob.status).filter(TrackedJob.candidate_id == candidate_id).all()
        summary = {"Wishlist": 0, "Applied": 0, "Interview": 0, "Offer": 0, "Rejected": 0}
        for (item_status,) in all_rows:
            if item_status in summary:
                summary[item_status] += 1
        return templates.TemplateResponse(
            request=request, name="tracker.html",
            context={"tracked_jobs": tracked_jobs, "summary": summary,
                     "total_tracked": len(all_rows), "selected_status": status,
                     "message": request.query_params.get("message", "")}
        )
    finally:
        session.close()

@app.post("/my-tracker/save/{job_id}")
def save_portal_job(request: Request, job_id: int):
    candidate_id = get_cookie_id(request, "candidate_id")
    if not candidate_id:
        return RedirectResponse("/login", status_code=303)
    session = get_session()
    try:
        candidate = session.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        job = session.query(Job).filter(Job.job_id == job_id, Job.status == "Open").first()
        if not candidate or not job:
            return RedirectResponse("/jobs", status_code=303)
        if session.query(Application).filter(Application.candidate_id == candidate_id, Application.job_id == job_id).first():
            return RedirectResponse("/tracker?message=You+have+already+applied+for+this+job", status_code=303)
        tracked = session.query(TrackedJob).filter(
            TrackedJob.candidate_id == candidate_id, TrackedJob.job_id == job_id
        ).first()
        if tracked:
            session.delete(tracked)
            message = "Job removed from your Wishlist"
        else:
            session.add(TrackedJob(candidate_id=candidate_id, job_id=job_id,
                                   company=session.query(Employee.company_name).filter(Employee.employee_id == job.employee_id).scalar(),
                                   role=job.title, source="Portal", status="Wishlist"))
            message = "Job saved to your Wishlist"
        session.commit()
        return RedirectResponse(f"/jobs?tracker_message={message.replace(' ', '+')}", status_code=303)
    finally:
        session.close()

@app.post("/my-tracker/add-external")
def add_external_tracked_job(request: Request, company: str = Form(...), role: str = Form(...),
                             source: str = Form("Manual"), notes: str = Form("")):
    candidate_id = get_cookie_id(request, "candidate_id")
    if not candidate_id:
        return RedirectResponse("/login", status_code=303)
    company, role = company.strip(), role.strip()
    if not company or not role:
        return RedirectResponse("/tracker?message=Company+and+role+are+required", status_code=303)
    session = get_session()
    try:
        session.add(TrackedJob(candidate_id=candidate_id, company=company, role=role,
                               source=(source.strip() or "Manual"), status="Wishlist", notes=notes.strip() or None))
        session.commit()
        return RedirectResponse("/tracker?message=External+job+added+to+your+tracker", status_code=303)
    finally:
        session.close()

@app.post("/my-tracker/update/{tracked_id}")
def update_tracker_item(request: Request, tracked_id: int, status: str = Form(...), notes: str = Form("")):
    candidate_id = get_cookie_id(request, "candidate_id")
    if not candidate_id:
        return RedirectResponse("/login", status_code=303)
    allowed = {"Wishlist", "Applied", "Interview", "Offer", "Rejected"}
    if status not in allowed:
        return RedirectResponse("/tracker?message=Invalid+status", status_code=303)
    session = get_session()
    try:
        item = session.query(TrackedJob).filter(TrackedJob.tracked_id == tracked_id,
                                                TrackedJob.candidate_id == candidate_id).first()
        if not item:
            return RedirectResponse("/tracker?message=Tracked+job+not+found", status_code=303)
        application = None
        if item.job_id:
            application = session.query(Application).filter(Application.job_id == item.job_id,
                                                              Application.candidate_id == candidate_id).first()
        if item.job_id:
            if application:
                item.status = {"Applied": "Applied", "Shortlisted": "Interview", "Rejected": "Rejected", "Hired": "Offer"}.get(application.status, item.status)
            else:
                item.status = "Wishlist"
        else:
            item.status = status
            if status != "Wishlist" and item.applied_date is None:
                item.applied_date = date.today()
        item.notes = notes.strip() or None
        session.commit()
        return RedirectResponse("/tracker?message=Tracker+updated", status_code=303)
    finally:
        session.close()

@app.post("/my-tracker/delete/{tracked_id}")
def delete_tracker_item(request: Request, tracked_id: int):
    candidate_id = get_cookie_id(request, "candidate_id")
    if not candidate_id:
        return RedirectResponse("/login", status_code=303)
    session = get_session()
    try:
        item = session.query(TrackedJob).filter(TrackedJob.tracked_id == tracked_id, TrackedJob.candidate_id == candidate_id).first()
        if item:
            session.delete(item)
            session.commit()
        return RedirectResponse("/tracker?message=Tracker+item+removed", status_code=303)
    finally:
        session.close()

@app.get("/employer/register")
def employer_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="employee_register.html", context={"message": None})

@app.post("/employer/register")
def employer_register_html(
    request: Request, company_name: str = Form(...), username: str = Form(...),
    email: str = Form(...), password: str = Form(...), phone: str = Form(...)
):
    session = get_session()
    try:
        company_name, username, email, phone = company_name.strip(), username.strip(), email.strip(), phone.strip()
        message = None
        if not company_name or not username:
            message = "Company name and username are required."
        elif not is_valid_email(email):
            message = "Invalid email address."
        elif not is_valid_phone(phone):
            message = "Phone number must contain exactly 10 digits."
        elif not is_valid_password(password):
            message = "Password must contain at least 8 characters, one letter and one number."
        elif session.query(Employee).filter(Employee.username == username).first():
            message = "Username already exists."
        elif session.query(Employee).filter(Employee.email == email).first():
            message = "Email already exists."
        if message:
            return templates.TemplateResponse(request=request, name="employee_register.html", context={"message": message}, status_code=400)
        employee = Employee(company_name=company_name, username=username, email=email,
                            password=hash_password(password), phone=phone)
        session.add(employee)
        session.commit()
        return RedirectResponse("/employer/login?registered=1", status_code=303)
    finally:
        session.close()

@app.get("/employer/login")
def employer_login_page(request: Request):
    if request.query_params.get("registered"):
        message = "Company registered successfully. Please log in."
    elif request.query_params.get("reset"):
        message = "Password updated successfully. Please log in."
    else:
        message = None
    return templates.TemplateResponse(request=request, name="employee_login.html", context={"message": message})

@app.post("/employer/login")
def employer_login_html(request: Request, username: str = Form(...), password: str = Form(...)):
    session = get_session()
    try:
        employee = session.query(Employee).filter(Employee.username == username.strip()).first()
        if not employee or not verify_password(password, employee.password):
            return templates.TemplateResponse(request=request, name="employee_login.html", context={"message": "Invalid username or password."}, status_code=401)
        if not is_argon2_hash(employee.password):
            employee.password = hash_password(password)
            session.commit()
        response = RedirectResponse("/employer/dashboard", status_code=303)
        response.set_cookie(
            key="employee_id",
            value=str(employee.employee_id),
            httponly=True,
            samesite="lax"
        )
        return response
    finally:
        session.close()

@app.get("/employer/logout")
def employer_logout(request: Request):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("employee_id")
    return response

@app.get("/forgot-password")
def forgot_password_page(request: Request):
    role = request.query_params.get("role", "candidate")
    if role not in ("candidate", "employer"):
        role = "candidate"
    return templates.TemplateResponse(
        request=request, name="forgot_password.html",
        context={"message": None, "role": role}
    )

@app.post("/forgot-password")
def reset_password_without_otp(
    request: Request,
    role: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    role = role.strip().lower()
    username = username.strip()
    email = email.strip().lower()
    message = None
    if role not in ("candidate", "employer"):
        message = "Please select a valid account type."
    elif not is_valid_email(email):
        message = "Please enter a valid email address."
    elif not is_valid_password(new_password):
        message = "Password must contain at least 8 characters, one letter and one number."
    elif new_password != confirm_password:
        message = "New password and confirm password do not match."
    if message:
        return templates.TemplateResponse(
            request=request, name="forgot_password.html",
            context={"message": message, "role": role}, status_code=400
        )

    session = get_session()
    try:
        if role == "candidate":
            account = session.query(Candidate).filter(
                Candidate.username == username, Candidate.email == email
            ).first()
            login_url = "/login"
        else:
            account = session.query(Employee).filter(
                Employee.username == username, Employee.email == email
            ).first()
            login_url = "/employer/login"
        if not account:
            return templates.TemplateResponse(
                request=request, name="forgot_password.html",
                context={"message": "No account found with that username and email.", "role": role},
                status_code=404
            )
        account.password = hash_password(new_password)
        session.commit()
        return RedirectResponse(f"{login_url}?reset=1", status_code=303)
    finally:
        session.close()

@app.get("/employer/dashboard")
def employer_dashboard(request: Request):
    employee_id = get_cookie_id(request, "employee_id")
    if not employee_id:
        return RedirectResponse("/employer/login", status_code=303)
    session = get_session()
    try:
        employee = session.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not employee:
            return RedirectResponse("/employer/login", status_code=303)
        jobs = session.query(Job).filter(Job.employee_id == employee_id).order_by(Job.posted_on.desc()).all()
        total_applications = session.query(Application).join(Job, Application.job_id == Job.job_id).filter(Job.employee_id == employee_id).count()
        return templates.TemplateResponse(
            request=request, name="employer_dashboard.html",
            context={"employee": employee, "jobs": jobs, "total_jobs": len(jobs),
                     "total_applications": total_applications}
        )
    finally:
        session.close()

@app.get("/employer/post-job")
def post_job_page(request: Request):
    if not get_cookie_id(request, "employee_id"):
        return RedirectResponse("/employer/login", status_code=303)
    return templates.TemplateResponse(request=request, name="post_job.html", context={"message": None})

@app.post("/employer/post-job")
def create_job_html(
    request: Request, title: str = Form(...), description: str = Form(...),
    location: str = Form(...), job_type: str = Form(...), salary: str = Form(...)
):
    employee_id = get_cookie_id(request, "employee_id")
    if not employee_id:
        return RedirectResponse("/employer/login", status_code=303)
    if not is_valid_choice(job_type, ["Full Time", "Part Time", "Internship", "Contract"]):
        return templates.TemplateResponse(request=request, name="post_job.html", context={"message": "Invalid job type."}, status_code=400)
    session = get_session()
    try:
        job = Job(employee_id=employee_id, title=title.strip(), description=description.strip(),
                  location=location.strip(), job_type=job_type, salary=salary.strip())
        session.add(job)
        session.commit()
        return RedirectResponse("/employer/dashboard", status_code=303)
    finally:
        session.close()

@app.get("/employer/job/{job_id}/applications")
def employer_applications(request: Request, job_id: int):
    employee_id = get_cookie_id(request, "employee_id")
    if not employee_id:
        return RedirectResponse("/employer/login", status_code=303)
    session = get_session()
    try:
        job = session.query(Job).filter(Job.job_id == job_id, Job.employee_id == employee_id).first()
        if not job:
            return RedirectResponse("/employer/dashboard", status_code=303)
        applications = session.query(Application, Candidate).join(
            Candidate, Application.candidate_id == Candidate.candidate_id
        ).filter(Application.job_id == job_id).order_by(Application.applied_on.desc()).all()
        return templates.TemplateResponse(request=request, name="employer_applications.html",
                                          context={"job": job, "applications": applications})
    finally:
        session.close()

@app.post("/employer/application/{application_id}/status")
def update_employer_application_status(request: Request, application_id: int, status: str = Form(...)):
    employee_id = get_cookie_id(request, "employee_id")
    if not employee_id:
        return RedirectResponse("/employer/login", status_code=303)
    if status not in ["Applied", "Shortlisted", "Rejected", "Hired"]:
        return RedirectResponse("/employer/dashboard", status_code=303)
    session = get_session()
    try:
        application = session.query(Application).join(Job, Application.job_id == Job.job_id).filter(
            Application.application_id == application_id, Job.employee_id == employee_id
        ).first()
        if not application:
            return RedirectResponse("/employer/dashboard", status_code=303)
        application.status = status
        sync_tracker(session, application.candidate_id, application.job_id, status)
        session.commit()
        return RedirectResponse(f"/employer/job/{application.job_id}/applications", status_code=303)
    finally:
        session.close()