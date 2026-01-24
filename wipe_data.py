#!/usr/bin/env python3
"""
wipe_data.py - Data Cleanup Script for Facial Recognition Attendance System

This script allows you to wipe various data from the system:
- Attendance logs (database records)
- Uploaded images (captured photos)
- Known faces (registered students)

Usage:
    python wipe_data.py                    # Interactive mode
    python wipe_data.py --all              # Wipe everything
    python wipe_data.py --attendance       # Wipe only attendance logs
    python wipe_data.py --uploads          # Wipe only uploaded images
    python wipe_data.py --faces            # Wipe only known faces
    python wipe_data.py --attendance --uploads  # Combine options
"""

import os
import sys
import shutil
import sqlite3
import argparse
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "attendance.db")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")


def get_stats():
    """Get current data statistics."""
    stats = {
        "attendance_records": 0,
        "upload_files": 0,
        "upload_size_mb": 0,
        "known_faces": 0
    }
    
    # Count attendance records
    if os.path.exists(DATABASE_PATH):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM attendance_logs")
            stats["attendance_records"] = cursor.fetchone()[0]
            conn.close()
        except:
            pass
    
    # Count upload files
    if os.path.exists(UPLOADS_DIR):
        files = [f for f in os.listdir(UPLOADS_DIR) if not f.startswith('.')]
        stats["upload_files"] = len(files)
        total_size = sum(os.path.getsize(os.path.join(UPLOADS_DIR, f)) for f in files if os.path.isfile(os.path.join(UPLOADS_DIR, f)))
        stats["upload_size_mb"] = round(total_size / (1024 * 1024), 2)
    
    # Count known faces
    if os.path.exists(KNOWN_FACES_DIR):
        valid_ext = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        files = [f for f in os.listdir(KNOWN_FACES_DIR) if os.path.splitext(f)[1].lower() in valid_ext]
        stats["known_faces"] = len(files)
    
    return stats


def print_stats(stats):
    """Print current statistics."""
    print("\n" + "=" * 50)
    print("  CURRENT DATA STATISTICS")
    print("=" * 50)
    print(f"  📊 Attendance Records:  {stats['attendance_records']}")
    print(f"  📁 Uploaded Images:     {stats['upload_files']} files ({stats['upload_size_mb']} MB)")
    print(f"  👤 Known Faces:         {stats['known_faces']}")
    print("=" * 50 + "\n")


def wipe_attendance():
    """Wipe all attendance records from database."""
    if not os.path.exists(DATABASE_PATH):
        print("  ⚠ No database found.")
        return 0
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attendance_logs")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM attendance_logs")
        conn.commit()
        conn.close()
        print(f"  ✓ Deleted {count} attendance records")
        return count
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 0


def wipe_uploads():
    """Wipe all uploaded images."""
    if not os.path.exists(UPLOADS_DIR):
        print("  ⚠ Uploads folder not found.")
        return 0
    
    count = 0
    for filename in os.listdir(UPLOADS_DIR):
        if filename.startswith('.'):
            continue
        filepath = os.path.join(UPLOADS_DIR, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
            count += 1
    
    print(f"  ✓ Deleted {count} uploaded images")
    return count


def wipe_known_faces():
    """Wipe all known face images."""
    if not os.path.exists(KNOWN_FACES_DIR):
        print("  ⚠ Known faces folder not found.")
        return 0
    
    count = 0
    valid_ext = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.startswith('.'):
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_ext:
            filepath = os.path.join(KNOWN_FACES_DIR, filename)
            os.remove(filepath)
            count += 1
    
    print(f"  ✓ Deleted {count} known face images")
    return count


def backup_database():
    """Create a backup of the database before wiping."""
    if not os.path.exists(DATABASE_PATH):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BASE_DIR, f"attendance_backup_{timestamp}.db")
    shutil.copy2(DATABASE_PATH, backup_path)
    print(f"  📦 Backup created: {os.path.basename(backup_path)}")
    return backup_path


