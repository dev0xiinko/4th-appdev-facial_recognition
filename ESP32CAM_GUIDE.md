# ESP32-CAM Setup Guide
## Facial Recognition Attendance System

---

## Table of Contents

1. [Hardware Overview](#hardware-overview)
2. [Required Components](#required-components)
3. [Software Installation](#software-installation)
4. [Wiring Diagrams](#wiring-diagrams)
5. [Arduino IDE Configuration](#arduino-ide-configuration)
6. [Code Configuration](#code-configuration)
7. [Uploading the Code](#uploading-the-code)
8. [Testing & Verification](#testing--verification)
9. [LED Status Codes](#led-status-codes)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

---

## Hardware Overview

### ESP32-CAM AI-Thinker Module

The ESP32-CAM is a low-cost development board with an ESP32-S chip, an OV2640 camera, and a microSD card slot.

```
┌─────────────────────────────────────────────────────────────┐
│                    ESP32-CAM AI-THINKER                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │                  ┌─────────────┐                    │   │
│   │                  │             │                    │   │
│   │                  │   OV2640    │                    │   │
│   │                  │   CAMERA    │                    │   │
│   │                  │   2MP       │                    │   │
│   │                  │             │                    │   │
│   │                  └─────────────┘                    │   │
│   │                                                     │   │
│   │    ┌──────┐                         ┌──────┐       │   │
│   │    │FLASH │                         │ LED  │       │   │
│   │    │ LED  │                         │(RED) │       │   │
│   │    └──────┘                         └──────┘       │   │
│   │      GPIO4                                          │   │
│   │                                                     │   │
│   │   ┌─────────────────────────────────────────────┐   │   │
│   │   │              ESP32-S CHIP                   │   │   │
│   │   │         Dual-core 240MHz                    │   │   │
│   │   │         520KB SRAM + 4MB PSRAM              │   │   │
│   │   └─────────────────────────────────────────────┘   │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   3V3 ●  ●  ●  ●  ●  ●  ●  ● 5V                            │
│   GND ●  ●  ●  ●  ●  ●  ●  ● GND                           │
│                                                             │
│         [RESET BUTTON]        [IPEX ANTENNA CONNECTOR]     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Specifications

| Feature | Specification |
|---------|---------------|
| **Processor** | ESP32-S (Xtensa dual-core 32-bit LX6) |
| **Clock Speed** | Up to 240 MHz |
| **SRAM** | 520 KB |
| **PSRAM** | 4 MB (external) |
| **Flash** | 4 MB |
| **Camera** | OV2640, 2 Megapixel |
| **Max Resolution** | 1600 x 1200 |
| **WiFi** | 802.11 b/g/n, 2.4 GHz |
| **Bluetooth** | v4.2 BR/EDR and BLE |
| **Flash LED** | White LED on GPIO 4 |
| **Operating Voltage** | 5V (USB) or 3.3V |
| **Dimensions** | 40.5 x 27 x 4.5 mm |

---

## Required Components

### Essential Hardware

| # | Component | Description | Where to Buy | Est. Price |
|---|-----------|-------------|--------------|------------|
| 1 | ESP32-CAM | AI-Thinker module with OV2640 | AliExpress, Amazon | $5-10 |
| 2 | ESP32-CAM-MB | USB programmer board | AliExpress, Amazon | $2-3 |
| 3 | Micro-USB Cable | Data cable (not charge-only) | Any electronics store | $2-3 |

### Alternative Programming Method

If you don't have ESP32-CAM-MB:

| # | Component | Description | Est. Price |
|---|-----------|-------------|------------|
| 1 | FTDI Adapter | FT232RL or CP2102 (3.3V/5V) | $3-5 |
| 2 | Jumper Wires | Female-to-female, 5 pieces | $1-2 |
| 3 | Breadboard | Optional, for stable connections | $2-3 |

### Optional Accessories

| Component | Purpose |
|-----------|---------|
| 5V 2A Power Adapter | Stable power supply |
| 3D Printed Case | Protection and mounting |
| External Antenna | Better WiFi range |
| LED Ring Light | Improved face lighting |

---

## Software Installation

### Step 1: Download Arduino IDE

1. Go to: https://www.arduino.cc/en/software
2. Download Arduino IDE 2.x for your operating system
3. Install and launch Arduino IDE

### Step 2: Add ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences** (or Arduino IDE → Settings on macOS)
3. Find **"Additional boards manager URLs"**
4. Add this URL:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
5. Click **OK**

```
┌─────────────────────────────────────────────────────────────┐
│  Preferences                                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Additional boards manager URLs:                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ https://raw.githubusercontent.com/espressif/        │   │
│  │ arduino-esp32/gh-pages/package_esp32_index.json     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                              [OK]  [Cancel]                 │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Install ESP32 Boards

1. Go to **Tools → Board → Boards Manager**
2. Search for **"esp32"**
3. Find **"esp32 by Espressif Systems"**
4. Click **Install** (this may take a few minutes)

```
┌─────────────────────────────────────────────────────────────┐
│  Boards Manager                                             │
├─────────────────────────────────────────────────────────────┤
│  Search: esp32                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  esp32 by Espressif Systems          [INSTALL]     │   │
│  │  Version: 2.x.x                                     │   │
│  │                                                     │   │
│  │  Boards included in this package:                   │   │
│  │  • ESP32 Dev Module                                 │   │
│  │  • AI Thinker ESP32-CAM  ← This one!               │   │
│  │  • ESP32-WROVER                                     │   │
│  │  • ...                                              │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Install ArduinoJson Library

1. Go to **Sketch → Include Library → Manage Libraries**
2. Search for **"ArduinoJson"**
3. Find **"ArduinoJson by Benoit Blanchon"**
4. Click **Install**

```
┌─────────────────────────────────────────────────────────────┐
│  Library Manager                                            │
├─────────────────────────────────────────────────────────────┤
│  Search: ArduinoJson                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  ArduinoJson                          [INSTALL]     │   │
│  │  by Benoit Blanchon                                 │   │
│  │  Version: 7.x.x                                     │   │
│  │                                                     │   │
│  │  A simple and efficient JSON library for           │   │
│  │  embedded C++                                        │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Step 5: Install USB Drivers (if needed)

**For CH340 chip (common on cheap programmers):**
- Windows: Download from https://sparks.gogo.co.nz/ch340.html
- macOS: Usually automatic, or use Homebrew
- Linux: Usually built-in

**For CP2102 chip:**
- Download from Silicon Labs: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

---

## Wiring Diagrams

### Option A: Using ESP32-CAM-MB Programmer (Recommended)

This is the easiest method - just plug and play!

```
┌─────────────────────────────────────────────────────────────┐
│                ESP32-CAM-MB PROGRAMMER                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    ┌─────────────────────────────────┐                     │
│    │                                 │                     │
│    │         ESP32-CAM               │                     │
│    │      (plugs in here)            │                     │
│    │           ↓ ↓ ↓                 │                     │
│    │    ● ● ● ● ● ● ● ●              │                     │
│    │    │ │ │ │ │ │ │ │              │                     │
│    ├────┴─┴─┴─┴─┴─┴─┴─┴──────────────┤                     │
│    │                                 │                     │
│    │     [IO0]   [RST]               │                     │
│    │    BUTTON  BUTTON               │                     │
│    │                                 │                     │
│    │         ┌───────┐               │                     │
│    │         │ MICRO │               │                     │
│    │         │  USB  │               │  ← Connect USB here │
│    │         └───────┘               │                     │
│    │                                 │                     │
│    └─────────────────────────────────┘                     │
│                                                             │
│  Steps:                                                     │
│  1. Insert ESP32-CAM into MB board (camera facing up)      │
│  2. Connect Micro-USB cable                                 │
│  3. Select correct COM port in Arduino IDE                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Option B: Using FTDI USB-to-Serial Adapter

```
┌─────────────────────────────────────────────────────────────┐
│                    FTDI WIRING DIAGRAM                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│       ESP32-CAM                         FTDI Adapter        │
│    ┌─────────────┐                    ┌─────────────┐       │
│    │             │                    │             │       │
│    │    5V   ●───┼────────────────────┼───●  VCC    │       │
│    │             │    (Red wire)      │             │       │
│    │   GND   ●───┼────────────────────┼───●  GND    │       │
│    │             │    (Black wire)    │             │       │
│    │   U0T   ●───┼────────────────────┼───●  RX     │       │
│    │             │    (Green wire)    │             │       │
│    │   U0R   ●───┼────────────────────┼───●  TX     │       │
│    │             │    (Yellow wire)   │             │       │
│    │   IO0   ●───┼──┐                 │             │       │
│    │             │  │  (Orange wire)  │             │       │
│    │   GND   ●───┼──┘                 │             │       │
│    │             │  ↑                 │             │       │
│    └─────────────┘  │                 └──────┬──────┘       │
│                     │                        │              │
│         Connect IO0 to GND                   │              │
│         ONLY during upload!              [USB PORT]         │
│                                              │              │
│                                         To Computer         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

   WIRING TABLE
   ┌───────────────┬───────────────┬─────────────┐
   │   ESP32-CAM   │  FTDI Adapter │ Wire Color  │
   ├───────────────┼───────────────┼─────────────┤
   │      5V       │     VCC       │    Red      │
   │     GND       │     GND       │   Black     │
   │     U0T       │      RX       │   Green     │
   │     U0R       │      TX       │  Yellow     │
   │     IO0       │     GND*      │  Orange     │
   └───────────────┴───────────────┴─────────────┘
   * IO0 to GND only during programming!
```

### ESP32-CAM Pinout Reference

```
                         ESP32-CAM PINOUT
                    ┌─────────────────────┐
                    │      [CAMERA]       │
                    │     ┌───────┐       │
                    │     │OV2640 │       │
                    │     └───────┘       │
                    │                     │
              3V3  ─┤●  1            16 ●├─ 5V
              GND  ─┤●  2            15 ●├─ GND
             IO12  ─┤●  3            14 ●├─ IO13
             IO13  ─┤●  4            13 ●├─ IO15
             IO15  ─┤●  5            12 ●├─ IO14
             IO14  ─┤●  6            11 ●├─ IO2
              IO2  ─┤●  7            10 ●├─ IO4 (FLASH LED)
  (FLASH) →  IO4  ─┤●  8             9 ●├─ IO0 (BOOT)
             U0R  ─┤●  9             8 ●├─ U0T
             U0T  ─┤● 10             7 ●├─ VCC
             GND  ─┤● 11             6 ●├─ 3V3
              5V  ─┤● 12             5 ●├─ GND
                    │                     │
                    │      [RESET]        │
                    │        [●]          │
                    └─────────────────────┘

   KEY PINS:
   ┌────────┬──────────────────────────────────┐
   │  Pin   │  Function                        │
   ├────────┼──────────────────────────────────┤
   │  5V    │  Power input (from USB)          │
   │  GND   │  Ground                          │
   │  U0T   │  UART TX (connect to FTDI RX)    │
   │  U0R   │  UART RX (connect to FTDI TX)    │
   │  IO0   │  Boot mode (GND = programming)   │
   │  IO4   │  Flash LED (built-in white LED)  │
   │  3V3   │  3.3V output                     │
   └────────┴──────────────────────────────────┘
```

---

## Arduino IDE Configuration

### Step 1: Open the Sketch

1. **File → Open**
2. Navigate to your project folder:
   ```
   /home/iinko/appdev/facial/esp32cam_attendance/
   ```
3. Select **esp32cam_attendance.ino**
4. Click **Open**

### Step 2: Select Board

Go to **Tools → Board → esp32** and select:

```
AI Thinker ESP32-CAM
```

### Step 3: Configure Board Settings

Go to **Tools** menu and configure:

```
┌─────────────────────────────────────────────────────────────┐
│  ARDUINO IDE - TOOLS MENU SETTINGS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Board:              "AI Thinker ESP32-CAM"                 │
│                                                             │
│  Upload Speed:       "115200"                               │
│                                                             │
│  CPU Frequency:      "240MHz (WiFi/BT)"                     │
│                                                             │
│  Flash Frequency:    "80MHz"                                │
│                                                             │
│  Flash Mode:         "QIO"                                  │
│                                                             │
│  Partition Scheme:   "Huge APP (3MB No OTA/1MB SPIFFS)"    │
│                                                             │
│  Core Debug Level:   "None"                                 │
│                                                             │
│  Erase All Flash:    "Disabled"                            │
│                                                             │
│  Port:               "/dev/ttyUSB0" (or your COM port)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Settings Summary Table

| Setting | Value | Notes |
|---------|-------|-------|
| Board | AI Thinker ESP32-CAM | Must match your hardware |
| Upload Speed | 115200 | Can try 921600 if stable |
| CPU Frequency | 240MHz (WiFi/BT) | Maximum performance |
| Flash Frequency | 80MHz | Standard setting |
| Flash Mode | QIO | Quad I/O for faster access |
| Partition Scheme | Huge APP (3MB No OTA) | More space for code |
| Port | Your USB port | Check Device Manager/dmesg |

---

## Code Configuration

### Open the Sketch and Find Configuration Section

Look for these lines near the top of the code:

```cpp
// =============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// =============================================================================

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server IP address (without http:// and port)
const char* serverIP = "192.168.1.13";
const int serverPort = 5000;
```

### Configuration Parameters

| Parameter | What to Enter | Example |
|-----------|---------------|---------|
| `ssid` | Your WiFi network name | `"MyHomeWiFi"` |
| `password` | Your WiFi password | `"MyPassword123"` |
| `serverIP` | Your server's IP address | `"192.168.1.13"` |
| `serverPort` | Flask server port | `5000` |

### Finding Your Server IP Address

**Linux:**
```bash
hostname -I | awk '{print $1}'
# Example output: 192.168.1.13
```

**macOS:**
```bash
ipconfig getifaddr en0
# Example output: 192.168.1.13
```

**Windows:**
```cmd
ipconfig | findstr /i "IPv4"
# Example output: IPv4 Address. . . . . : 192.168.1.13
```

### Optional Settings

```cpp
// Poll interval in milliseconds (how often to check for commands)
const unsigned long POLL_INTERVAL = 500;  // 500ms = responsive

// Flash LED settings
const bool USE_FLASH = true;           // Enable/disable flash
const int FLASH_BRIGHTNESS = 100;      // 0-255 brightness
```

### Complete Configuration Example

```cpp
// =============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// =============================================================================

// WiFi credentials
const char* ssid = "MyHomeNetwork";        // ← Your WiFi name
const char* password = "SecurePass123!";   // ← Your WiFi password

// Server IP address
const char* serverIP = "192.168.1.13";     // ← Your server IP
const int serverPort = 5000;

// Poll interval (500ms is good for responsiveness)
const unsigned long POLL_INTERVAL = 500;

// Flash LED settings
const bool USE_FLASH = true;
const int FLASH_BRIGHTNESS = 100;
```

---

## Uploading the Code

### Method A: Using ESP32-CAM-MB (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│              UPLOAD PROCESS WITH MB BOARD                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: Prepare Hardware                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Insert ESP32-CAM into MB board                   │   │
│  │  • Ensure camera faces UP                           │   │
│  │  • Connect Micro-USB cable to computer              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 2: Enter Programming Mode                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Press and HOLD the [IO0] button                 │   │
│  │  2. While holding IO0, press [RST] button once      │   │
│  │  3. Release [RST] button                            │   │
│  │  4. Release [IO0] button                            │   │
│  │                                                     │   │
│  │     [IO0]  [RST]                                    │   │
│  │       ↓      ↓                                      │   │
│  │      ███    ███                                     │   │
│  │     HOLD   PRESS                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 3: Upload                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Click Upload button (→) in Arduino IDE           │   │
│  │  • Wait for "Connecting..." message                 │   │
│  │  • Wait for upload to complete                      │   │
│  │  • Look for "Done uploading"                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 4: Run the Code                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Press [RST] button to restart                    │   │
│  │  • Open Serial Monitor (115200 baud)                │   │
│  │  • Watch for startup messages                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Method B: Using FTDI Adapter

```
┌─────────────────────────────────────────────────────────────┐
│              UPLOAD PROCESS WITH FTDI ADAPTER                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: Wire the Connections                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ESP32-CAM  ←→  FTDI                                │   │
│  │     5V      →   VCC                                 │   │
│  │    GND      →   GND                                 │   │
│  │    U0T      →   RX                                  │   │
│  │    U0R      →   TX                                  │   │
│  │    IO0      →   GND  ← IMPORTANT for upload!        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 2: Connect and Upload                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Connect IO0 to GND (jumper wire)                │   │
│  │  2. Connect FTDI USB to computer                    │   │
│  │  3. Select correct COM port in Arduino IDE          │   │
│  │  4. Click Upload button (→)                         │   │
│  │  5. Wait for "Done uploading"                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  STEP 3: Run the Code                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. DISCONNECT IO0 from GND  ← IMPORTANT!           │   │
│  │  2. Press RST button (or power cycle)               │   │
│  │  3. Open Serial Monitor (115200 baud)               │   │
│  │  4. Watch for startup messages                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Upload Progress Indicators

```
ARDUINO IDE OUTPUT WINDOW:

Sketch uses 1234567 bytes (94%) of program storage space.
Global variables use 65432 bytes (20%) of dynamic memory.

esptool.py v4.x
Connecting........_____
Chip is ESP32-D0WDQ6 (revision 1)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration
Crystal is 40MHz
MAC: aa:bb:cc:dd:ee:ff
Uploading stub...
Running stub...
Stub running...
Changing baud rate to 115200
Changed.
Configuring flash size...
Flash will be erased from 0x00001000 to 0x00xyz000...
Compressed 1234567 bytes to 654321...
Writing at 0x00010000... (3%)
Writing at 0x00020000... (7%)
...
Writing at 0x00180000... (100%)
Wrote 1234567 bytes (654321 compressed) at 0x00001000 in 45.6 seconds

Leaving...
Hard resetting via RTS pin...

✓ Done uploading.
```

---

## Testing & Verification

### Step 1: Open Serial Monitor

1. **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. Press **RST** button on ESP32-CAM

### Step 2: Check Startup Messages

You should see:

```
========================================
  ESP32-CAM Attendance System
  COMMAND-BASED CAPTURE MODE
========================================
Poll URL: http://192.168.1.13:5000/api/command/poll
Recognize URL: http://192.168.1.13:5000/api/recognize
PSRAM found - using VGA resolution
Camera initialized successfully

Connecting to WiFi: YourWiFiName
......
WiFi connected!
IP Address: 192.168.1.50

System ready! Waiting for commands...
========================================
```

### Step 3: Verify Server Connection

1. Make sure your Flask server is running:
   ```bash
   cd /home/iinko/appdev/facial
   source venv/bin/activate
   python app.py
   ```

2. Open dashboard in browser:
   ```
   http://192.168.1.13:5000
   ```

3. Click **"Capture Attendance"** button

4. Watch Serial Monitor for:
   ```
   *** CAPTURE COMMAND RECEIVED ***
   Mode: attendance
   
   ========================================
   Capturing image...
   Image captured: 28453 bytes
   Sending to server (mode: attendance)...
   Response code: 200
   Response: {"status":"success","name":"John Doe"...}
   ✓ ATTENDANCE LOGGED!
     Student: John Doe
     Confidence: 85.4%
   ========================================
   ```

### Step 4: Verify LED Flash

When capture is triggered:
1. **Flash LED** (white) turns ON briefly
2. Image is captured
3. LED turns OFF
4. Status LED blinks according to result

---

## LED Status Codes

The ESP32-CAM uses its built-in flash LED (GPIO 4) to indicate status:

```
┌─────────────────────────────────────────────────────────────┐
│                    LED STATUS CODES                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STARTUP                                                    │
│  ───────                                                    │
│  ███░░░███░░░███░░░     3 quick blinks = WiFi connected    │
│  ███░███░███░███░███░   10 rapid blinks = WiFi failed      │
│                                                             │
│  CAPTURE RESULT                                             │
│  ──────────────                                             │
│                                                             │
│  ████████████░░░░░░░    1 long blink (500ms)               │
│                         = Attendance logged successfully ✓  │
│                                                             │
│  ████████░░░████████░░░ 2 long blinks (400ms each)         │
│                         = Student registered successfully ✓ │
│                                                             │
│  ███░░░███░░░          2 quick blinks (150ms each)         │
│                         = Duplicate entry ○                 │
│                                                             │
│  ██░░██░░██░░          3 quick blinks (100ms each)         │
│                         = Face not recognized ✗             │
│                                                             │
│  █░█░█░█░█░            5 rapid blinks (50ms each)          │
│                         = Error occurred !                  │
│                                                             │
│  DURING CAPTURE                                             │
│  ──────────────                                             │
│  ████████████████████   Solid ON during flash               │
│                         = Taking photo                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

LEGEND:
  ███ = LED ON
  ░░░ = LED OFF
```

### Quick Reference Table

| Pattern | Duration | Meaning |
|---------|----------|---------|
| 1 long blink | 500ms | ✓ Attendance logged |
| 2 long blinks | 400ms each | ✓ Student registered |
| 2 quick blinks | 150ms each | ○ Duplicate (already logged) |
| 3 quick blinks | 100ms each | ✗ Face not recognized |
| 5 rapid blinks | 50ms each | ! Error occurred |
| 3 blinks at startup | 100ms each | WiFi connected |
| 10 rapid blinks at startup | 50ms each | WiFi connection failed |

---

## Troubleshooting

### Upload Problems

| Error | Cause | Solution |
|-------|-------|----------|
| "Failed to connect to ESP32" | Not in programming mode | Hold IO0, press RST, then upload |
| "No serial port detected" | Driver not installed | Install CH340 or CP2102 driver |
| "Timed out waiting for packet header" | Connection issue | Check wiring, try different USB cable |
| "A fatal error occurred: Packet content transfer incomplete" | Power issue | Use 5V 2A power supply |

### Camera Problems

| Error | Cause | Solution |
|-------|-------|----------|
| "Camera init failed with error 0x20001" | Ribbon cable loose | Reseat camera ribbon cable |
| "Camera capture failed" | Camera not initialized | Check camera connector, restart |
| "No PSRAM found" | PSRAM not detected | Check if your board has PSRAM |

### WiFi Problems

| Error | Cause | Solution |
|-------|-------|----------|
| WiFi won't connect | Wrong credentials | Double-check SSID and password |
| "WiFi connection failed" | Out of range | Move closer to router |
| Disconnects frequently | Signal interference | Change WiFi channel, add external antenna |
| Won't connect | 5GHz network | ESP32 only supports 2.4GHz WiFi |

### Server Communication Problems

| Error | Cause | Solution |
|-------|-------|----------|
| "HTTP request failed" | Wrong IP address | Verify server IP with `hostname -I` |
| "Connection refused" | Server not running | Start Flask server |
| "Timeout" | Firewall blocking | Allow port 5000 in firewall |
| No response | Different network | Ensure same WiFi network |

### Power Problems

| Symptom | Cause | Solution |
|---------|-------|----------|
| Random restarts | Insufficient power | Use 5V 2A power supply |
| "Brownout detector triggered" | Voltage drop | Better power supply, shorter USB cable |
| LED very dim | Low power | Check power source |

### How to Check if ESP32-CAM is Working

```bash
# From your server, test if ESP32 is polling:
# Watch the Flask server logs for:
# "GET /api/command/poll HTTP/1.1" 200

# Or check manually:
curl http://YOUR_SERVER_IP:5000/api/command/poll
# Should return: {"status":"no_command"}
```

---

## Maintenance

### Regular Checks

| Task | Frequency | How To |
|------|-----------|--------|
| Clean camera lens | Weekly | Soft cloth, no liquid |
| Check connections | Monthly | Reseat ribbon cable |
| Update firmware | As needed | Re-upload sketch |
| Check WiFi signal | If issues | Move closer to router |

### Cleaning the Camera Lens

```
1. Power off the ESP32-CAM
2. Use a soft, lint-free cloth
3. Gently wipe the camera lens
4. Do NOT use water or cleaning solutions
5. Let dry completely before powering on
```

### Reseating the Camera Ribbon Cable

```
┌─────────────────────────────────────────────────────────────┐
│              RESEATING CAMERA RIBBON CABLE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Locate the black connector latch                        │
│     ┌─────────────┐                                         │
│     │   CAMERA    │                                         │
│     └──────┬──────┘                                         │
│            │ ribbon cable                                   │
│     ┌──────┴──────┐                                         │
│     │ ▓▓▓▓▓▓▓▓▓▓▓ │ ← black latch                          │
│     └─────────────┘                                         │
│                                                             │
│  2. Gently lift the black latch upward                      │
│                                                             │
│  3. Slide ribbon cable out                                  │
│                                                             │
│  4. Reinsert ribbon cable (gold contacts facing DOWN)       │
│                                                             │
│  5. Press black latch down to secure                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Factory Reset

If you need to start fresh:

1. Erase all flash in Arduino IDE:
   - Tools → Erase All Flash Before Sketch Upload → **Enabled**
2. Upload the sketch again
3. Set Erase All Flash back to **Disabled**

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│              ESP32-CAM QUICK REFERENCE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HARDWARE                                                   │
│  ─────────                                                  │
│  Board:        AI Thinker ESP32-CAM                         │
│  Camera:       OV2640 (2MP)                                 │
│  Flash LED:    GPIO 4                                       │
│  Boot Pin:     GPIO 0 (IO0)                                 │
│                                                             │
│  ARDUINO IDE SETTINGS                                       │
│  ────────────────────                                       │
│  Board:        AI Thinker ESP32-CAM                         │
│  Upload Speed: 115200                                       │
│  Partition:    Huge APP (3MB No OTA)                        │
│  Port:         /dev/ttyUSB0 or COMx                         │
│                                                             │
│  PROGRAMMING MODE                                           │
│  ────────────────                                           │
│  1. Hold IO0 button                                         │
│  2. Press RST button                                        │
│  3. Release both                                            │
│  4. Upload code                                             │
│  5. Press RST to run                                        │
│                                                             │
│  SERIAL MONITOR                                             │
│  ──────────────                                             │
│  Baud Rate:    115200                                       │
│                                                             │
│  LED SIGNALS                                                │
│  ───────────                                                │
│  1 long    = Attendance logged ✓                            │
│  2 long    = Student registered ✓                           │
│  2 quick   = Duplicate ○                                    │
│  3 quick   = Unknown face ✗                                 │
│  5 rapid   = Error !                                        │
│                                                             │
│  WIFI                                                       │
│  ────                                                       │
│  Frequency:    2.4 GHz only                                 │
│  Protocol:     802.11 b/g/n                                 │
│                                                             │
│  POWER                                                      │
│  ─────                                                      │
│  Voltage:      5V                                           │
│  Recommended:  5V 2A adapter                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Need Help?

### Diagnostic Commands

Run these on your server to diagnose issues:

```bash
# Check if server is running
curl http://localhost:5000/health

# Check ESP32 polling
# Watch Flask logs for repeated GET /api/command/poll requests

# Test capture command manually
curl -X POST -H "Content-Type: application/json" \
    -d '{"mode":"attendance"}' \
    http://localhost:5000/api/command/capture

# Check command result
curl http://localhost:5000/api/command/result
```

### Serial Monitor Debug

Add this to your code for more debug info:
```cpp
Serial.setDebugOutput(true);  // Already in setup()
```

---

*ESP32-CAM Setup Guide - Version 1.0*
*Last Updated: January 2026*
