# app/core/database.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings


def get_connection():
    """
    Creates a new PostgreSQL connection.
    Uses DATABASE_URL from environment.
    """
    if not settings.DATABASE_URL:
        raise Exception("DATABASE_URL is not set in environment variables")

    conn = psycopg2.connect(
        settings.DATABASE_URL,
        cursor_factory=RealDictCursor
    )

    return conn


def init_db():
    """
    Initializes required tables if they do not exist.
    Run once at startup.
    """

    conn = get_connection()
    cur = conn.cursor()

    # =========================
    # USERS TABLE
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance NUMERIC DEFAULT 0
        );
    """)

    # =========================
    # TRANSACTIONS TABLE
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            reference TEXT UNIQUE,
            amount NUMERIC,
            type TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # =========================
    # ACTIVATIONS TABLE (SMS)
    # =========================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activations (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            country TEXT,
            service TEXT,
            request_id TEXT UNIQUE,
            number TEXT,
            otp TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
