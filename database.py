"""
database.py - SQLite Database Helper Functions

This module handles all database operations for the facial recognition
attendance system, including:
- Database initialization
- Attendance logging
- Query functions for attendance records
"""

import sqlite3
from datetime import datetime
from typing import Optional
import os

# Database file path
DATABASE_PATH = "attendance.db"


def get_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Returns:
        sqlite3.Connection: A connection to the SQLite database
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn


def init_database() -> None:
    """
    Initialize the database with required tables.
    
    Creates the attendance_logs table if it doesn't exist.
    This should be called when the application starts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create attendance_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT,
            confidence REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on student_name for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_student_name 
        ON attendance_logs(student_name)
    """)
    
    # Create index on timestamp for date-based queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON attendance_logs(timestamp)
    """)
    
    conn.commit()
    conn.close()
    print("[DATABASE] Database initialized successfully")


def log_attendance(
    student_name: str,
    image_path: Optional[str] = None,
    confidence: Optional[float] = None
) -> int:
    """
    Log an attendance record for a recognized student.
    
    Args:
        student_name: Name of the recognized student
        image_path: Path to the captured image (optional)
        confidence: Recognition confidence score (optional)
    
    Returns:
        int: The ID of the newly created attendance record
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO attendance_logs (student_name, timestamp, image_path, confidence)
        VALUES (?, ?, ?, ?)
    """, (student_name, datetime.now(), image_path, confidence))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"[DATABASE] Attendance logged for {student_name} (ID: {record_id})")
    return record_id


def get_all_attendance_logs(limit: int = 100) -> list:
    """
    Retrieve all attendance logs, ordered by most recent first.
    
    Args:
        limit: Maximum number of records to return (default: 100)
    
    Returns:
        list: List of attendance records as dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, student_name, timestamp, image_path, confidence
        FROM attendance_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert rows to list of dicts
    return [dict(row) for row in rows]


def get_attendance_by_date(date: str) -> list:
    """
    Retrieve attendance logs for a specific date.
    
    Args:
        date: Date string in 'YYYY-MM-DD' format
    
    Returns:
        list: List of attendance records for that date
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, student_name, timestamp, image_path, confidence
        FROM attendance_logs
        WHERE DATE(timestamp) = ?
        ORDER BY timestamp DESC
    """, (date,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_attendance_by_student(student_name: str, limit: int = 50) -> list:
    """
    Retrieve attendance logs for a specific student.
    
    Args:
        student_name: Name of the student
        limit: Maximum number of records to return
    
    Returns:
        list: List of attendance records for that student
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, student_name, timestamp, image_path, confidence
        FROM attendance_logs
        WHERE student_name = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (student_name, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_today_attendance() -> list:
    """
    Retrieve all attendance logs for today.
    
    Returns:
        list: List of today's attendance records
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return get_attendance_by_date(today)


def get_unique_students_today() -> list:
    """
    Get a list of unique students who attended today.
    
    Returns:
        list: List of unique student names
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT DISTINCT student_name, MIN(timestamp) as first_seen
        FROM attendance_logs
        WHERE DATE(timestamp) = ?
        GROUP BY student_name
        ORDER BY first_seen ASC
    """, (today,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def check_duplicate_attendance(student_name: str, minutes_threshold: int = 5) -> bool:
    """
    Check if a student has been logged recently (to avoid duplicate entries).
    
    Args:
        student_name: Name of the student
        minutes_threshold: Minimum minutes between attendance logs
    
    Returns:
        bool: True if a recent attendance exists (duplicate), False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM attendance_logs
        WHERE student_name = ?
        AND timestamp > datetime('now', ? || ' minutes')
    """, (student_name, f"-{minutes_threshold}"))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['count'] > 0


def get_attendance_stats() -> dict:
    """
    Get attendance statistics.
    
    Returns:
        dict: Statistics including total logs, unique students, today's count
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Total attendance logs
    cursor.execute("SELECT COUNT(*) as total FROM attendance_logs")
    total_logs = cursor.fetchone()['total']
    
    # Unique students
    cursor.execute("SELECT COUNT(DISTINCT student_name) as count FROM attendance_logs")
    unique_students = cursor.fetchone()['count']
    
    # Today's logs
    cursor.execute("""
        SELECT COUNT(*) as count FROM attendance_logs
        WHERE DATE(timestamp) = ?
    """, (today,))
    today_logs = cursor.fetchone()['count']
    
    # Today's unique students
    cursor.execute("""
        SELECT COUNT(DISTINCT student_name) as count FROM attendance_logs
        WHERE DATE(timestamp) = ?
    """, (today,))
    today_unique = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_logs': total_logs,
        'unique_students': unique_students,
        'today_logs': today_logs,
        'today_unique_students': today_unique
    }


if __name__ == "__main__":
    # Test database initialization
    init_database()
    print("Database initialized successfully!")
    print(f"Stats: {get_attendance_stats()}")
