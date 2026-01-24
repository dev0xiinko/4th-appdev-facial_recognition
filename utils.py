"""
utils.py - Face Recognition Utility Functions

This module provides helper functions for:
- Loading known face encodings from the known_faces folder
- Saving uploaded images
- Recognizing faces in images
- Image preprocessing
"""

import os
import face_recognition
import numpy as np
from PIL import Image
from datetime import datetime
from typing import Optional, Tuple
import io

# Configuration
KNOWN_FACES_DIR = "known_faces"
UPLOADS_DIR = "uploads"
TOLERANCE = 0.6  # Lower = more strict matching (0.4-0.6 is typical)
MODEL = "hog"  # Use "cnn" for better accuracy (requires GPU/more compute)


def ensure_directories() -> None:
    """
    Ensure that required directories exist.
    Creates known_faces and uploads directories if they don't exist.
    """
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    print(f"[UTILS] Directories ensured: {KNOWN_FACES_DIR}, {UPLOADS_DIR}")


def load_known_faces() -> Tuple[list, list]:
    """
    Load all known face encodings from the known_faces directory.
    
    The function expects image files in the known_faces folder where
    the filename (without extension) is used as the student name.
    
    Example:
        known_faces/
            John_Doe.jpg       -> Student name: "John Doe"
            Jane_Smith.png     -> Student name: "Jane Smith"
    
    Returns:
        Tuple containing:
            - list of face encodings (numpy arrays)
            - list of corresponding student names
    """
    known_encodings = []
    known_names = []
    
    # Supported image extensions
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    if not os.path.exists(KNOWN_FACES_DIR):
        print(f"[UTILS] Known faces directory not found: {KNOWN_FACES_DIR}")
        ensure_directories()
        return [], []
    
    # Iterate through all files in the known_faces directory
    for filename in os.listdir(KNOWN_FACES_DIR):
        filepath = os.path.join(KNOWN_FACES_DIR, filename)
        
        # Skip directories and non-image files
        if not os.path.isfile(filepath):
            continue
            
        # Check file extension
        _, ext = os.path.splitext(filename)
        if ext.lower() not in valid_extensions:
            continue
        
        try:
            # Load the image
            image = face_recognition.load_image_file(filepath)
            
            # Get face encodings (may return multiple if multiple faces in image)
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                # Use the first face found in the image
                known_encodings.append(encodings[0])
                
                # Extract student name from filename (replace underscores with spaces)
                name = os.path.splitext(filename)[0].replace("_", " ")
                known_names.append(name)
                
                print(f"[UTILS] Loaded face encoding for: {name}")
            else:
                print(f"[UTILS] WARNING: No face found in {filename}")
                
        except Exception as e:
            print(f"[UTILS] ERROR loading {filename}: {str(e)}")
    
    print(f"[UTILS] Loaded {len(known_encodings)} known face(s)")
    return known_encodings, known_names


def save_uploaded_image(image_data: bytes, prefix: str = "capture") -> str:
    """
    Save an uploaded image to the uploads directory.
    
    Args:
        image_data: Raw image bytes from the upload
        prefix: Prefix for the saved filename
    
    Returns:
        str: Path to the saved image file
    """
    ensure_directories()
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{prefix}_{timestamp}.jpg"
    filepath = os.path.join(UPLOADS_DIR, filename)
    
    # Save the image
    try:
        # Try to open and resave to ensure valid image format
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image.save(filepath, 'JPEG', quality=95)
        print(f"[UTILS] Saved uploaded image: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"[UTILS] ERROR saving image: {str(e)}")
        # Fallback: save raw bytes
        with open(filepath, 'wb') as f:
            f.write(image_data)
        return filepath


def recognize_face(
    image_path: str,
    known_encodings: list,
    known_names: list,
    tolerance: float = TOLERANCE
) -> Tuple[Optional[str], Optional[float]]:
    """
    Attempt to recognize a face in an image by comparing against known faces.
    
    Args:
        image_path: Path to the image to analyze
        known_encodings: List of known face encodings
        known_names: List of corresponding student names
        tolerance: Matching tolerance (lower = more strict)
    
    Returns:
        Tuple containing:
            - Student name if recognized, None otherwise
            - Confidence score (inverse of face distance), None if not recognized
    """
    if len(known_encodings) == 0:
        print("[UTILS] No known faces loaded for comparison")
        return None, None
    
    try:
        # Load the image to analyze
        image = face_recognition.load_image_file(image_path)
        
        # Detect face locations in the image
        face_locations = face_recognition.face_locations(image, model=MODEL)
        
        if len(face_locations) == 0:
            print("[UTILS] No face detected in the uploaded image")
            return None, None
        
        # Get face encodings for detected faces
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) == 0:
            print("[UTILS] Could not encode detected face")
            return None, None
        
        # Use the first face found
        face_encoding = face_encodings[0]
        
        # Compare against all known faces
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        # Find the best match
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        # Check if the best match is within tolerance
        if best_distance <= tolerance:
            matched_name = known_names[best_match_index]
            # Convert distance to confidence (0-1 scale, higher is better)
            confidence = 1.0 - best_distance
            
            print(f"[UTILS] Face recognized: {matched_name} (confidence: {confidence:.2%})")
            return matched_name, confidence
        else:
            print(f"[UTILS] Face not recognized (best distance: {best_distance:.3f})")
            return None, None
            
    except Exception as e:
        print(f"[UTILS] ERROR during face recognition: {str(e)}")
        return None, None


