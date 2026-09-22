def apply_for_job(candidate_id, job_id):
    cursor.execute(
        "INSERT INTO applications (job_id, candidate_id, status) VALUES (%s, %s, %s)",
        (job_id, candidate_id, "Applied")          
    )
    connection.commit()
    print("Application submitted successfully.")


def create_user():
    print(f"\n{'='*10} Welcome to Job Portal {'='*10}")
    name = input("Enter your Fullname: ")
    email = input("Enter your Email: ")
    cursor.execute(
        "SELECT candidate_id, full_name FROM candidates WHERE email = %s",
        (email,)
    )

    found_user = cursor.fetchone()
    if found_user:
        print(f"\nWelcome Back {found_user[1]}!")
        return found_user[0]
    else:
        phone = input("Enter your Phone number: ")
        skills = input("Enter your Skills (comma-separated, e.g. Python, MySQL): ")
        experience_years = input("Enter your Years of Experience: ")
        cursor.execute(
            """INSERT INTO candidates (full_name, email, phone, skills, experience_years)
               VALUES (%s, %s, %s, %s, %s)""",
            (name, email, phone, skills, experience_years)
        )
        connection.commit()
        print(f"\nUser '{name}' created successfully!")
        return cursor.lastrowid          

def add_job(title, description, location, job_type, salary, company_name):
    cursor.execute(
        """INSERT INTO jobs (title, description, location, job_type, salary, company_name)
           VALUES (%s, %s, %s, %s, %s, %s)""",          
        (title, description, location, job_type, salary, company_name)
    )
    connection.commit()
    print(f"\nJob '{title}' posted successfully!")

def view_jobs():
    cursor.execute("SELECT job_id, title, company_name, location, job_type, status FROM jobs WHERE status = 'Open'")
    jobs = cursor.fetchall()
    if not jobs:
        print("\nNo open jobs available right now.")
        return

    print(f"\n{'ID':<5}{'Title':<25}{'Company':<20}{'Location':<15}{'Type':<12}")
    print("-" * 77)
    for job in jobs:
        print(f"{job[0]:<5} {job[1]:<25} {job[2]:<20} {job[3]:<15} {job[4]:<12}")

def search_jobs(keyword):
    cursor.execute(
        """SELECT job_id, title, company_name, location, job_type
           FROM jobs
           WHERE status = 'Open' AND (title LIKE %s OR location LIKE %s)""",
        (f"%{keyword}%", f"%{keyword}%")
    )
    results = cursor.fetchall()

    if not results:
        print(f"\nNo jobs found matching '{keyword}'.")
        return

    for job in results:
        print(f"[{job[0]}] {job[1]} — {job[2]} ({job[3]}, {job[4]})")