import os

# 1. Create Directory Structure
dirs = [
    'edge_ai', 
    'backend', 
    'frontend', 
    'contracts', 
    'docker/mosquitto/config'
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# 2. Define File Contents
files = {
    '.gitignore': """# Environment Variables (NEVER push secrets)
.env
.env.local

# Python
__pycache__/
*.py[cod]
venv/
env/
*.egg-info/

# Node/Hardhat
node_modules/
cache/
artifacts/
typechain/
coverage/

# Flutter
frontend/build/
frontend/.dart_tool/
frontend/.packages
frontend/.pub-cache/

# OS
.DS_Store
Thumbs.db
""",

    'README.md': """# SiteSight IoT
**Edge CV & Cyber-Physical Monitoring Dashboard**

A zero-budget cyber-physical safety monitoring system. Uses Edge AI (YOLOv8) to detect site violations, stores evidence immutably on IPFS, logs audit trails to a blockchain smart contract, and alerts managers via a Flutter mobile app.

## Architecture
Webcam -> Edge AI (Docker) -> MQTT/HTTP -> FastAPI -> IPFS (Pinata) -> Blockchain (Hardhat) -> Flutter App
""",

    'docker/docker-compose.yml': """version: '3.8'
services:
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: sitesight_mosquitto
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf
    restart: unless-stopped
""",

    'docker/mosquitto/config/mosquitto.conf': """# Standard MQTT Listener
listener 1883
allow_anonymous true

# WebSocket Listener for Mobile/Web
listener 9001
protocol websockets
allow_anonymous true
""",

    'backend/.env': """# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Pinata (IPFS)
PINATA_JWT=your_pinata_jwt

# Blockchain
ETH_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=your_hardhat_private_key
CONTRACT_ADDRESS=

# MQTT
MQTT_BROKER_URL=127.0.0.1
MQTT_PORT=1883
""",

    'backend/requirements.txt': """fastapi==0.110.0
uvicorn==0.29.0
paho-mqtt==1.6.1
web3==6.15.1
pinatapy==0.2.0
python-dotenv==1.0.1
supabase==2.3.4
python-multipart==0.0.9
""",

    'edge_ai/requirements.txt': """ultralytics==8.1.45
opencv-python==4.9.0.80
paho-mqtt==1.6.1
requests==2.31.0
python-dotenv==1.0.1
"""
}

# 3. Write Files
for path, content in files.items():
    # Ensure directory exists before writing (for nested paths like docker/...)
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 4. Copy .env to edge_ai
with open('backend/.env', 'r', encoding='utf-8') as f:
    env_content = f.read()
with open('edge_ai/.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✅ SiteSight IoT Level 1 structure generated successfully!")