def recognize_face_from_bytes(
    image_data: bytes,
    known_encodings: list,
    known_names: list,
    tolerance: float = TOLERANCE
) -> Tuple[Optional[str], Optional[float]]:
    """
    Recognize a face directly from image bytes without saving to disk first.
    
    Args:
        image_data: Raw image bytes
        known_encodings: List of known face encodings
        known_names: List of corresponding student names
        tolerance: Matching tolerance
    
    Returns:
        Tuple containing:
            - Student name if recognized, None otherwise
            - Confidence score, None if not recognized
    """
    if len(known_encodings) == 0:
        print("[UTILS] No known faces loaded for comparison")
        return None, None
    
    try:
        # Load image from bytes
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert PIL image to numpy array (required by face_recognition)
        image_array = np.array(pil_image)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(image_array, model=MODEL)
        
        if len(face_locations) == 0:
            print("[UTILS] No face detected in the image")
            return None, None
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        
        if len(face_encodings) == 0:
            print("[UTILS] Could not encode detected face")
            return None, None
        
        # Use the first face
        face_encoding = face_encodings[0]
        
        # Compare against known faces
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        # Find best match
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        if best_distance <= tolerance:
            matched_name = known_names[best_match_index]
            confidence = 1.0 - best_distance
            print(f"[UTILS] Face recognized: {matched_name} (confidence: {confidence:.2%})")
            return matched_name, confidence
        else:
            print(f"[UTILS] Face not recognized (best distance: {best_distance:.3f})")
            return None, None
            
    except Exception as e:
        print(f"[UTILS] ERROR during face recognition: {str(e)}")
        return None, None


def add_known_face(image_data: bytes, student_name: str) -> bool:
    """
    Add a new known face to the system.
    
    Args:
        image_data: Raw image bytes containing the face
        student_name: Name of the student
    
    Returns:
        bool: True if successfully added, False otherwise
    """
    ensure_directories()
    
    try:
        # Load and validate image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array for face detection
        image_array = np.array(pil_image)
        
        # Verify a face can be detected
        face_locations = face_recognition.face_locations(image_array, model=MODEL)
        
        if len(face_locations) == 0:
            print(f"[UTILS] No face detected in image for {student_name}")
            return False
        
        # Save the image with student name as filename
        filename = student_name.replace(" ", "_") + ".jpg"
        filepath = os.path.join(KNOWN_FACES_DIR, filename)
        
        pil_image.save(filepath, 'JPEG', quality=95)
        print(f"[UTILS] Added known face for: {student_name}")
        return True
        
    except Exception as e:
        print(f"[UTILS] ERROR adding known face: {str(e)}")
        return False


def get_registered_students() -> list:
    """
    Get a list of all registered students (based on files in known_faces folder).
    
    Returns:
        list: List of student names
    """
    students = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    if not os.path.exists(KNOWN_FACES_DIR):
        return students
    
    for filename in os.listdir(KNOWN_FACES_DIR):
        _, ext = os.path.splitext(filename)
        if ext.lower() in valid_extensions:
            name = os.path.splitext(filename)[0].replace("_", " ")
            students.append(name)
    
    return sorted(students)


if __name__ == "__main__":
    # Test loading known faces
    ensure_directories()
    encodings, names = load_known_faces()
    print(f"\nLoaded {len(names)} known face(s):")
    for name in names:
        print(f"  - {name}")
