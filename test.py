import mysql.connector as ms

try:
    conn = ms.connect(
        host="localhost",
        user="test_job",
        password="job@123",
        database="jobportal"
    )
    print("SUCCESS — connected!")
    conn.close()
except ms.Error as e:
    print("FAILED:", e)