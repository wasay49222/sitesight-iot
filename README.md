# SiteSight IoT - Edge CV & Cyber-Physical Monitoring Dashboard

![Edge AI](https://img.shields.io/badge/Edge%20AI-YOLOv8-blue)
![Blockchain](https://img.shields.io/badge/Blockchain-Ethereum-green)
![Storage](https://img.shields.io/badge/Storage-IPFS-orange)
![Mobile](https://img.shields.io/badge/Mobile-Flutter-purple)

A cyber-physical safety monitoring system that uses Edge AI to detect site violations, stores evidence immutably on IPFS, logs audit trails to blockchain smart contracts, and alerts managers via a Flutter mobile app.

**Total Cost: $0** - Built entirely with free-tier services and open-source tools.

## 🎯 Features

- **Edge AI Detection**: Real-time computer vision using YOLOv8 to detect safety violations (e.g., missing hard hats)
- **Decentralized Storage**: Violation images stored on IPFS via Pinata (tamper-proof content addressing)
- **Blockchain Auditing**: Immutable audit logs via Ethereum smart contracts (Hardhat local testnet)
- **Real-Time Alerts**: MQTT-based telemetry and push notifications to mobile app
- **Mobile Dashboard**: Flutter app with audit log viewer, GIS map, and live feed
- **Offline Resilience**: SQLite buffering when backend is unreachable

## ️ Architecture
┌─────────────┐ MQTT/HTTP ─────────────┐ IPFS ┌─────────────┐
│ Edge AI │ ────────────────> │ FastAPI │ ───────────> │ Pinata │
│ (YOLOv8) │ │ Backend │ │ (IPFS) │
└───────────── └─────────────┘ └─────────────┘
│ │
│ Blockchain │ CID
▼ │
┌─────────────┐ │
│ Hardhat │ │
│ (Ethereum) │ │
└─────────────┘ │
│ │
│ TX Hash │
▼ ▼
┌─────────────────────────────────────┐
│ Supabase (PostgreSQL) │
└─────────────────────────────────────┘
│
│ Real-time
▼
┌─────────────┐
│ Flutter │
│ Mobile App │
└─────────────┘

## ️ Tech Stack

### Edge Layer
- **Python 3.11+** with OpenCV
- **Ultralytics YOLOv8** for object detection
- **Paho MQTT** for telemetry
- **SQLite** for offline buffering

### Backend
- **FastAPI** (Python web framework)
- **Web3.py** for blockchain interaction
- **Pinata API** for IPFS pinning
- **Supabase** for database & auth

### Blockchain
- **Hardhat** (Local Ethereum testnet)
- **Solidity** smart contracts
- **web3.py** integration

### Mobile
- **Flutter** (Cross-platform iOS/Android)
- **Supabase Flutter** for data sync
- **MQTT Client** for real-time alerts
- **Cached Network Image** for IPFS loading

### Infrastructure
- **Docker** for Mosquitto MQTT broker
- **Docker** for Edge AI simulation (resource constraints)

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 16+ and npm
- Flutter 3.0+
- Docker Desktop
- Git

##  Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/sitesight-iot.git
cd sitesight-iot

2. Environment Setup
Create .env files in the following locations:
backend/.env:

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key
PINATA_JWT=your_pinata_jwt
ETH_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=your_hardhat_account_private_key
CONTRACT_ADDRESS=your_deployed_contract_address
MQTT_BROKER_URL=127.0.0.1
MQTT_PORT=1883

edge_ai/.env
CAMERA_ID=your_camera_uuid
BACKEND_URL=http://127.0.0.1:8000/api/violations
MQTT_BROKER_URL=127.0.0.1
MQTT_PORT=1883

sitesight_app/lib/main.dart
Replace the placeholder constants with your actual Supabase credentials.
3. Infrastructure Setup
Start Docker Services:
cd docker
docker-compose up -d
Start Local Blockchain:
cd contracts
npm install
npx hardhat node
Deploy Smart Contract:
# In a new terminal (contracts/)
npx hardhat run scripts/deploy.js --network localhost
# Copy the deployed contract address to backend/.env
4. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
cd edge_ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

5. Edge AI Setup
cd edge_ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

6. Flutter App Setup
cd sitesight_app
flutter pub get
flutter run

Project Structure
sitesight-iot/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── .env             # Environment variables (NOT in Git)
│   └── requirements.txt # Python dependencies
── contracts/           # Solidity smart contracts
│   ├── contracts/
│   │   ── SiteSightAudit.sol
│   ├── scripts/
│   │   └── deploy.js
│   └── hardhat.config.js
├── docker/              # Docker configurations
│   └── docker-compose.yml
├── edge_ai/            # Edge AI simulation
│   ├── main.py
│   ├── .env
│   └── requirements.txt
├── sitesight_app/      # Flutter mobile app
│   ├── lib/
│   │   ── main.dart
│   └── pubspec.yaml
├── .gitignore
── README.md

Course Coverage
Course
How It's Covered
Cyber-Physical Systems
Bridging physical webcam/hardware with digital cloud infrastructure via Edge AI and MQTT
Computer Networks
MQTT protocol for lightweight IoT telemetry, WebSockets for live streaming, HTTP POST for binary data
Blockchain
Solidity smart contract development, Hardhat deployment, web3.py integration, immutable audit logging
Computer Vision
Ultralytics YOLOv8 object detection, OpenCV frame processing, Edge optimization
HCI (Flutter UI)
Designing a high-contrast, real-time mobile dashboard for non-technical site managers
Remote Sensing/GIS
Plotting IoT camera nodes and violation events on a geospatial map

🔒 Security Considerations
Tamper-Proof Logs: IPFS content-addressed storage + blockchain immutability
API Key Security: All sensitive keys stored in .env files (gitignored)
RLS Policies: Supabase Row Level Security for data access control
MQTT Security: Production deployment should use TLS/SSL and X.509 certificates
📝 Development Roadmap
Edge AI detection with YOLOv8
FastAPI backend with IPFS integration
Smart contract deployment
Flutter mobile app with audit log
Real-time WebSocket live feed
GIS map integration with camera markers
Docker containerization for Edge AI
Production deployment to Render/Sepolia
🤝 Contributing
This is a portfolio project. Feel free to fork and experiment!
License
MIT License - See LICENSE file for details
👨‍💻 Author
Wasay
Built with ❤️ using free-tier services and open-source tools