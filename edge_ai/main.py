import cv2
import time
import uuid
import json
import sqlite3
import requests
import paho.mqtt.client as mqtt
from pathlib import Path
from ultralytics import YOLO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
CAMERA_ID = os.getenv("CAMERA_ID", "cam-001")
MQTT_BROKER = os.getenv("MQTT_BROKER_URL", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/violations")

# Edge Constraints: Use nano model and low resolution for 8GB RAM
MODEL_PATH = "yolov8n.pt"
FRAME_WIDTH = 416
FRAME_HEIGHT = 416

# Debounce config: Alert only if violation persists for ~2 seconds (at ~15 FPS = 30 frames)
DEBOUNCE_FRAMES = 30 

# --- LOCAL OFFLINE BUFFER (SQLite) ---
DB_PATH = "edge_buffer.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_violations (
            msg_id TEXT PRIMARY KEY,
            image_path TEXT,
            camera_id TEXT,
            violation_type TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_to_buffer(msg_id, img_path, v_type, timestamp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO pending_violations VALUES (?, ?, ?, ?, ?)",
        (msg_id, img_path, CAMERA_ID, v_type, timestamp)
    )
    conn.commit()
    conn.close()
    print(f"💾 [OFFLINE BUFFER] Saved violation {msg_id} locally.")

# --- MQTT SETUP ---
def on_connect(client, userdata, flags, rc):
    print(f"✅ [MQTT] Connected to broker at {MQTT_BROKER}:{MQTT_PORT} with result code {rc}")

# Note: Using paho-mqtt 1.6.1 syntax
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start() # Run MQTT network loop in background thread

# --- MAIN LOOP ---
def main():
    print(f"🚀 Starting Edge AI Node: {CAMERA_ID}")
    print("Loading YOLOv8 Nano model...")
    model = YOLO(MODEL_PATH)
    init_db()

    # Open webcam (0 is default)
    cap = cv2.VideoCapture(0)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    violation_counter = 0
    last_alert_time = 0

    print("📷 Camera started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to grab frame")
            break

        # Run YOLO inference (verbose=False to keep console clean)
        results = model(frame, verbose=False, conf=0.5)
        
        # SIMULATION LOGIC: 
        # In a real scenario, this would check for a specific class like 'no_hard_hat'.
        # For now, we trigger on 'person' (class 0 in COCO) to test the pipeline.
        # Just stand in front of your webcam to trigger it!
        person_detected = any(r.cls == 0 for r in results[0].boxes)

        if person_detected:
            violation_counter += 1
            
            # TEMPORAL DEBOUNCING: Only trigger if violation persists
            if violation_counter >= DEBOUNCE_FRAMES and (time.time() - last_alert_time) > 5:
                last_alert_time = time.time()
                violation_counter = 0 # Reset counter
                
                msg_id = str(uuid.uuid4())
                timestamp = time.time()
                
                # Save frame locally for HTTP upload
                img_filename = f"violation_{msg_id}.jpg"
                img_path = str(Path(__file__).parent / img_filename)
                cv2.imwrite(img_path, frame)
                
                # 1. MQTT TELEMETRY (Lightweight, QoS 1 for guaranteed delivery)
                telemetry = {
                    "msg_id": msg_id,
                    "camera_id": CAMERA_ID,
                    "violation_type": "no_hard_hat",
                    "timestamp": timestamp
                }
                mqtt_client.publish("sitesight/telemetry", json.dumps(telemetry), qos=1)
                print(f"📡 [MQTT] Published telemetry for {msg_id}")
                
                # 2. HTTP POST (Heavy payload: Image)
                try:
                    with open(img_path, "rb") as f:
                        files = {"image": (img_filename, f, "image/jpeg")}
                        data = {"msg_id": msg_id, "camera_id": CAMERA_ID, "violation_type": "no_hard_hat"}
                        
                        response = requests.post(BACKEND_URL, data=data, files=files, timeout=5)
                        
                        if response.status_code == 200:
                            print(f"✅ [HTTP] Image uploaded successfully. Backend will handle IPFS/Blockchain.")
                            # Clean up local file after successful upload
                            os.remove(img_path)
                        else:
                            raise Exception(f"HTTP {response.status_code}")
                            
                except Exception as e:
                    print(f"❌ [HTTP] Backend unreachable. Buffering locally. Error: {e}")
                    save_to_buffer(msg_id, img_path, "no_hard_hat", timestamp)

        else:
            # Reset counter if no violation is seen
            violation_counter = 0

        # Draw bounding boxes for visual feedback
        annotated_frame = results[0].plot()
        cv2.imshow("SiteSight Edge View", annotated_frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    mqtt_client.loop_stop()

if __name__ == "__main__":
    main()