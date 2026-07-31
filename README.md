# SiteSight IoT
**Edge CV & Cyber-Physical Monitoring Dashboard**

A zero-budget cyber-physical safety monitoring system. Uses Edge AI (YOLOv8) to detect site violations, stores evidence immutably on IPFS, logs audit trails to a blockchain smart contract, and alerts managers via a Flutter mobile app.

## Architecture
Webcam -> Edge AI (Docker) -> MQTT/HTTP -> FastAPI -> IPFS (Pinata) -> Blockchain (Hardhat) -> Flutter App
