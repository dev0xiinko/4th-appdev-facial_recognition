# Facial Recognition Attendance System

A Python-based facial recognition attendance system designed to work with ESP32-CAM devices. The system uses Flask as the backend framework and the `face_recognition` library for face detection and recognition.

## Features

- **ESP32-CAM Integration**: Receives images via HTTP POST requests
- **Face Recognition**: Uses dlib-based face_recognition library for accurate face detection
- **SQLite Database**: Stores attendance logs with timestamps and confidence scores
- **Web Dashboard**: Real-time attendance monitoring with a modern UI
- **REST API**: Full API for integration with other systems
- **Duplicate Prevention**: Prevents logging the same student multiple times within a configurable time window

## Project Structure

```
facial/
├── app.py                 # Flask server with REST API endpoints
├── database.py            # SQLite helper functions
├── utils.py               # Face recognition utility functions
├── requirements.txt       # Python dependencies
├── templates/
│   └── dashboard.html     # Web dashboard template
├── known_faces/           # Store student images here (filename = student name)
├── uploads/               # Incoming images from ESP32-CAM
└── attendance.db          # SQLite database (created automatically)
```

## Installation

### Prerequisites

- Python 3.10+
- cmake (for building dlib)
- Build tools (gcc, g++, make)

### 1. Install System Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv cmake build-essential
sudo apt install -y libopenblas-dev liblapack-dev libjpeg-dev
```

### 2. Create Virtual Environment

```bash
cd facial
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note**: The `face_recognition` library requires `dlib`, which can take several minutes to compile.

## Setup

### Add Known Faces

1. Place student photos in the `known_faces/` folder
2. Name each file with the student's name (underscores become spaces)
   - Example: `John_Doe.jpg` → Student name: "John Doe"
   - Example: `Jane_Smith.png` → Student name: "Jane Smith"
3. Ensure each image contains a clear, front-facing photo with good lighting
4. One face per image is recommended

### Start the Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`

## API Endpoints

### POST `/api/recognize`
Receive and process an image from ESP32-CAM.

**Request**: Image data as raw body or multipart form-data (key: `image` or `file`)

**Response**:
```json
// Success
{
    "status": "success",
    "name": "John Doe",
    "confidence": 0.8542,
    "record_id": 1,
    "timestamp": "2026-01-22T10:30:00.000000"
}

// Unknown face
{
    "status": "unknown",
    "message": "Face not recognized"
}

// Duplicate (same student within 5 minutes)
{
    "status": "duplicate",
    "name": "John Doe",
    "message": "Already logged within 5 minutes"
}
```

### POST `/api/register`
Register a new student face.

**Request**: Multipart form-data
- `name`: Student name (required)
- `image`: Image file (required)

**Response**:
```json
{
    "status": "success",
    "message": "Successfully registered John Doe",
    "name": "John Doe"
}
```

### GET `/api/attendance`
Get attendance logs.

**Query Parameters**:
- `limit`: Maximum records (default: 100)
- `today`: Set to "true" for today's records only

**Response**:
```json
{
    "status": "success",
    "count": 5,
    "logs": [
        {
            "id": 1,
            "student_name": "John Doe",
            "timestamp": "2026-01-22 10:30:00",
            "confidence": 0.85
        }
    ]
}
```

### GET `/api/stats`
Get attendance statistics.

### GET `/api/students`
Get list of registered students.

### POST `/api/reload`
Reload known faces from the known_faces folder.

### GET `/` or `/dashboard`
Web dashboard for viewing attendance.

### GET `/health`
Health check endpoint.

## ESP32-CAM Integration

### Arduino Code Example

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:5000/api/recognize";

void sendPhoto() {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        return;
    }

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");
    
    int httpResponseCode = http.POST(fb->buf, fb->len);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(response);
    } else {
        Serial.printf("Error: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    
    http.end();
    esp_camera_fb_return(fb);
}

void setup() {
    Serial.begin(115200);
    
    // Initialize camera (add your camera pin configuration)
    // ...
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected!");
}

void loop() {
    sendPhoto();
    delay(5000);  // Send every 5 seconds
}
```

## Configuration

### Recognition Tolerance

Edit `utils.py` to adjust recognition sensitivity:

```python
TOLERANCE = 0.6  # Lower = more strict (0.4-0.6 typical)
MODEL = "hog"    # Use "cnn" for better accuracy (requires GPU)
```

### Duplicate Prevention

Edit `app.py` to change the time threshold:

```python
DUPLICATE_THRESHOLD_MINUTES = 5  # Minutes between same student logs
```

## Testing

### Test with curl

```bash
# Test recognition with an image file
curl -X POST -H "Content-Type: image/jpeg" \
    --data-binary @test_image.jpg \
    http://localhost:5000/api/recognize

# Get attendance logs
curl http://localhost:5000/api/attendance

# Get today's attendance
curl http://localhost:5000/api/attendance?today=true

# Get statistics
curl http://localhost:5000/api/stats

# Get registered students
curl http://localhost:5000/api/students

# Register a new student
curl -X POST -F "name=John Doe" -F "image=@photo.jpg" \
    http://localhost:5000/api/register
```

## Troubleshooting

### No face detected
- Ensure the image has good lighting
- Face should be clearly visible and front-facing
- Try a higher resolution image

### Recognition accuracy is low
- Use high-quality, well-lit photos for known faces
- Adjust the `TOLERANCE` value in `utils.py`
- Consider using `MODEL = "cnn"` for better accuracy (slower)

### dlib installation fails
- Ensure cmake is installed
- Install build-essential package
- Try upgrading pip before installation

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## License

MIT License - Feel free to use and modify for your projects.
