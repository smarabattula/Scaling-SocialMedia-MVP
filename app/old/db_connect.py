import psycopg2
from psycopg2.extras import RealDictCursor
import time
def open_connection():
    count = 0
    while count <= 5:
        try:
            conn = psycopg2.connect("host=localhost dbname=fastapi-db user=postgres password=password", cursor_factory=RealDictCursor)
            print("Database connection successful!")
            return conn
        except psycopg2.Error as e:
            print(f"An error occurred while connecting to the database: {e}")
            time.sleep(2)
        count += 1
    raise TimeoutError("Error: Connection Timed Out after 5 retries. Retry again")

def close_connection(conn) -> None:
    if conn:
        conn.close()

def query_posts(conn, query, data):
    try:

        curr = conn.cursor()
        curr.execute(query, data)
        records = curr.fetchall()
        return records
    except psycopg2.Error as e:
        print(f"An error occurred while querying the database: {e}")
    finally:
        curr.close()

def insert_update_post(conn, query, data):
    try:
        curr = conn.cursor()
        result = curr.execute(query, data)
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"An error occurred while inserting a record in the database: {e}")
        return False
    finally:
        curr.close()

def delete_post(conn, query, data):
    try:
        curr = conn.cursor()
        result = curr.execute(query, data)
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"An error occurred while deleting a record in the database: {e}")
        return False
    finally:
        curr.close()


