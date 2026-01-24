# Facial Recognition Attendance System
## Complete Documentation Guide

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Software Requirements](#software-requirements)
4. [Installation Guide](#installation-guide)
5. [ESP32-CAM Setup](#esp32-cam-setup)
6. [Server Configuration](#server-configuration)
7. [Using the Web Dashboard](#using-the-web-dashboard)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Configuration](#advanced-configuration)

---

## System Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐         ┌──────────────────┐         ┌─────────────┐
    │   ESP32-CAM  │◄───────►│   Flask Server   │◄───────►│  Dashboard  │
    │              │  WiFi   │                  │   HTTP  │   (Browser) │
    │  • Camera    │         │  • Face Recog.   │         │             │
    │  • Flash LED │         │  • SQLite DB     │         │  • View     │
    │  • Polling   │         │  • REST API      │         │  • Capture  │
    └──────────────┘         └──────────────────┘         │  • Register │
                                      │                   └─────────────┘
                                      │
                             ┌────────┴────────┐
                             │                 │
                      ┌──────┴──────┐   ┌──────┴──────┐
                      │ known_faces │   │  uploads    │
                      │   folder    │   │   folder    │
                      │             │   │             │
                      │ Student     │   │ Captured    │
                      │ photos      │   │ images      │
                      └─────────────┘   └─────────────┘
```

### Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ATTENDANCE WORKFLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

  USER                    DASHBOARD                 SERVER                ESP32-CAM
   │                          │                        │                      │
   │  Click "Capture"         │                        │                      │
   ├─────────────────────────►│                        │                      │
   │                          │  POST /command/capture │                      │
   │                          ├───────────────────────►│                      │
   │                          │                        │  Store command       │
   │                          │                        │◄─────────────────────┤
   │                          │                        │  GET /command/poll   │
   │                          │                        ├─────────────────────►│
   │                          │                        │  Return "capture"    │
   │                          │                        │◄─────────────────────┤
   │                          │                        │                      │ Flash LED
   │                          │                        │                      │ Take Photo
   │                          │                        │  POST /recognize     │
   │                          │                        │◄─────────────────────┤
   │                          │                        │  Face Recognition    │
   │                          │                        │  Log Attendance      │
   │                          │  GET /command/result   │                      │
   │                          ├───────────────────────►│                      │
   │                          │  Return result         │                      │
   │                          │◄───────────────────────┤                      │
   │  Show toast notification │                        │                      │
   │◄─────────────────────────┤                        │                      │
   │                          │                        │                      │
```

---

## Hardware Requirements

### Essential Components

| Component | Model/Specification | Quantity | Estimated Price |
|-----------|---------------------|----------|-----------------|
| ESP32-CAM | AI-Thinker with OV2640 | 1 | $5-10 |
| USB Programmer | ESP32-CAM-MB or FTDI | 1 | $2-5 |
| USB Cable | Micro-USB | 1 | $2-3 |
| Power Supply | 5V 2A (optional but recommended) | 1 | $5-8 |

### ESP32-CAM Specifications

```
┌─────────────────────────────────────────────┐
│           ESP32-CAM AI-THINKER              │
├─────────────────────────────────────────────┤
│  Processor    : ESP32-S (Dual-core 240MHz)  │
│  RAM          : 520KB SRAM + 4MB PSRAM      │
│  Flash        : 4MB                         │
│  Camera       : OV2640 (2MP, 1600x1200)     │
│  WiFi         : 802.11 b/g/n                │
│  Flash LED    : Built-in (GPIO 4)           │
│  Voltage      : 5V (via USB) or 3.3V        │
│  Dimensions   : 40.5 x 27 x 4.5 mm          │
└─────────────────────────────────────────────┘
```

### Pinout Diagram

```
                      ESP32-CAM AI-THINKER
                    ┌─────────────────────┐
                    │      ┌───────┐      │
                    │      │CAMERA │      │
                    │      │OV2640 │      │
                    │      └───────┘      │
                    │                     │
              3V3  ─┤●                   ●├─ 5V
              GND  ─┤●                   ●├─ GND  
             IO12  ─┤●                   ●├─ IO13
             IO14  ─┤●                   ●├─ IO15
              IO2  ─┤●                   ●├─ IO14
              IO4  ─┤●  [FLASH LED]     ●├─ IO0 ◄── GND for programming
             U0R   ─┤●                   ●├─ VOT
             U0T   ─┤●                   ●├─ VOR
                    │      [RESET]        │
                    │        [●]          │
                    └─────────────────────┘
                           ┌─────┐
                           │IPEX │ (Antenna connector)
                           └─────┘
```

### FTDI Wiring (If Not Using MB Board)

```
    ESP32-CAM                    FTDI Adapter
    ┌────────┐                   ┌────────┐
    │   5V   ├───────────────────┤  VCC   │
    │  GND   ├───────────────────┤  GND   │
    │  U0T   ├───────────────────┤  RX    │
    │  U0R   ├───────────────────┤  TX    │
    │  IO0   ├───────┐           │        │
    └────────┘       │           └────────┘
                     │
                    GND  (Connect during upload only)
```

### Server Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Dual-core | Quad-core |
| RAM | 4 GB | 8 GB |
| Storage | 1 GB free | 10 GB free |
| OS | Ubuntu 20.04+ / Windows 10+ / macOS 10.15+ | Ubuntu 22.04+ |
| Python | 3.10 | 3.11+ |
| Network | Same WiFi as ESP32-CAM | Wired Ethernet |

---

## Software Requirements

### Server Dependencies

```
Flask>=3.0.0          # Web framework
face-recognition>=1.3.0   # Face detection & recognition
Pillow>=10.0.0        # Image processing
numpy>=1.24.0         # Numerical operations
Werkzeug>=3.0.0       # HTTP utilities
setuptools            # For pkg_resources
```

### Arduino IDE Requirements

- **Arduino IDE**: Version 2.0+ (or 1.8.x)
- **ESP32 Board Support**: espressif/arduino-esp32
- **ArduinoJson Library**: Version 6.x or 7.x

### System Dependencies (Linux)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-pip python3-venv cmake build-essential
sudo apt install -y libopenblas-dev liblapack-dev libjpeg-dev
```

---

## Installation Guide

### Step 1: Clone/Download Project

```bash
cd /path/to/your/projects
# If using git:
# git clone <repository-url> facial
# Or create directory:
mkdir facial
cd facial
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install setuptools  # Required for face_recognition_models
```

> **Note**: The `face_recognition` library requires `dlib`, which compiles from source. This may take 5-15 minutes.

### Step 4: Verify Installation

```bash
python -c "import face_recognition; print('Face recognition OK')"
python -c "from flask import Flask; print('Flask OK')"
```

### Step 5: Initialize and Run Server

```bash
python app.py
```

Expected output:
```
============================================================
  Facial Recognition Attendance System
============================================================
[UTILS] Directories ensured: known_faces, uploads
[DATABASE] Database initialized successfully
[UTILS] Loaded 0 known face(s)
[APP] Loaded 0 known face(s)

[APP] Server ready!
...
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

---

## ESP32-CAM Setup

### Step 1: Install Arduino IDE & Board Support

1. Download Arduino IDE from https://www.arduino.cc/en/software
2. Open Arduino IDE → File → Preferences
3. Add to "Additional Board URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Tools → Board → Boards Manager → Search "esp32" → Install

### Step 2: Install ArduinoJson Library

1. Sketch → Include Library → Manage Libraries
2. Search "ArduinoJson"
3. Install by Benoit Blanchon (version 6.x or 7.x)

### Step 3: Configure the Sketch

Open `esp32cam_attendance/esp32cam_attendance.ino` and update:

```cpp
// WiFi credentials - CHANGE THESE
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// Server IP - CHANGE THIS to your server's IP
const char* serverIP = "192.168.1.13";  // Find with: hostname -I (Linux)
const int serverPort = 5000;
```

### Step 4: Board Settings

| Setting | Value |
|---------|-------|
| Board | AI Thinker ESP32-CAM |
| CPU Frequency | 240MHz (WiFi/BT) |
| Flash Frequency | 80MHz |
| Flash Mode | QIO |
| Partition Scheme | Huge APP (3MB No OTA/1MB SPIFFS) |
| Upload Speed | 115200 |
| Port | (Your USB port) |

### Step 5: Upload Process

**Using ESP32-CAM-MB:**
1. Insert ESP32-CAM into MB board
2. Connect USB cable
3. Press and hold IO0 button on MB board
4. Press RST button (while holding IO0)
5. Release both buttons
6. Click Upload in Arduino IDE
7. After upload, press RST to run

**Using FTDI Adapter:**
1. Connect wires as shown in wiring diagram
2. Connect IO0 to GND
3. Power on (connect USB)
4. Click Upload
5. After upload, disconnect IO0 from GND
6. Press RST button or power cycle

### Step 6: Verify ESP32-CAM Connection

Open Serial Monitor (115200 baud):
```
========================================
  ESP32-CAM Attendance System
  COMMAND-BASED CAPTURE MODE
========================================
Poll URL: http://192.168.1.13:5000/api/command/poll
Recognize URL: http://192.168.1.13:5000/api/recognize
PSRAM found - using VGA resolution
Camera initialized successfully

Connecting to WiFi: YourWiFi
.....
WiFi connected!
IP Address: 192.168.1.xx

System ready! Waiting for commands...
========================================
```

---

## Server Configuration

### File Structure

```
facial/
├── app.py                 # Main Flask application
├── database.py            # SQLite database functions
├── utils.py               # Face recognition utilities
├── requirements.txt       # Python dependencies
├── attendance.db          # SQLite database (auto-created)
├── templates/
│   └── dashboard.html     # Web dashboard
├── known_faces/           # Student photos (add here)
│   ├── John_Doe.jpg
│   ├── Jane_Smith.png
│   └── ...
├── uploads/               # Captured images (auto-saved)
│   └── esp32_20260122_*.jpg
└── esp32cam_attendance/
    └── esp32cam_attendance.ino  # Arduino sketch
```

### Configuration Options

Edit `utils.py` to adjust recognition settings:

```python
# Recognition tolerance (0.0 - 1.0)
# Lower = more strict, fewer false positives
# Higher = more lenient, fewer false negatives
TOLERANCE = 0.6  # Default, good balance

# Face detection model
# "hog" = faster, works on CPU
# "cnn" = more accurate, requires GPU/more compute
MODEL = "hog"
```

Edit `app.py` for timing settings:

```python
# Minimum minutes between same student's attendance logs
DUPLICATE_THRESHOLD_MINUTES = 5
```

### Adding Known Faces

1. Take clear, front-facing photos of each student
2. Name files with student names (underscores = spaces):
   ```
   known_faces/
   ├── John_Doe.jpg        → "John Doe"
   ├── Jane_Smith.png      → "Jane Smith"
   ├── Bob_Johnson.jpeg    → "Bob Johnson"
   ```
3. Reload faces via dashboard or API:
   ```bash
   curl -X POST http://localhost:5000/api/reload
   ```

### Photo Requirements for Best Results

| Requirement | Recommendation |
|-------------|----------------|
| Lighting | Well-lit, minimal shadows |
| Angle | Front-facing, looking at camera |
| Expression | Neutral expression |
| Resolution | At least 200x200 pixels |
| Format | JPG, JPEG, PNG, GIF, BMP |
| Faces per image | One face only |

---

## Using the Web Dashboard

### Accessing the Dashboard

Open in browser: `http://YOUR_SERVER_IP:5000`

### Dashboard Features

```
┌─────────────────────────────────────────────────────────────────────────┐
│  👁️ FaceTrack                              ESP32-CAM: Ready    📅 Date │
│     Attendance Recognition System                               🕐 Time │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐  ┌──────────────────────────┐                │
│  │ 📸 Capture Attendance│  │ 👤 Register New Student  │                │
│  └──────────────────────┘  └──────────────────────────┘                │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Today's     │ │ Total Scans │ │ Registered  │ │ All-Time    │       │
│  │ Attendance  │ │ Today       │ │ Students    │ │ Records     │       │
│  │     5       │ │     12      │ │     8       │ │    156      │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Today's Attendance Log              │  Registered Students            │
│  ─────────────────────               │  ────────────────────           │
│  │ J │ John Doe    10:30  85.2%    │  │ J │ John Doe    ✓ Present    │
│  │ J │ Jane Smith  10:25  92.1%    │  │ J │ Jane Smith  ✓ Present    │
│  │ B │ Bob Johnson 09:45  88.7%    │  │ B │ Bob Johnson — Not in     │
│  │ ...                              │  │ ...                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Capture Attendance

1. Position student in front of ESP32-CAM
2. Click **"📸 Capture Attendance"**
3. ESP32-CAM flashes and captures image
4. Result shown as toast notification:
   - ✓ Green: Attendance logged with name and confidence
   - ⚠ Yellow: Duplicate (already logged) or unknown face
   - ✗ Red: Error occurred

### Register New Student

1. Click **"👤 Register New Student"**
2. Enter student name in the modal
3. Position student in front of ESP32-CAM
4. Click **"📸 Capture & Register"**
5. On success, student is added to system

### LED Feedback Codes

| LED Pattern | Meaning |
|-------------|---------|
| 1 long blink (500ms) | ✓ Attendance logged |
| 2 long blinks (400ms) | ✓ Student registered |
| 2 quick blinks (150ms) | ○ Duplicate entry |
| 3 quick blinks (100ms) | ✗ Face not recognized |
| 5 rapid blinks (50ms) | ! Error occurred |

---

## API Reference

### Base URL
```
http://YOUR_SERVER_IP:5000
```

### Endpoints

#### POST /api/command/capture
Request ESP32-CAM to capture an image.

**Request:**
```json
{
    "mode": "attendance",  // or "register"
    "name": "John Doe"     // required for register mode
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Capture command sent (attendance)",
    "mode": "attendance"
}
```

---

#### GET /api/command/poll
ESP32-CAM polls this endpoint for commands.

**Response (command pending):**
```json
{
    "status": "capture",
    "mode": "attendance",
    "student_name": null
}
```

**Response (no command):**
```json
{
    "status": "no_command"
}
```

---

#### GET /api/command/result
Get result of last capture.

**Response:**
```json
{
    "status": "success",
    "name": "John Doe",
    "confidence": 0.8542,
    "record_id": 42,
    "timestamp": "2026-01-22T10:30:00.000000"
}
```

---

#### POST /api/recognize
Receive and process image from ESP32-CAM.

**Headers:**
```
Content-Type: image/jpeg
X-Capture-Mode: attendance  (or register)
X-Student-Name: John Doe    (for register mode)
```

**Body:** Raw JPEG image bytes

**Response (recognized):**
```json
{
    "status": "success",
    "name": "John Doe",
    "confidence": 0.8542,
    "record_id": 42,
    "timestamp": "2026-01-22T10:30:00.000000"
}
```

**Response (unknown):**
```json
{
    "status": "unknown",
    "message": "Face not recognized"
}
```

**Response (duplicate):**
```json
{
    "status": "duplicate",
    "name": "John Doe",
    "message": "Already logged within 5 minutes"
}
```

---

#### GET /api/attendance
Get attendance logs.

**Query Parameters:**
- `limit` (int): Maximum records (default: 100)
- `today` (bool): Only today's records

**Example:**
```bash
curl "http://localhost:5000/api/attendance?today=true&limit=50"
```

**Response:**
```json
{
    "status": "success",
    "count": 5,
    "logs": [
        {
            "id": 42,
            "student_name": "John Doe",
            "timestamp": "2026-01-22 10:30:00",
            "image_path": "uploads/esp32_20260122_103000.jpg",
            "confidence": 0.8542
        }
    ]
}
```

---

#### GET /api/stats
Get attendance statistics.

**Response:**
```json
{
    "status": "success",
    "total_logs": 156,
    "unique_students": 8,
    "today_logs": 12,
    "today_unique_students": 5
}
```

---

#### GET /api/students
Get list of registered students.

**Response:**
```json
{
    "status": "success",
    "count": 8,
    "students": ["Bob Johnson", "Jane Smith", "John Doe"]
}
```

---

#### POST /api/reload
Reload known faces from folder.

**Response:**
```json
{
    "status": "success",
    "message": "Loaded 8 known face(s)",
    "students": ["Bob Johnson", "Jane Smith", "John Doe"]
}
```

---

#### GET /health
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "known_faces_count": 8,
    "timestamp": "2026-01-22T10:30:00.000000"
}
```

---

## Troubleshooting

### Server Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: flask` | Activate venv: `source venv/bin/activate` |
| `No module named 'pkg_resources'` | Install: `pip install setuptools` |
| `face_recognition_models` error | Run: `pip install face-recognition-models` |
| Port 5000 in use | Change port in `app.py` or kill process: `pkill -f "python app.py"` |
| No faces loading | Check file extensions (.jpg, .png) and file permissions |

### ESP32-CAM Issues

| Problem | Solution |
|---------|----------|
| Upload fails | Hold IO0 button while pressing RST, then upload |
| Camera init failed | Check camera ribbon cable connection |
| WiFi won't connect | Verify SSID/password, check 2.4GHz (not 5GHz) |
| No response from server | Check IP address, firewall settings |
| Brownout detector triggered | Use better power supply (5V 2A) |
| Image quality poor | Improve lighting, clean camera lens |

### Recognition Issues

| Problem | Solution |
|---------|----------|
| Face not recognized | Use better quality reference photo |
| Wrong person recognized | Lower TOLERANCE in utils.py (e.g., 0.5) |
| Too many false negatives | Raise TOLERANCE (e.g., 0.65) |
| "No face detected" | Improve lighting, face camera directly |
| Slow recognition | Use MODEL = "hog" instead of "cnn" |

### Network Issues

| Problem | Solution |
|---------|----------|
| ESP32 can't reach server | Ensure same network, check firewall |
| Dashboard won't load | Verify server is running on 0.0.0.0 |
| Timeout errors | Increase timeout in ESP32 code |

### Finding Your Server IP

```bash
# Linux
hostname -I | awk '{print $1}'

# macOS
ipconfig getifaddr en0

# Windows
ipconfig | findstr /i "IPv4"
```

---

## Advanced Configuration

### Running in Production

Use Gunicorn instead of Flask's development server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Running as a Service (Linux)

Create `/etc/systemd/system/facial-attendance.service`:

```ini
[Unit]
Description=Facial Recognition Attendance System
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/facial
ExecStart=/path/to/facial/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable facial-attendance
sudo systemctl start facial-attendance
```

### Using CNN Model for Better Accuracy

In `utils.py`:
```python
MODEL = "cnn"  # Requires NVIDIA GPU with CUDA
```

Install CUDA-enabled dlib:
```bash
pip uninstall dlib
pip install dlib --no-cache-dir  # With CUDA toolkit installed
```

### Multiple ESP32-CAMs

The system supports multiple ESP32-CAMs polling the same server. Each camera will:
- Receive the same capture command
- First to respond logs the attendance
- Duplicate prevention handles multiple captures

### Backup Database

```bash
# Backup
cp attendance.db attendance_backup_$(date +%Y%m%d).db

# Restore
cp attendance_backup_20260122.db attendance.db
```

### Export Attendance to CSV

```python
import sqlite3
import csv

conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM attendance_logs")

with open('attendance_export.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Student', 'Timestamp', 'Image', 'Confidence'])
    writer.writerows(cursor.fetchall())

conn.close()
```

---

## Support

### Logs Location

- Server logs: Console output (stdout)
- ESP32 logs: Serial Monitor (115200 baud)
- Database: `attendance.db` (SQLite)

### Useful Commands

```bash
# Check server status
curl http://localhost:5000/health

# View recent attendance
curl http://localhost:5000/api/attendance?limit=10

# Reload faces after adding new photos
curl -X POST http://localhost:5000/api/reload

# Test capture command
curl -X POST -H "Content-Type: application/json" \
    -d '{"mode":"attendance"}' \
    http://localhost:5000/api/command/capture
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial release with command-based capture |

---

## License

MIT License - Free to use and modify for personal and commercial projects.

---

*Documentation generated for Facial Recognition Attendance System*
