/**
 * ESP32-CAM Facial Recognition Attendance System
 * COMMAND-BASED CAPTURE MODE
 * 
 * This sketch polls the server for capture commands from the web dashboard.
 * When a command is received, it captures an image and sends it to the server.
 * 
 * Hardware: ESP32-CAM AI-Thinker module
 * 
 * Instructions:
 * 1. Update WiFi credentials (ssid and password)
 * 2. Update serverIP with your server's IP address
 * 3. Select "AI Thinker ESP32-CAM" board in Arduino IDE
 * 4. Upload using an FTDI adapter or ESP32-CAM-MB programmer
 * 
 * Libraries needed:
 * - ESP32 board support (install via Board Manager)
 * - ArduinoJson (install via Library Manager)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include "esp_timer.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// =============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// =============================================================================

// WiFi credentials
const char* ssid = "Adrian";
const char* password = "09226611";

// Server IP address (without http:// and port)
const char* serverIP = "192.168.1.13";
const int serverPort = 5000;

// Poll interval in milliseconds (how often to check for commands)
const unsigned long POLL_INTERVAL = 500;  // 500ms = responsive

// Flash LED settings
const bool USE_FLASH = true;
const int FLASH_BRIGHTNESS = 100;  // 0-255

// =============================================================================
// ESP32-CAM AI-THINKER PIN DEFINITIONS
// =============================================================================

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

#define LED_GPIO_NUM       4

// =============================================================================
// GLOBAL VARIABLES
// =============================================================================

unsigned long lastPollTime = 0;
bool wifiConnected = false;
String currentMode = "";
String studentName = "";

// Server URLs
String pollUrl;
String recognizeUrl;

// =============================================================================
// CAMERA INITIALIZATION
// =============================================================================

bool initCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_LATEST;
    
    if (psramFound()) {
        config.frame_size = FRAMESIZE_VGA;     // 640x480
        config.jpeg_quality = 10;               // Higher quality for face recognition
        config.fb_count = 2;
        config.fb_location = CAMERA_FB_IN_PSRAM;
        Serial.println("PSRAM found - using VGA resolution");
    } else {
        config.frame_size = FRAMESIZE_CIF;     // 352x288
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.fb_location = CAMERA_FB_IN_DRAM;
        Serial.println("No PSRAM - using CIF resolution");
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x\n", err);
        return false;
    }

    // Optimize camera settings for face capture
    sensor_t* s = esp_camera_sensor_get();
    if (s != NULL) {
        s->set_brightness(s, 1);      // Slightly brighter
        s->set_contrast(s, 0);
        s->set_saturation(s, 0);
        s->set_whitebal(s, 1);
        s->set_awb_gain(s, 1);
        s->set_wb_mode(s, 0);
        s->set_exposure_ctrl(s, 1);
        s->set_aec2(s, 1);
        s->set_gain_ctrl(s, 1);
        s->set_agc_gain(s, 0);
        s->set_bpc(s, 1);
        s->set_wpc(s, 1);
        s->set_raw_gma(s, 1);
        s->set_lenc(s, 1);
        s->set_hmirror(s, 0);
        s->set_vflip(s, 0);
        s->set_dcw(s, 1);
    }

    Serial.println("Camera initialized successfully");
    return true;
}

// =============================================================================
// LED FLASH CONTROL
// =============================================================================

void setupFlash() {
    // ESP32 Arduino Core 3.x API: ledcAttach(pin, freq, resolution)
    ledcAttach(LED_GPIO_NUM, 5000, 8);
    ledcWrite(LED_GPIO_NUM, 0);
}

void flashOn() {
    if (USE_FLASH) {
        ledcWrite(LED_GPIO_NUM, FLASH_BRIGHTNESS);
    }
}

void flashOff() {
    ledcWrite(LED_GPIO_NUM, 0);
}

void blinkLED(int times, int delayMs) {
    for (int i = 0; i < times; i++) {
        ledcWrite(LED_GPIO_NUM, 50);
        delay(delayMs);
        ledcWrite(LED_GPIO_NUM, 0);
        delay(delayMs);
    }
}

// Quick status blink (non-blocking visual feedback)
void quickBlink() {
    ledcWrite(LED_GPIO_NUM, 20);
    delay(50);
    ledcWrite(LED_GPIO_NUM, 0);
}

// =============================================================================
// WIFI CONNECTION
// =============================================================================

bool connectWiFi() {
    Serial.println();
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("WiFi connected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        wifiConnected = true;
        blinkLED(3, 100);
        return true;
    } else {
        Serial.println();
        Serial.println("WiFi connection FAILED!");
        wifiConnected = false;
        blinkLED(10, 50);
        return false;
    }
}

// =============================================================================
// POLL FOR COMMANDS
// =============================================================================

bool pollForCommand() {
    if (WiFi.status() != WL_CONNECTED) {
        return false;
    }
    
    HTTPClient http;
    http.begin(pollUrl);
    http.setTimeout(5000);
    
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String response = http.getString();
        http.end();
        
        // Parse JSON response
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, response);
        
        if (error) {
            Serial.println("JSON parse error in poll");
            return false;
        }
        
        const char* status = doc["status"];
        
        if (strcmp(status, "capture") == 0) {
            // Capture command received!
            currentMode = String((const char*)doc["mode"]);
            
            if (doc.containsKey("student_name") && !doc["student_name"].isNull()) {
                studentName = String((const char*)doc["student_name"]);
            } else {
                studentName = "";
            }
            
            Serial.println("\n*** CAPTURE COMMAND RECEIVED ***");
            Serial.printf("Mode: %s\n", currentMode.c_str());
            if (studentName.length() > 0) {
                Serial.printf("Student: %s\n", studentName.c_str());
            }
            
            return true;
        }
    } else {
        http.end();
    }
    
    return false;
}

// =============================================================================
// CAPTURE AND SEND IMAGE
// =============================================================================

void captureAndSend() {
    Serial.println("\n========================================");
    Serial.println("Capturing image...");
    
    // Visual feedback - LED on during capture
    flashOn();
    delay(200);  // Let flash stabilize and give user feedback
    
    // Capture image
    camera_fb_t* fb = esp_camera_fb_get();
    
    // Flash off
    flashOff();
    
    if (!fb) {
        Serial.println("ERROR: Camera capture failed!");
        blinkLED(5, 100);
        return;
    }
    
    Serial.printf("Image captured: %d bytes\n", fb->len);
    Serial.printf("Sending to server (mode: %s)...\n", currentMode.c_str());
    
    // Send image to server
    HTTPClient http;
    http.begin(recognizeUrl);
    http.addHeader("Content-Type", "image/jpeg");
    http.addHeader("X-Capture-Mode", currentMode);
    
    if (studentName.length() > 0) {
        http.addHeader("X-Student-Name", studentName);
    }
    
    http.setTimeout(15000);  // 15 second timeout for processing
    
    int httpResponseCode = http.POST(fb->buf, fb->len);
    
    // Return frame buffer
    esp_camera_fb_return(fb);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.printf("Response code: %d\n", httpResponseCode);
        Serial.print("Response: ");
        Serial.println(response);
        
        // Parse and show result
        parseResponse(response);
        
    } else {
        Serial.printf("ERROR: HTTP request failed: %s\n", 
                      http.errorToString(httpResponseCode).c_str());
        blinkLED(3, 200);
    }
    
    http.end();
    
    // Reset state
    currentMode = "";
    studentName = "";
    
    Serial.println("========================================\n");
}

// =============================================================================
// PARSE SERVER RESPONSE
// =============================================================================

void parseResponse(String response) {
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (error) {
        Serial.print("JSON parsing failed: ");
        Serial.println(error.c_str());
        return;
    }
    
    const char* status = doc["status"];
    
    // Check if this is a logout/time-out response
    const char* logType = "IN";
    if (doc.containsKey("log_type")) {
        logType = doc["log_type"];
    }
    bool isLogout = (strcmp(logType, "OUT") == 0);
    
    if (strcmp(status, "success") == 0) {
        const char* name = doc["name"];
        float confidence = doc["confidence"];
        
        if (isLogout) {
            Serial.println("✓ TIME OUT LOGGED!");
            Serial.printf("  Student: %s (Goodbye!)\n", name);
            // Logout success - two short blinks
            blinkLED(2, 200);
        } else {
            Serial.println("✓ TIME IN LOGGED!");
            Serial.printf("  Student: %s\n", name);
            Serial.printf("  Confidence: %.1f%%\n", confidence * 100);
            // Time in success - one long blink
            blinkLED(1, 500);
        }
        
    } else if (strcmp(status, "registered") == 0) {
        const char* name = doc["name"];
        
        Serial.println("✓ STUDENT REGISTERED!");
        Serial.printf("  Name: %s\n", name);
        
        // Registration success - double long blink
        blinkLED(2, 400);
        
    } else if (strcmp(status, "duplicate") == 0) {
        const char* name = doc["name"];
        
        if (isLogout) {
            Serial.println("○ ALREADY LOGGED OUT");
        } else {
            Serial.println("○ ALREADY LOGGED IN");
        }
        Serial.printf("  Student: %s\n", name);
        
        // Duplicate - two quick blinks
        blinkLED(2, 150);
        
    } else if (strcmp(status, "unknown") == 0) {
        Serial.println("✗ FACE NOT RECOGNIZED");
        
        // Unknown - three quick blinks
        blinkLED(3, 100);
        
    } else if (strcmp(status, "error") == 0) {
        const char* message = doc["message"];
        Serial.println("! ERROR");
        Serial.printf("  Message: %s\n", message);
        
        // Error - rapid blinks
        blinkLED(5, 50);
    }
}

// =============================================================================
// SETUP
// =============================================================================

void setup() {
    // Disable brownout detector
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
    
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    delay(1000);
    
    Serial.println();
    Serial.println("========================================");
    Serial.println("  ESP32-CAM Attendance System");
    Serial.println("  COMMAND-BASED CAPTURE MODE");
    Serial.println("========================================");
    
    // Build URLs
    pollUrl = "http://" + String(serverIP) + ":" + String(serverPort) + "/api/command/poll";
    recognizeUrl = "http://" + String(serverIP) + ":" + String(serverPort) + "/api/recognize";
    
    Serial.printf("Poll URL: %s\n", pollUrl.c_str());
    Serial.printf("Recognize URL: %s\n", recognizeUrl.c_str());
    
    // Setup flash LED
    setupFlash();
    
    // Initialize camera
    if (!initCamera()) {
        Serial.println("FATAL: Camera initialization failed!");
        Serial.println("Restarting in 5 seconds...");
        delay(5000);
        ESP.restart();
    }
    
    // Connect to WiFi
    if (!connectWiFi()) {
        Serial.println("WARNING: WiFi connection failed!");
        Serial.println("Will retry during operation...");
    }
    
    Serial.println();
    Serial.println("System ready! Waiting for commands...");
    Serial.println("Use the web dashboard to trigger captures.");
    Serial.println("========================================\n");
}

// =============================================================================
// MAIN LOOP
// =============================================================================

void loop() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected, reconnecting...");
        connectWiFi();
        delay(1000);
        return;
    }
    
    unsigned long currentTime = millis();
    
    // Poll for commands at regular intervals
    if (currentTime - lastPollTime >= POLL_INTERVAL) {
        lastPollTime = currentTime;
        
        // Quick visual feedback that we're polling
        // quickBlink();  // Uncomment to see polling activity
        
        // Check for capture command
        if (pollForCommand()) {
            // Command received - capture and send
            captureAndSend();
        }
    }
    
    delay(10);  // Small delay to prevent watchdog issues
}
