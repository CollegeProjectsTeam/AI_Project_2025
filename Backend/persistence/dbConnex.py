from __future__ import annotations

import os
from typing import Any, Iterable, Optional

from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

from Backend.services.logging_service import Logger


log = Logger("Database")

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_env_path = os.path.join(_project_root, ".env")
load_dotenv(dotenv_path=_env_path)


class Database:
    def __init__(self, minconn: int = 1, maxconn: int = 10):
        self.db_params = {
            "host": os.getenv("HOST"),
            "port": os.getenv("PORT"),
            "dbname": os.getenv("DATABASE_NAME"),
            "user": os.getenv("USER"),
            "password": os.getenv("PASSWORD"),
        }

        missing = [k for k, v in self.db_params.items() if not str(v or "").strip()]
        if missing:
            log.error("Missing database env vars", {"missing": missing, "env_path": _env_path})
            raise RuntimeError(f"Missing database env vars: {', '.join(missing)}")

        try:
            self.pool: SimpleConnectionPool = SimpleConnectionPool(minconn, maxconn, **self.db_params)
            log.ok("Database connection pool created", {"min": minconn, "max": maxconn, "host": self.db_params["host"]})
        except Exception as e:
            log.error("Error creating connection pool", {"host": self.db_params.get("host")}, exc=e)
            raise

    def get_conn(self):
        try:
            return self.pool.getconn()
        except Exception as e:
            log.error("Failed to get connection from pool", exc=e)
            raise

    def put_conn(self, conn) -> None:
        try:
            if conn is not None:
                self.pool.putconn(conn)
        except Exception as e:
            log.error("Failed to return connection to pool", exc=e)

    def close_all(self) -> None:
        try:
            self.pool.closeall()
            log.warn("Database pool closed")
        except Exception as e:
            log.error("Failed to close pool", exc=e)

    def execute(
        self,
        query: str,
        params: Optional[Iterable[Any]] = None,
        fetch: bool = False,
    ):
        conn = self.get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchall() if fetch else None
            conn.commit()
            return result
        except Exception as e:
            try:
                conn.rollback()
            except Exception as rb:
                log.error("Rollback failed", exc=rb)
            log.error("Query failed", {"query": query[:220], "has_params": params is not None, "fetch": fetch}, exc=e)
            raise
        finally:
            self.put_conn(conn)


db = Database()
