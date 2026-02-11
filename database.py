"""
database.py - SQLite Database Helper Functions

This module handles all database operations for the facial recognition
attendance system, including:
- Database initialization
- Student management
- Attendance logging (Time In / Time Out)
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
    
    Creates the students and attendance_logs tables if they don't exist.
    This should be called when the application starts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            year_level TEXT,
            guardian_name TEXT,
            guardian_email TEXT,
            image_filename TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create attendance_logs table with log_type
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            log_type TEXT DEFAULT 'IN',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT,
            confidence REAL,
            email_sent INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Migration: Add log_type column if it doesn't exist (for existing databases)
    try:
        cursor.execute("SELECT log_type FROM attendance_logs LIMIT 1")
    except:
        print("[DATABASE] Adding log_type column to existing table...")
        cursor.execute("ALTER TABLE attendance_logs ADD COLUMN log_type TEXT DEFAULT 'IN'")
    
    # Migration: Add email_sent column if it doesn't exist
    try:
        cursor.execute("SELECT email_sent FROM attendance_logs LIMIT 1")
    except:
        print("[DATABASE] Adding email_sent column to existing table...")
        cursor.execute("ALTER TABLE attendance_logs ADD COLUMN email_sent INTEGER DEFAULT 0")
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_student_name 
        ON attendance_logs(student_name)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON attendance_logs(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_log_type 
        ON attendance_logs(log_type)
    """)
    
    conn.commit()
    conn.close()
    print("[DATABASE] Database initialized successfully")


# =============================================================================
# Student Management
# =============================================================================

def add_student(
    name: str,
    year_level: str = None,
    guardian_name: str = None,
    guardian_email: str = None,
    image_filename: str = None
) -> int:
    """
    Add or update a student in the database.
    
    Args:
        name: Student's full name
        year_level: Year level (e.g., "BSIT - 1st Year")
        guardian_name: Guardian's full name
        guardian_email: Guardian's email address
        image_filename: Filename of the student's face image
    
    Returns:
        int: The student ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if student exists
    cursor.execute("SELECT id FROM students WHERE name = ?", (name,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing student
        cursor.execute("""
            UPDATE students 
            SET year_level = COALESCE(?, year_level),
                guardian_name = COALESCE(?, guardian_name),
                guardian_email = COALESCE(?, guardian_email),
                image_filename = COALESCE(?, image_filename),
                updated_at = ?
            WHERE name = ?
        """, (year_level, guardian_name, guardian_email, image_filename, 
              datetime.now(), name))
        student_id = existing['id']
    else:
        # Insert new student
        cursor.execute("""
            INSERT INTO students (name, year_level, guardian_name, guardian_email, image_filename)
            VALUES (?, ?, ?, ?, ?)
        """, (name, year_level, guardian_name, guardian_email, image_filename))
        student_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    print(f"[DATABASE] Student saved: {name} (ID: {student_id})")
    return student_id


def get_student(name: str) -> Optional[dict]:
    """
    Get student information by name.
    
    Args:
        name: Student's name
    
    Returns:
        dict: Student information or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_all_students() -> list:
    """
    Get all registered students.
    
    Returns:
        list: List of student records
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# =============================================================================
# Attendance Logging
# =============================================================================

def log_attendance(
    student_name: str,
    log_type: str = "IN",
    image_path: Optional[str] = None,
    confidence: Optional[float] = None
) -> int:
    """
    Log an attendance record for a recognized student.
    
    Args:
        student_name: Name of the recognized student
        log_type: "IN" for time in, "OUT" for time out
        image_path: Path to the captured image (optional)
        confidence: Recognition confidence score (optional)
    
    Returns:
        int: The ID of the newly created attendance record
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO attendance_logs (student_name, log_type, timestamp, image_path, confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (student_name, log_type.upper(), datetime.now(), image_path, confidence))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"[DATABASE] Attendance logged: {student_name} - {log_type} (ID: {record_id})")
    return record_id


def mark_email_sent(record_id: int) -> None:
    """
    Mark an attendance record as having email notification sent.
    
    Args:
        record_id: The attendance log ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE attendance_logs SET email_sent = 1 WHERE id = ?
    """, (record_id,))
    
    conn.commit()
    conn.close()


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
        SELECT id, student_name, log_type, timestamp, image_path, confidence
        FROM attendance_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
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
        SELECT id, student_name, log_type, timestamp, image_path, confidence
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
        SELECT id, student_name, log_type, timestamp, image_path, confidence
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
    Get a list of unique students who attended today with their status.
    
    Returns:
        list: List of unique student records with attendance status
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT DISTINCT student_name, 
               MIN(timestamp) as first_in,
               (SELECT log_type FROM attendance_logs a2 
                WHERE a2.student_name = attendance_logs.student_name 
                AND DATE(a2.timestamp) = ?
                ORDER BY a2.timestamp DESC LIMIT 1) as last_action
        FROM attendance_logs
        WHERE DATE(timestamp) = ?
        GROUP BY student_name
        ORDER BY first_in ASC
    """, (today, today))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def check_duplicate_attendance(student_name: str, log_type: str, minutes_threshold: int = 5) -> bool:
    """
    Check if a student has been logged recently (to avoid duplicate entries).
    
    Args:
        student_name: Name of the student
        log_type: "IN" or "OUT"
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
        AND log_type = ?
        AND timestamp > datetime('now', ? || ' minutes')
    """, (student_name, log_type.upper(), f"-{minutes_threshold}"))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['count'] > 0


def get_student_last_action(student_name: str) -> Optional[str]:
    """
    Get the last action (IN/OUT) for a student today.
    
    Args:
        student_name: Name of the student
    
    Returns:
        str: "IN" or "OUT", or None if no action today
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT log_type FROM attendance_logs
        WHERE student_name = ? AND DATE(timestamp) = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (student_name, today))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['log_type'] if result else None


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
    
    # Unique students (registered)
    cursor.execute("SELECT COUNT(*) as count FROM students")
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
    
    # Today's time ins
    cursor.execute("""
        SELECT COUNT(*) as count FROM attendance_logs
        WHERE DATE(timestamp) = ? AND log_type = 'IN'
    """, (today,))
    today_ins = cursor.fetchone()['count']
    
    # Today's time outs
    cursor.execute("""
        SELECT COUNT(*) as count FROM attendance_logs
        WHERE DATE(timestamp) = ? AND log_type = 'OUT'
    """, (today,))
    today_outs = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_logs': total_logs,
        'unique_students': unique_students,
        'today_logs': today_logs,
        'today_unique_students': today_unique,
        'today_time_ins': today_ins,
        'today_time_outs': today_outs
    }


if __name__ == "__main__":
    # Test database initialization
    init_database()
    print("Database initialized successfully!")
    print(f"Stats: {get_attendance_stats()}")
