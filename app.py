"""
app.py - Flask Server for Facial Recognition Attendance System

This is the main application server that:
- Receives images from ESP32-CAM via HTTP POST
- Performs face recognition against known faces
- Logs attendance to SQLite database
- Provides a web dashboard for viewing attendance logs

Endpoints:
    POST /api/recognize     - Receive and process image from ESP32-CAM
    POST /api/register      - Register a new student face
    GET  /api/attendance    - Get attendance logs (JSON)
    GET  /api/stats         - Get attendance statistics
    GET  /api/students      - Get list of registered students
    GET  /                  - Web dashboard
    GET  /dashboard         - Web dashboard (alias)
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from database import init_database, log_attendance, get_all_attendance_logs
from database import get_today_attendance, get_attendance_stats, check_duplicate_attendance
from database import get_unique_students_today
from utils import (
    load_known_faces, 
    save_uploaded_image, 
    recognize_face,
    recognize_face_from_bytes,
    add_known_face,
    get_registered_students,
    ensure_directories,
    UPLOADS_DIR
)
import os
from datetime import datetime
import time

# Initialize Flask application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Global variables for known faces (loaded at startup)
known_encodings = []
known_names = []

# Minimum minutes between attendance logs for same student (prevents duplicates)
DUPLICATE_THRESHOLD_MINUTES = 5

# Capture command state (for ESP32-CAM polling)
capture_command = {
    "pending": False,
    "mode": None,           # "attendance" or "register"
    "student_name": None,   # Only used for registration
    "timestamp": 0,
    "result": None,         # Store the result for frontend polling
    "result_timestamp": 0
}


def reload_known_faces() -> None:
    """
    Reload known faces from the known_faces directory.
    Call this after adding new student faces.
    """
    global known_encodings, known_names
    known_encodings, known_names = load_known_faces()
    print(f"[APP] Loaded {len(known_names)} known face(s)")


# =============================================================================
# Capture Command Endpoints (Frontend -> ESP32-CAM communication)
# =============================================================================

@app.route('/api/command/capture', methods=['POST'])
def request_capture():
    """
    Request ESP32-CAM to capture an image.
    Called by the frontend when user clicks capture button.
    
    Expected JSON:
        - mode: "attendance" or "register"
        - name: Student name (required for register mode)
    """
    global capture_command
    
    try:
        data = request.get_json() or {}
        mode = data.get('mode', 'attendance')
        student_name = data.get('name', '').strip()
        
        if mode == 'register' and not student_name:
            return jsonify({
                "status": "error",
                "message": "Student name is required for registration"
            }), 400
        
        # Set capture command
        capture_command = {
            "pending": True,
            "mode": mode,
            "student_name": student_name if mode == 'register' else None,
            "timestamp": time.time(),
            "result": None,
            "result_timestamp": 0
        }
        
        print(f"[APP] Capture requested: mode={mode}, name={student_name}")
        
        return jsonify({
            "status": "success",
            "message": f"Capture command sent ({mode})",
            "mode": mode
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/command/poll', methods=['GET'])
def poll_command():
    """
    ESP32-CAM polls this endpoint to check for pending capture commands.
    Returns the command if pending, otherwise returns no_command.
    """
    global capture_command
    
    # Check if command is pending and not too old (expires after 30 seconds)
    if capture_command["pending"] and (time.time() - capture_command["timestamp"]) < 30:
        return jsonify({
            "status": "capture",
            "mode": capture_command["mode"],
            "student_name": capture_command["student_name"]
        }), 200
    else:
        # Clear expired command
        if capture_command["pending"] and (time.time() - capture_command["timestamp"]) >= 30:
            capture_command["pending"] = False
            capture_command["result"] = {"status": "timeout", "message": "Capture timed out"}
            capture_command["result_timestamp"] = time.time()
        
        return jsonify({
            "status": "no_command"
        }), 200


@app.route('/api/command/result', methods=['GET'])
def get_capture_result():
    """
    Frontend polls this to get the result of the last capture.
    """
    global capture_command
    
    if capture_command["result"] and (time.time() - capture_command["result_timestamp"]) < 60:
        return jsonify(capture_command["result"]), 200
    else:
        return jsonify({
            "status": "waiting",
            "pending": capture_command["pending"]
        }), 200


@app.route('/api/command/clear', methods=['POST'])
def clear_command():
    """
    Clear the current capture command and result.
    """
    global capture_command
    capture_command = {
        "pending": False,
        "mode": None,
        "student_name": None,
        "timestamp": 0,
        "result": None,
        "result_timestamp": 0
    }
    return jsonify({"status": "success"}), 200


# =============================================================================
# ESP32-CAM Image Recognition Endpoint
# =============================================================================

@app.route('/api/recognize', methods=['POST'])
def recognize():
    """
    Receive an image from ESP32-CAM and attempt to recognize the face.
    
    Expected: Image data in request body or as multipart file upload.
    Optional header: X-Capture-Mode (attendance/register)
    Optional header: X-Student-Name (for register mode)
    
    Returns:
        JSON with recognition result:
        - Success: {"status": "success", "name": "Student Name", "confidence": 0.85}
        - Unknown: {"status": "unknown", "message": "Face not recognized"}
        - Error: {"status": "error", "message": "Error description"}
    """
    global capture_command
    
    try:
        image_data = None
        
        # Check capture mode from headers (sent by ESP32-CAM based on command)
        capture_mode = request.headers.get('X-Capture-Mode', 'attendance')
        student_name_header = request.headers.get('X-Student-Name', '')
        
        # Check for file upload (multipart/form-data)
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                result = {"status": "error", "message": "No file selected"}
                capture_command["result"] = result
                capture_command["result_timestamp"] = time.time()
                capture_command["pending"] = False
                return jsonify(result), 400
            image_data = file.read()
        
        # Check for file with key 'file'
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                result = {"status": "error", "message": "No file selected"}
                capture_command["result"] = result
                capture_command["result_timestamp"] = time.time()
                capture_command["pending"] = False
                return jsonify(result), 400
            image_data = file.read()
        
        # Check for raw image data in request body (ESP32-CAM typically sends this)
        elif request.data:
            image_data = request.data
        
        # No image data found
        if not image_data or len(image_data) == 0:
            result = {"status": "error", "message": "No image data received"}
            capture_command["result"] = result
            capture_command["result_timestamp"] = time.time()
            capture_command["pending"] = False
            return jsonify(result), 400
        
        print(f"[APP] Received image: {len(image_data)} bytes, mode: {capture_mode}")
        
        # Save the uploaded image
        image_path = save_uploaded_image(image_data, prefix="esp32")
        
        # Handle registration mode
        if capture_mode == 'register':
            reg_name = student_name_header or capture_command.get("student_name", "")
            if not reg_name:
                result = {"status": "error", "message": "Student name required for registration"}
                capture_command["result"] = result
                capture_command["result_timestamp"] = time.time()
                capture_command["pending"] = False
                return jsonify(result), 400
            
            # Add the known face
            success = add_known_face(image_data, reg_name)
            
            if success:
                reload_known_faces()
                result = {
                    "status": "registered",
                    "message": f"Successfully registered {reg_name}",
                    "name": reg_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "status": "error",
                    "message": "Could not detect face in the image"
                }
            
            capture_command["result"] = result
            capture_command["result_timestamp"] = time.time()
            capture_command["pending"] = False
            return jsonify(result), 200 if success else 400
        
        # Handle attendance mode (default)
        matched_name, confidence = recognize_face(
            image_path, 
            known_encodings, 
            known_names
        )
        
        if matched_name:
            # Check for duplicate attendance (same student within threshold)
            is_duplicate = check_duplicate_attendance(
                matched_name, 
                DUPLICATE_THRESHOLD_MINUTES
            )
            
            if is_duplicate:
                result = {
                    "status": "duplicate",
                    "name": matched_name,
                    "message": f"Already logged within {DUPLICATE_THRESHOLD_MINUTES} minutes"
                }
                capture_command["result"] = result
                capture_command["result_timestamp"] = time.time()
                capture_command["pending"] = False
                return jsonify(result), 200
            
            # Log attendance
            record_id = log_attendance(
                student_name=matched_name,
                image_path=image_path,
                confidence=confidence
            )
            
            result = {
                "status": "success",
                "name": matched_name,
                "confidence": round(confidence, 4) if confidence else None,
                "record_id": record_id,
                "timestamp": datetime.now().isoformat()
            }
            capture_command["result"] = result
            capture_command["result_timestamp"] = time.time()
            capture_command["pending"] = False
            return jsonify(result), 200
        else:
            result = {
                "status": "unknown",
                "message": "Face not recognized"
            }
            capture_command["result"] = result
            capture_command["result_timestamp"] = time.time()
            capture_command["pending"] = False
            return jsonify(result), 200
            
    except Exception as e:
        print(f"[APP] ERROR in /api/recognize: {str(e)}")
        result = {"status": "error", "message": str(e)}
        capture_command["result"] = result
        capture_command["result_timestamp"] = time.time()
        capture_command["pending"] = False
        return jsonify(result), 500


# =============================================================================
# Student Registration Endpoint
# =============================================================================

@app.route('/api/register', methods=['POST'])
def register_student():
    """
    Register a new student face in the system.
    
    Expected:
        - Image file as multipart upload
        - 'name' field with student name
    
    Returns:
        JSON with registration result
    """
    try:
        # Get student name
        student_name = request.form.get('name')
        if not student_name or student_name.strip() == '':
            return jsonify({
                "status": "error",
                "message": "Student name is required"
            }), 400
        
        student_name = student_name.strip()
        
        # Get image data
        image_data = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    "status": "error",
                    "message": "No image file selected"
                }), 400
            image_data = file.read()
        elif 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
        elif request.data:
            image_data = request.data
        
        if not image_data:
            return jsonify({
                "status": "error",
                "message": "No image data received"
            }), 400
        
        # Add the known face
        success = add_known_face(image_data, student_name)
        
        if success:
            # Reload known faces to include the new student
            reload_known_faces()
            
            return jsonify({
                "status": "success",
                "message": f"Successfully registered {student_name}",
                "name": student_name
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Could not detect face in the image"
            }), 400
            
    except Exception as e:
        print(f"[APP] ERROR in /api/register: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =============================================================================
# Web Fallback Endpoints (Direct Upload - No ESP32-CAM needed)
# =============================================================================

@app.route('/api/web/register', methods=['POST'])
def web_register():
    """
    Register a new student via web upload (fallback when ESP32-CAM not available).
    Accepts file upload or base64 image data.
    
    Expected:
        - 'name': Student name (form field or JSON)
        - 'image': Image file (multipart) OR
        - 'image_data': Base64 encoded image (JSON)
    """
    try:
        image_data = None
        student_name = None
        
        # Check for multipart form data first (most common from webcam/upload)
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                image_data = file.read()
            student_name = request.form.get('name', '').strip()
        # Check for JSON request (base64)
        elif request.is_json:
            data = request.get_json()
            student_name = data.get('name', '').strip()
            image_base64 = data.get('image_data', '')
            
            if image_base64:
                # Remove data URL prefix if present
                if ',' in image_base64:
                    image_base64 = image_base64.split(',')[1]
                import base64
                image_data = base64.b64decode(image_base64)
        else:
            # Fallback: check form data
            student_name = request.form.get('name', '').strip()
        
        if not student_name:
            return jsonify({
                "status": "error",
                "message": "Student name is required"
            }), 400
        
        if not image_data:
            return jsonify({
                "status": "error",
                "message": "No image data received"
            }), 400
        
        print(f"[APP] Web register: {student_name}, image size: {len(image_data)} bytes")
        
        # Save upload for reference
        save_uploaded_image(image_data, prefix="web_register")
        
        # Add the known face
        success = add_known_face(image_data, student_name)
        
        if success:
            reload_known_faces()
            return jsonify({
                "status": "registered",
                "message": f"Successfully registered {student_name}",
                "name": student_name,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Could not detect face in the image. Please ensure face is clearly visible."
            }), 400
            
    except Exception as e:
        print(f"[APP] ERROR in /api/web/register: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/web/attendance', methods=['POST'])
def web_attendance():
    """
    Log attendance via web upload (fallback when ESP32-CAM not available).
    Accepts file upload or base64 image data from webcam.
    
    Expected:
        - 'image': Image file (multipart) OR
        - 'image_data': Base64 encoded image (JSON)
    """
    try:
        image_data = None
        
        # Check for multipart form data first (from webcam blob or file upload)
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                image_data = file.read()
        # Check for JSON request (base64)
        elif request.is_json:
            data = request.get_json()
            image_base64 = data.get('image_data', '')
            
            if image_base64:
                # Remove data URL prefix if present
                if ',' in image_base64:
                    image_base64 = image_base64.split(',')[1]
                import base64
                image_data = base64.b64decode(image_base64)
        
        if not image_data:
            return jsonify({
                "status": "error",
                "message": "No image data received"
            }), 400
        
        print(f"[APP] Web attendance image: {len(image_data)} bytes")
        
        # Save the uploaded image
        image_path = save_uploaded_image(image_data, prefix="web_attendance")
        
        # Attempt face recognition
        matched_name, confidence = recognize_face(
            image_path, 
            known_encodings, 
            known_names
        )
        
        if matched_name:
            # Check for duplicate attendance
            is_duplicate = check_duplicate_attendance(
                matched_name, 
                DUPLICATE_THRESHOLD_MINUTES
            )
            
            if is_duplicate:
                return jsonify({
                    "status": "duplicate",
                    "name": matched_name,
                    "message": f"Already logged within {DUPLICATE_THRESHOLD_MINUTES} minutes"
                }), 200
            
            # Log attendance
            record_id = log_attendance(
                student_name=matched_name,
                image_path=image_path,
                confidence=confidence
            )
            
            return jsonify({
                "status": "success",
                "name": matched_name,
                "confidence": round(confidence, 4) if confidence else None,
                "record_id": record_id,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "unknown",
                "message": "Face not recognized"
            }), 200
            
    except Exception as e:
        print(f"[APP] ERROR in /api/web/attendance: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =============================================================================
# Attendance Data Endpoints
# =============================================================================

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """
    Get attendance logs.
    
    Query parameters:
        - limit: Maximum number of records (default: 100)
        - today: If 'true', only return today's logs
    
    Returns:
        JSON array of attendance records
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        today_only = request.args.get('today', 'false').lower() == 'true'
        
        if today_only:
            logs = get_today_attendance()
        else:
            logs = get_all_attendance_logs(limit=limit)
        
        return jsonify({
            "status": "success",
            "count": len(logs),
            "logs": logs
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get attendance statistics.
    
    Returns:
        JSON with statistics
    """
    try:
        stats = get_attendance_stats()
        return jsonify({
            "status": "success",
            **stats
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/students', methods=['GET'])
def get_students():
    """
    Get list of registered students.
    
    Returns:
        JSON array of student names
    """
    try:
        students = get_registered_students()
        return jsonify({
            "status": "success",
            "count": len(students),
            "students": students
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/reload', methods=['POST'])
def reload_faces():
    """
    Reload known faces from the known_faces directory.
    Useful after manually adding face images.
    
    Returns:
        JSON with reload result
    """
    try:
        reload_known_faces()
        return jsonify({
            "status": "success",
            "message": f"Loaded {len(known_names)} known face(s)",
            "students": known_names
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =============================================================================
# Web Dashboard
# =============================================================================

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """
    Render the attendance dashboard web page.
    """
    try:
        logs = get_today_attendance()
        stats = get_attendance_stats()
        unique_today = get_unique_students_today()
        students = get_registered_students()
        
        return render_template(
            'dashboard.html',
            logs=logs,
            stats=stats,
            unique_today=unique_today,
            students=students,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve uploaded images for viewing in the dashboard.
    """
    return send_from_directory(UPLOADS_DIR, filename)


# =============================================================================
# Health Check
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return jsonify({
        "status": "healthy",
        "known_faces_count": len(known_names),
        "timestamp": datetime.now().isoformat()
    }), 200


# =============================================================================
# Application Startup
# =============================================================================

def initialize_app():
    """
    Initialize the application:
    - Create required directories
    - Initialize database
    - Load known faces
    """
    print("\n" + "=" * 60)
    print("  Facial Recognition Attendance System")
    print("=" * 60)
    
    # Ensure directories exist
    ensure_directories()
    
    # Initialize database
    init_database()
    
    # Load known faces
    reload_known_faces()
    
    print("\n[APP] Server ready!")
    print("[APP] Endpoints:")
    print("  POST /api/recognize  - Process ESP32-CAM image")
    print("  POST /api/register   - Register new student")
    print("  GET  /api/attendance - Get attendance logs")
    print("  GET  /api/stats      - Get statistics")
    print("  GET  /api/students   - Get registered students")
    print("  GET  /               - Web dashboard")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    # Initialize the application
    initialize_app()
    
    # Run the Flask development server
    # Note: For production, use a proper WSGI server like Gunicorn
    app.run(
        host='0.0.0.0',  # Listen on all interfaces (required for ESP32-CAM)
        port=5000,
        debug=True,
        threaded=True
    )