def confirm_action(message):
    """Ask for user confirmation."""
    response = input(f"\n{message} (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def interactive_mode():
    """Run in interactive mode with menu."""
    print("\n" + "=" * 50)
    print("  🗑️  DATA WIPE UTILITY")
    print("  Facial Recognition Attendance System")
    print("=" * 50)
    
    stats = get_stats()
    print_stats(stats)
    
    print("What would you like to wipe?\n")
    print("  1. Attendance logs only (database records)")
    print("  2. Uploaded images only (captured photos)")
    print("  3. Known faces only (registered students)")
    print("  4. Attendance + Uploads (keep known faces)")
    print("  5. Everything (full reset)")
    print("  6. Cancel\n")
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice == '6':
        print("\n  Cancelled. No data was deleted.\n")
        return
    
    actions = {
        '1': ['attendance'],
        '2': ['uploads'],
        '3': ['faces'],
        '4': ['attendance', 'uploads'],
        '5': ['attendance', 'uploads', 'faces']
    }
    
    if choice not in actions:
        print("\n  Invalid choice.\n")
        return
    
    selected = actions[choice]
    
    # Confirm
    action_names = {
        'attendance': 'attendance logs',
        'uploads': 'uploaded images',
        'faces': 'known faces (registered students)'
    }
    items = [action_names[a] for a in selected]
    
    print(f"\n⚠️  You are about to delete: {', '.join(items)}")
    
    if not confirm_action("Are you sure?"):
        print("\n  Cancelled. No data was deleted.\n")
        return
    
    # Create backup if wiping database
    if 'attendance' in selected:
        print("\n  Creating backup...")
        backup_database()
    
    # Perform wipe
    print("\n  Wiping data...")
    
    if 'attendance' in selected:
        wipe_attendance()
    if 'uploads' in selected:
        wipe_uploads()
    if 'faces' in selected:
        wipe_known_faces()
    
    print("\n  ✅ Data wipe complete!\n")
    
    # Show new stats
    new_stats = get_stats()
    print_stats(new_stats)


def main():
    parser = argparse.ArgumentParser(
        description="Wipe data from the Facial Recognition Attendance System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wipe_data.py                    Interactive mode
  python wipe_data.py --all              Wipe everything
  python wipe_data.py --attendance       Wipe only attendance logs
  python wipe_data.py --uploads          Wipe only uploaded images
  python wipe_data.py --faces            Wipe only known faces
  python wipe_data.py -a -u              Wipe attendance and uploads
  python wipe_data.py --all --no-backup  Wipe all without backup
        """
    )
    
    parser.add_argument('-a', '--attendance', action='store_true',
                        help='Wipe attendance logs (database)')
    parser.add_argument('-u', '--uploads', action='store_true',
                        help='Wipe uploaded images')
    parser.add_argument('-f', '--faces', action='store_true',
                        help='Wipe known faces (registered students)')
    parser.add_argument('--all', action='store_true',
                        help='Wipe all data (attendance, uploads, faces)')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip database backup')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='Skip confirmation prompt')
    parser.add_argument('--stats', action='store_true',
                        help='Show current data statistics only')
    
    args = parser.parse_args()
    
    # Show stats only
    if args.stats:
        stats = get_stats()
        print_stats(stats)
        return
    
    # Interactive mode if no arguments
    if not (args.attendance or args.uploads or args.faces or args.all):
        interactive_mode()
        return
    
    # Determine what to wipe
    wipe_list = []
    if args.all:
        wipe_list = ['attendance', 'uploads', 'faces']
    else:
        if args.attendance:
            wipe_list.append('attendance')
        if args.uploads:
            wipe_list.append('uploads')
        if args.faces:
            wipe_list.append('faces')
    
    # Show current stats
    stats = get_stats()
    print_stats(stats)
    
    # Confirm
    if not args.yes:
        action_names = {
            'attendance': 'attendance logs',
            'uploads': 'uploaded images',
            'faces': 'known faces'
        }
        items = [action_names[a] for a in wipe_list]
        print(f"⚠️  About to delete: {', '.join(items)}")
        
        if not confirm_action("Continue?"):
            print("\n  Cancelled.\n")
            return
    
    # Backup
    if 'attendance' in wipe_list and not args.no_backup:
        print("\n  Creating backup...")
        backup_database()
    
    # Wipe
    print("\n  Wiping data...")
    
    if 'attendance' in wipe_list:
        wipe_attendance()
    if 'uploads' in wipe_list:
        wipe_uploads()
    if 'faces' in wipe_list:
        wipe_known_faces()
    
    print("\n  ✅ Done!\n")


if __name__ == "__main__":
    main()
