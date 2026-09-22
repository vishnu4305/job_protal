from database import get_connection
from validation import *

connection = get_connection()
cursor = connection.cursor()
print("\nDatabase connected successfully!")

current_user_id = None
current_role = None

def register_candidate():
    print("\n" + "=" * 15)
    print("CANDIDATE REGISTRATION")
    print("=" * 15)
    name = get_non_empty_input("Full Name: ")
    username = get_non_empty_input("Username: ")
    email = get_valid_email("Email: ")
    password = get_valid_password("Password: ")
    phone = get_valid_phone("Phone: ")
    skills = get_non_empty_input("Skills (example: Python, MySQL): ")
    experience = get_valid_number("Years of Experience: ")

    # Check username
    cursor.execute(
        """
        SELECT candidate_id
        FROM candidates
        WHERE username = %s
        """,
        (username,)
    )

    if cursor.fetchone():
        print("\nUsername already exists.")
        return None
    # Check email
    cursor.execute(
        """
        SELECT candidate_id
        FROM candidates
        WHERE email = %s
        """,
        (email,)
    )
    if cursor.fetchone():
        print("\nEmail already exists.")
        return None
    # Insert candidate
    cursor.execute(
        """
        INSERT INTO candidates
        (
            full_name,
            username,
            password,
            email,
            phone,
            skills,
            experience_years
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            username,
            password,
            email,
            phone,
            skills,
            int(experience)
        )
    )
    connection.commit()
    print("\nCandidate registered successfully!")
    return cursor.lastrowid


def login_candidate():
    print("\n" + "=" * 15)
    print("CANDIDATE LOGIN")
    print("=" * 15)
    username = get_non_empty_input("Username: ")
    password = get_non_empty_input("Password: ")
    cursor.execute(
        """
        SELECT candidate_id, full_name
        FROM candidates
        WHERE username = %s
        AND password = %s
        """,
        (username, password)
    )

    user = cursor.fetchone()
    if user:
        print(f"\nWelcome, {user[1]}!")
        return user[0]
    print("\nInvalid username or password.")
    return None

def register_employee():
    print("\n" + "=" * 15)
    print("EMPLOYER REGISTRATION")
    print("=" * 15)
    company_name = get_non_empty_input("Company Name: ")
    username = get_non_empty_input("Username: ")
    email = get_valid_email("Company Email: ")
    password = get_valid_password("Password: ")
    phone = get_valid_phone("Phone: ")

    # Check username
    cursor.execute(
        """
        SELECT employee_id
        FROM employees
        WHERE username = %s
        """,
        (username,)
    )

    if cursor.fetchone():
        print("\nUsername already exists.")
        return None

    # Check email
    cursor.execute(
        """
        SELECT employee_id
        FROM employees
        WHERE email = %s
        """,
        (email,)
    )

    if cursor.fetchone():
        print("\nEmail already exists.")
        return None

    # Insert employer
    cursor.execute(
        """
        INSERT INTO employees
        (
            company_name,
            username,
            password,
            email,
            phone
        )
        VALUES
        (%s, %s, %s, %s, %s)
        """,
        (
            company_name,
            username,
            password,
            email,
            phone
        )
    )
    connection.commit()
    print("\nEmployer registered successfully!")
    return cursor.lastrowid


def login_employee():
    print("\n" + "=" * 15)
    print("EMPLOYER LOGIN")
    print("=" * 15)
    username = get_non_empty_input("Username: ")
    password = get_non_empty_input("Password: ")
    cursor.execute(
        """
        SELECT employee_id, company_name
        FROM employees
        WHERE username = %s
        AND password = %s
        """,
        (username, password)
    )
    user = cursor.fetchone()
    if user:
        print(f"\nWelcome, {user[1]}!")
        return user[0]
    print("\nInvalid username or password.")
    return None

def login_or_register():
    global current_role
    while True:
        print("\n" + "=" * 20)
        print("JOB PORTAL")
        print("=" * 20)
        print("1. Candidate Login")
        print("2. Candidate Register")
        print("3. Employer Login")
        print("4. Employer Register")
        print("5. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            user_id = login_candidate()
            if user_id:
                current_role = "candidate"
                return user_id
        elif choice == "2":
            user_id = register_candidate()
            if user_id:
                current_role = "candidate"
                return user_id
        elif choice == "3":
            user_id = login_employee()
            if user_id:
                current_role = "employee"
                return user_id
        elif choice == "4":
            user_id = register_employee()
            if user_id:
                current_role = "employee"
                return user_id
        elif choice == "5":
            return None
        else:
            print("\nInvalid choice.")

def add_job(employee_id):
    print("\n" + "=" * 15)
    print("ADD JOB")
    print("=" * 15)

    title = get_non_empty_input("Job Title: ")
    description = get_non_empty_input("Job Description: ")
    location = get_non_empty_input("Location: ")
    job_type = get_valid_choice(
        "Job Type (Full Time/Part Time/Internship/Contract): ",
        [
            "Full Time",
            "Part Time",
            "Internship",
            "Contract"
        ]
    )

    salary = get_non_empty_input("Salary (example: 6 LPA): ")
    cursor.execute(
        """
        INSERT INTO jobs
        (
            employee_id,
            title,
            description,
            location,
            job_type,
            salary
        )
        VALUES
        (%s, %s, %s, %s, %s, %s)
        """,
        (
            employee_id,
            title,
            description,
            location,
            job_type,
            salary
        )
    )
    connection.commit()
    print("\nJob added successfully!")


def view_jobs():
    cursor.execute(
        """
        SELECT
            j.job_id,
            j.title,
            e.company_name,
            j.location,
            j.job_type,
            j.salary
        FROM jobs j
        JOIN employees e
        ON j.employee_id = e.employee_id
        WHERE j.status = 'Open'
        ORDER BY j.posted_on DESC
        """
    )
    jobs = cursor.fetchall()
    if not jobs:
        print("\nNo jobs available.")
        return
    print("\n" + "=" * 100)
    print(
        f"{'ID':<5}"
        f"{'TITLE':<25}"
        f"{'COMPANY':<20}"
        f"{'LOCATION':<15}"
        f"{'TYPE':<15}"
        f"SALARY"
    )
    print("-" * 100)
    for job in jobs:
        print(
            f"{job[0]:<5}"
            f"{job[1]:<25}"
            f"{job[2]:<20}"
            f"{job[3]:<15}"
            f"{job[4]:<15}"
            f"{job[5]}"
        )
def search_jobs():
    keyword = get_non_empty_input(
        "Search job title/location: "
    )
    cursor.execute(
        """
        SELECT
            j.job_id,
            j.title,
            e.company_name,
            j.location,
            j.job_type,
            j.salary
        FROM jobs j
        JOIN employees e
        ON j.employee_id = e.employee_id
        WHERE j.status = 'Open'
        AND (
            j.title LIKE %s
            OR j.location LIKE %s
            OR j.description LIKE %s
        )
        """,
        (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        )
    )
    jobs = cursor.fetchall()
    if not jobs:
        print("\nNo matching jobs found.")
        return
    print("\nSearch Results")
    print("-" * 100)
    for job in jobs:
        print(
            f"ID: {job[0]} | "
            f"Title: {job[1]} | "
            f"Company: {job[2]} | "
            f"Location: {job[3]} | "
            f"Type: {job[4]} | "
            f"Salary: {job[5]}"
        )

def sort_jobs():
    print("\nSort Jobs By")
    print("1. Title")
    print("2. Latest Posted")
    choice = input(
        "Enter choice: "
    ).strip()
    if choice == "1":
        column = "j.title"
    elif choice == "2":
        column = "j.posted_on"
    else:
        print("\nInvalid choice.")
        return
    query = f"""
        SELECT
            j.job_id,
            j.title,
            e.company_name,
            j.location,
            j.job_type,
            j.salary
        FROM jobs j
        JOIN employees e
        ON j.employee_id = e.employee_id
        WHERE j.status = 'Open'
        ORDER BY {column} ASC
    """
    cursor.execute(query)
    jobs = cursor.fetchall()
    if not jobs:
        print("\nNo jobs available.")
        return
    print("\nSorted Jobs")
    print("-" * 100)
    for job in jobs:
        print(
            f"ID: {job[0]} | "
            f"{job[1]} | "
            f"{job[2]} | "
            f"{job[3]} | "
            f"{job[4]} | "
            f"{job[5]}"
        )


def apply_for_job(candidate_id):

    job_id = get_valid_number("Enter Job ID: ")
    job_id = int(job_id)
    # Check job
    cursor.execute(
        """
        SELECT job_id
        FROM jobs
        WHERE job_id = %s
        AND status = 'Open'
        """,
        (job_id,)
    )
    if not cursor.fetchone():
        print("\nJob not found.")
        return

    # Check duplicate application
    cursor.execute(
        """
        SELECT application_id
        FROM applications
        WHERE job_id = %s
        AND candidate_id = %s
        """,
        (job_id,candidate_id)
    )

    if cursor.fetchone():
        print(
            "\nYou have already applied "
            "for this job."
        )
        return
    # Insert application
    cursor.execute(
        """
        INSERT INTO applications
        (
            job_id,
            candidate_id,
            status
        )
        VALUES
        (%s, %s, %s)
        """,
        (
            job_id,
            candidate_id,
            "Applied"
        )
    )
    connection.commit()
    print("\nApplication submitted successfully!")


def view_my_applications(candidate_id):
    cursor.execute(
        """
        SELECT
            a.application_id,
            j.title,
            e.company_name,
            j.location,
            a.status,
            a.applied_on
        FROM applications a
        JOIN jobs j
        ON a.job_id = j.job_id
        JOIN employees e
        ON j.employee_id = e.employee_id
        WHERE a.candidate_id = %s
        ORDER BY a.applied_on DESC
        """,
        (candidate_id,)
    )
    applications = cursor.fetchall()
    if not applications:
        print("\nYou have not applied for any jobs.")
        return
    print("\nMy Applications")
    print("-" * 100)
    for app in applications:
        print(f"Application ID : {app[0]}")
        print(f"Job            : {app[1]}")
        print(f"Company        : {app[2]}")
        print(f"Location       : {app[3]}")
        print(f"Status         : {app[4]}")
        print(f"Applied On     : {app[5]}")
        print("-" * 100)

def view_applications(employee_id):
    job_id = get_valid_number("Enter Job ID: ")
    job_id = int(job_id)
    # Check job ownership
    cursor.execute(
        """
        SELECT job_id
        FROM jobs
        WHERE job_id = %s
        AND employee_id = %s
        """,
        (job_id,employee_id)
    )
    if not cursor.fetchone():
        print(
            "\nThis job does not belong "
            "to your company."
        )
        return
    cursor.execute(
        """
        SELECT
            a.application_id,
            c.full_name,
            c.email,
            c.phone,
            c.skills,
            c.experience_years,
            a.status,
            a.applied_on
        FROM applications a
        JOIN candidates c
        ON a.candidate_id = c.candidate_id
        WHERE a.job_id = %s
        """,
        (job_id,)
    )
    applications = cursor.fetchall()
    if not applications:
        print("\nNo applications found.")
        return
    print("\nApplications")
    print("=" * 100)

    for app in applications:
        print(f"Application ID : {app[0]}")
        print(f"Candidate      : {app[1]}")
        print(f"Email          : {app[2]}")
        print(f"Phone          : {app[3]}")
        print(f"Skills         : {app[4]}")
        print(f"Experience     : {app[5]} years")
        print(f"Status         : {app[6]}")
        print(f"Applied On     : {app[7]}")
        print("-" * 100)
        
        
def update_application_status(employee_id):

    application_id = get_valid_number("Enter Application ID: ")
    application_id = int(application_id)
    new_status = get_valid_choice(
        "Status (Applied/Shortlisted/Rejected/Hired): ",
        ["Applied","Shortlisted","Rejected","Hired"]
    )
    # Check application belongs to employer
    cursor.execute(
        """
        SELECT a.application_id
        FROM applications a
        JOIN jobs j
        ON a.job_id = j.job_id
        WHERE a.application_id = %s
        AND j.employee_id = %s
        """,
        (application_id,employee_id)
    )
    if not cursor.fetchone():
        print(
            "\nApplication not found "
            "or does not belong to you.")
        return
    cursor.execute(
        """
        UPDATE applications SET status = %s WHERE application_id = %s
        """,
        (new_status,application_id)
    )
    connection.commit()
    print("\nApplication status updated successfully!")


def candidate_menu(candidate_id):
    while True:
        print("\n" + "=" * 20)
        print("CANDIDATE MENU")
        print("=" * 20)

        print("1. View Jobs")
        print("2. Search Jobs")
        print("3. Apply for Job")
        print("4. Sort Jobs")
        print("5. View My Applications")
        print("6. Logout")

        choice = input("\nEnter choice: ").strip()
        if choice == "1":
            view_jobs()
        elif choice == "2":
            search_jobs()
        elif choice == "3":
            apply_for_job(candidate_id)
        elif choice == "4":
            sort_jobs()
        elif choice == "5":
            view_my_applications(candidate_id)
        elif choice == "6":
            print("\nLogged out.")
            break
        else:
            print("\nInvalid choice.")
def employer_menu(employee_id):
    while True:
        print("\n" + "=" * 20)
        print("EMPLOYER MENU")
        print("=" * 20)

        print("1. Add Job")
        print("2. View Applications")
        print("3. Update Application Status")
        print("4. Logout")
        choice = input("\nEnter choice: ").strip()
        if choice == "1":
            add_job(employee_id)
        elif choice == "2":
            view_applications(employee_id)
        elif choice == "3":
            update_application_status(employee_id)
        elif choice == "4":
            print("\nLogged out.")
            break
        else:
            print("\nInvalid choice.")

def main():

    global current_user_id
    global current_role
    current_user_id = login_or_register()
    if current_user_id is None:
        print("\nThank you for using Job Portal.")
        return
    if current_role == "candidate":
        candidate_menu(current_user_id)
    elif current_role == "employee":
        employer_menu(current_user_id)
        
    cursor.close()
    connection.close()
    print("\nDatabase connection closed.")

main()