import mysql.connector as ms

def get_connection():
    connection = ms.connect(
        host="localhost",
        user="job",              
        password="job@123",      
        database="jobportal"
    )
    print("Connected....")
    return connection