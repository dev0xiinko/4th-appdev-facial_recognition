# FaceTrack Attendance System
## User Guide

---

<div align="center">

# 👁️ FaceTrack

**Facial Recognition Attendance System**

*Easy, Fast, and Accurate Attendance Tracking*

</div>

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Taking Attendance](#taking-attendance)
4. [Registering New Students](#registering-new-students)
5. [Viewing Attendance Records](#viewing-attendance-records)
6. [Using the ESP32-CAM](#using-the-esp32-cam)
7. [Using Fallback Options](#using-fallback-options)
8. [Understanding LED Indicators](#understanding-led-indicators)
9. [Tips for Best Results](#tips-for-best-results)
10. [Frequently Asked Questions](#frequently-asked-questions)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing the Dashboard

1. Open your web browser (Chrome, Firefox, Edge, or Safari)
2. Enter the dashboard URL provided by your administrator:
   ```
   http://[SERVER-IP]:5000
   ```
   Example: `http://192.168.1.13:5000`

3. The dashboard will load automatically

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   👁️ FaceTrack                                                         │
│   Attendance Recognition System                                         │
│                                                                         │
│   ┌──────────────────────┐  ┌──────────────────────────┐               │
│   │ 📸 Capture Attendance│  │ 👤 Register New Student  │               │
│   └──────────────────────┘  └──────────────────────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Dashboard Overview

### Main Sections

```
┌─────────────────────────────────────────────────────────────────────────┐
│  1️⃣ HEADER                                                              │
│  ─────────────────────────────────────────────────────────────────────  │
│  Logo, ESP32-CAM status indicator, and current date/time                │
├─────────────────────────────────────────────────────────────────────────┤
│  2️⃣ CONTROL BUTTONS                                                     │
│  ─────────────────────────────────────────────────────────────────────  │
│  Buttons to capture attendance and register students                    │
├─────────────────────────────────────────────────────────────────────────┤
│  3️⃣ STATISTICS CARDS                                                    │
│  ─────────────────────────────────────────────────────────────────────  │
│  Quick overview of today's attendance and system stats                  │
├─────────────────────────────────────────────────────────────────────────┤
│  4️⃣ ATTENDANCE LOG              │  5️⃣ REGISTERED STUDENTS              │
│  ───────────────────────────────│  ────────────────────────────────────│
│  Today's attendance records     │  List of all registered students     │
│  with timestamps                │  with attendance status              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 ESP32-CAM: Ready | Camera device is connected and working |
| 🔴 ESP32-CAM: Offline | Camera device is not connected |
| ✓ Present | Student has checked in today |
| — Not checked in | Student hasn't checked in yet |

### Statistics Cards

| Card | Description |
|------|-------------|
| **Today's Attendance** | Number of unique students present today |
| **Total Scans Today** | Total number of face scans performed |
| **Registered Students** | Total students in the system |
| **All-Time Records** | Total attendance records ever logged |

---

## Taking Attendance

### Method 1: Using ESP32-CAM (Primary)

**Step 1:** Position the student in front of the ESP32-CAM camera

```
     ┌─────────────┐
     │  ESP32-CAM  │
     │   📷        │
     └─────────────┘
           │
           ▼
     ┌─────────────┐
     │   Student   │
     │    😊       │  ← Face the camera
     │             │    About 1-2 feet away
     └─────────────┘
```

**Step 2:** Click the **"📸 Capture Attendance"** button on the dashboard

**Step 3:** Wait for the result:
- ✅ **Green notification**: Attendance logged successfully
- ⚠️ **Yellow notification**: Already logged or face not recognized
- ❌ **Red notification**: Error occurred

### Method 2: Using Webcam (Fallback)

If ESP32-CAM is not available:

1. Click **"🎥 Webcam Attendance"** button
2. Allow camera access when prompted
3. Position face in the camera view
4. Click **"📸 Capture"**

### Method 3: Upload Photo (Fallback)

1. Click **"📁 Upload Photo"** button
2. Select or drag an image file
3. Click **"📤 Submit"**

---

## Registering New Students

### Before You Begin

For best results, ensure:
- ✅ Good lighting on the student's face
- ✅ Student is facing the camera directly
- ✅ No sunglasses or face coverings
- ✅ Neutral facial expression

### Method 1: Using ESP32-CAM

**Step 1:** Click **"👤 Register New Student"**

**Step 2:** Enter the student's full name
```
┌─────────────────────────────────────────┐
│  Register New Student                   │
│                                         │
│  Enter name: [John Smith            ]   │
│                                         │
│  [Cancel]  [📸 Capture & Register]     │
└─────────────────────────────────────────┘
```

**Step 3:** Position the student in front of ESP32-CAM

**Step 4:** Click **"📸 Capture & Register"**

**Step 5:** Wait for confirmation message

### Method 2: Using Webcam

1. Click **"🎥 Webcam Register"**
2. Enter the student's name
3. Camera will start automatically
4. Position face in camera view
5. Click **"📸 Capture"**

### Method 3: Upload Photo

1. Click **"📁 Upload & Register"**
2. Enter the student's name
3. Select or drag a photo file
4. Click **"📤 Submit"**

### Photo Requirements

| Requirement | Good ✅ | Bad ❌ |
|-------------|---------|--------|
| Lighting | Even, well-lit | Dark, harsh shadows |
| Angle | Front-facing | Side profile |
| Expression | Neutral | Extreme expressions |
| Accessories | None | Sunglasses, masks |
| Distance | 1-3 feet | Too close/far |
| Background | Simple | Busy, distracting |

---

## Viewing Attendance Records

### Today's Attendance

The **"Today's Attendance Log"** panel shows:
- Student name with avatar
- Check-in timestamp
- Recognition confidence percentage

```
┌─────────────────────────────────────────────────────────────┐
│  Today's Attendance Log                         [↻ Refresh] │
├─────────────────────────────────────────────────────────────┤
│  👤 John Smith        10:30:45 AM       ████████░░  85.2%  │
│  👤 Jane Doe          10:28:12 AM       █████████░  92.1%  │
│  👤 Bob Johnson       09:45:33 AM       ████████░░  88.7%  │
└─────────────────────────────────────────────────────────────┘
```

### Understanding Confidence Scores

| Score | Meaning |
|-------|---------|
| 90-100% | Excellent match |
| 80-89% | Good match |
| 70-79% | Acceptable match |
| 60-69% | Marginal match |
| Below 60% | Not recognized |

### Refreshing Data

Click the **"↻ Refresh"** button to update the attendance list with the latest records.

---

## Using the ESP32-CAM

### Device Overview

```
         ┌───────────────────────┐
         │    ┌─────────────┐    │
         │    │   CAMERA    │    │
         │    │   LENS      │    │
         │    └─────────────┘    │
         │                       │
         │   💡 FLASH LED       │
         │                       │
         │   [RESET BUTTON]      │
         └───────────────────────┘
               ESP32-CAM
```

### Positioning the Camera

**Recommended Setup:**

```
                    ┌─────────────┐
                    │  ESP32-CAM  │
                    │     📷      │
                    └─────────────┘
                          │
                     1-2 feet
                          │
                          ▼
    ┌─────────────────────────────────────────┐
    │                                         │
    │              STUDENT                    │
    │                                         │
    │        Face centered in view            │
    │        Good lighting on face            │
    │        Looking directly at camera       │
    │                                         │
    └─────────────────────────────────────────┘
```

### Status Indicator

The dashboard shows the ESP32-CAM connection status:

| Status | Meaning | Action |
|--------|---------|--------|
| 🟢 Ready | Connected and working | None needed |
| 🔴 Offline | Not connected | Check power and WiFi |
| 🟡 Checking... | Verifying connection | Wait a moment |

---

## Using Fallback Options

When ESP32-CAM is unavailable, use these alternatives:

### Webcam Capture

Use your computer's built-in or USB webcam:

```
┌─────────────────────────────────────────┐
│  Webcam Capture                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │     [Live Camera Feed]          │   │
│  │                                 │   │
│  │         👤                      │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Cancel]           [📸 Capture]        │
└─────────────────────────────────────────┘
```

**Steps:**
1. Click webcam button
2. Camera starts automatically
3. Position face in view
4. Click Capture

### File Upload

Upload an existing photo:

```
┌─────────────────────────────────────────┐
│  Upload Photo                           │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │     📁 Click or drag file       │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Cancel]           [📤 Submit]         │
└─────────────────────────────────────────┘
```

**Supported formats:** JPG, JPEG, PNG, GIF, BMP

---

## Understanding LED Indicators

The ESP32-CAM has a built-in LED that indicates the result:

### LED Flash Patterns

| Pattern | Visual | Meaning |
|---------|--------|---------|
| **1 long blink** | ━━━━━ | ✅ Attendance logged successfully |
| **2 long blinks** | ━━ ━━ | ✅ Student registered successfully |
| **2 quick blinks** | ─ ─ | ⚠️ Duplicate (already logged recently) |
| **3 quick blinks** | ─ ─ ─ | ⚠️ Face not recognized |
| **5 rapid blinks** | ····· | ❌ Error occurred |
| **Solid flash** | ━━━━━━━━ | 📸 Taking photo |

### During Capture

```
1. Button clicked → LED solid ON (flash)
2. Photo taken → LED OFF
3. Processing → Wait...
4. Result → LED blinks pattern
```

---

## Tips for Best Results

### For Accurate Recognition

✅ **DO:**
- Ensure good, even lighting on the face
- Face the camera directly
- Remove hats, sunglasses, or masks
- Keep a neutral expression
- Stand 1-2 feet from the camera
- Register multiple photos per student if needed

❌ **DON'T:**
- Capture in low light conditions
- Stand too close or too far
- Tilt head at extreme angles
- Cover parts of the face
- Rush the capture process

### For Fast Check-ins

1. **Set up a dedicated station** with good lighting
2. **Train students** on proper positioning
3. **Use ESP32-CAM** for fastest results
4. **Avoid duplicate scans** within 5 minutes

### Lighting Tips

```
     GOOD LIGHTING                    BAD LIGHTING
     ═════════════                    ════════════

     💡      💡                            💡
       \    /                               │
        \  /                                │
         👤                                 👤
          │                            (shadows on
     (even light                       one side)
      on face)
```

---

## Frequently Asked Questions

### General Questions

**Q: How many students can be registered?**
> There is no hard limit. The system can handle hundreds of students efficiently.

**Q: How accurate is the recognition?**
> The system typically achieves 85-95% accuracy with good lighting and proper registration photos.

**Q: Can the same student check in multiple times?**
> The system prevents duplicate check-ins within 5 minutes.

**Q: What happens if the internet goes down?**
> The system works on local network. Internet is not required, but devices must be on the same WiFi network.

### Registration Questions

**Q: Can I update a student's photo?**
> Yes, simply register them again with the same name. The new photo will replace the old one.

**Q: What if a student isn't recognized?**
> Try registering them with a new photo in better lighting conditions.

**Q: Can I delete a student?**
> Contact your administrator to remove student photos from the system.

### Attendance Questions

**Q: How do I view past attendance records?**
> The dashboard shows today's records. Contact your administrator for historical data.

**Q: What time zone does the system use?**
> The system uses the server's local time zone.

**Q: Can attendance be manually added?**
> Currently, attendance is only recorded through face recognition.

---

## Troubleshooting

### Common Issues and Solutions

#### "Face not recognized"

| Cause | Solution |
|-------|----------|
| Poor lighting | Move to a well-lit area |
| Wrong angle | Face the camera directly |
| Not registered | Register the student first |
| Photo quality | Re-register with a better photo |

#### "ESP32-CAM Offline"

| Cause | Solution |
|-------|----------|
| Power issue | Check USB connection |
| WiFi disconnected | Restart the device |
| Wrong network | Ensure same WiFi network |
| Server down | Contact administrator |

#### "Capture timeout"

| Cause | Solution |
|-------|----------|
| Slow network | Wait and try again |
| Device busy | Restart ESP32-CAM |
| Server overloaded | Wait a moment |

#### Webcam not working

| Cause | Solution |
|-------|----------|
| Permission denied | Allow camera access in browser |
| Camera in use | Close other apps using camera |
| Browser issue | Try a different browser |

### Getting Help

If you encounter issues not covered here:

1. **Note the error message** displayed
2. **Take a screenshot** if possible
3. **Contact your system administrator**

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        QUICK REFERENCE CARD                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TAKING ATTENDANCE                                                      │
│  ─────────────────                                                      │
│  1. Position student in front of camera                                 │
│  2. Click "📸 Capture Attendance"                                       │
│  3. Wait for confirmation                                               │
│                                                                         │
│  REGISTERING STUDENTS                                                   │
│  ────────────────────                                                   │
│  1. Click "👤 Register New Student"                                     │
│  2. Enter student name                                                  │
│  3. Position student, click Capture                                     │
│                                                                         │
│  LED SIGNALS                                                            │
│  ───────────                                                            │
│  ━━━━━      = Attendance logged ✅                                      │
│  ━━ ━━     = Registered ✅                                              │
│  ─ ─       = Duplicate ⚠️                                               │
│  ─ ─ ─     = Not recognized ⚠️                                          │
│  ·····     = Error ❌                                                   │
│                                                                         │
│  FALLBACK OPTIONS                                                       │
│  ────────────────                                                       │
│  🎥 Webcam Attendance/Register - Use computer camera                    │
│  📁 Upload Photo - Use existing photo file                              │
│                                                                         │
│  BEST PRACTICES                                                         │
│  ──────────────                                                         │
│  • Good lighting on face                                                │
│  • Face camera directly                                                 │
│  • 1-2 feet from camera                                                 │
│  • No sunglasses or masks                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

<div align="center">

## Need Help?

Contact your system administrator for assistance.

---

*FaceTrack Attendance System - User Guide v1.0*

*© 2026 - All Rights Reserved*

</div>
