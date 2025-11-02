import psycopg2
from psycopg2 import pool

import os
from dotenv import load_dotenv

# Get the directory of the project root (relative to this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Build full path to .env
env_path = os.path.join(project_root, '.env')

# Load .env
load_dotenv(dotenv_path=env_path)

class Database:
    def __init__(self):
        self.db_params = {
            "host": os.getenv("HOST"),
            "port": os.getenv("PORT"),
            "database": os.getenv("DATABASE_NAME"),
            "user": os.getenv("USER"),
            "password": os.getenv("PASSWORD"),
        }

        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10, **self.db_params
            )
            if self.connection_pool:
                print("Database connection pool created successfully")
        except Exception as e:
            print(f"Error creating connection pool: {e}")

    def get_conn(self):
        """Get a connection from the pool"""
        return self.connection_pool.getconn()

    def put_conn(self, conn):
        """Return a connection to the pool"""
        self.connection_pool.putconn(conn)

    def execute_query(self, query, params=None, fetch=False):
        """Execute SQL safely (insert, select, update, delete)"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
            else:
                result = None
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(f" Query error: {e}")
        finally:
            cursor.close()
            self.put_conn(conn)

# Singleton instance
db = Database()
