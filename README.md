# SiteSight IoT
## Computer-vision event monitoring and logging prototype

A student portfolio project connecting webcam detection, MQTT telemetry, HTTP image uploads, IPFS storage, local Ethereum logging, and a Flutter record viewer.

**The current detector identifies people and labels those events as simulated safety violations. It does not detect whether a person is wearing a hard hat.**

## Implementation

| Component | Current implementation |
| --- | --- |
| Webcam detection | A pretrained YOLOv8 nano model detects COCO class 0 (person). |
| Event simulation | Persistent person detection triggers an event labelled `no_hard_hat` for exercising the pipeline. |
| Telemetry | The edge script publishes event metadata to `sitesight/telemetry` over MQTT. |
| Image upload | The script saves a frame and sends it to a FastAPI endpoint over HTTP. |
| Backend integrations | The endpoint uploads images through Pinata/IPFS, submits a local Ethereum transaction, and inserts a Supabase record. |
| Smart contract | A Solidity contract records content identifiers, timestamps, camera IDs, and event labels. |
| Flutter interface | Fetches Supabase records, displays images/metadata, and supports manual refresh. |
| Failed-upload buffer | Failed HTTP uploads are recorded in local SQLite; automatic replay is not implemented. |

Key code: [edge script](edge_ai/main.py), [backend](backend/main.py), [contract](contracts/contracts/SiteSightAudit.sol), [Flutter interface](sitesight_app/lib/main.dart).

### Data flow

1. The edge script detects a person and creates a simulated event.
2. It publishes MQTT telemetry and separately sends the image to FastAPI.
3. FastAPI uploads the image to Pinata, submits its CID to a local Hardhat contract, and writes a Supabase row.
4. Flutter fetches stored rows and loads images through an IPFS gateway.

These are implemented code paths requiring service configuration. A successful end-to-end run was not verified during this documentation review.

## Current limitations

- **Detection:** No trained helmet/missing-hard-hat classifier is integrated.
- **Mobile alerts:** MQTT telemetry is published by the edge script, but there is no completed backend/mobile MQTT subscription or push-notification flow.
- **Live views:** GIS maps, live-video streaming, and real-time mobile subscriptions are not implemented in the reviewed app.
- **Offline handling:** SQLite records failed uploads, but there is no replay worker. Broker connection failures are also not covered by this HTTP buffer.
- **Verification button:** The Flutter button opens a public Etherscan URL. Transactions from a local Hardhat chain will not appear there; the button does not independently verify the image or record.
- **Blockchain scope:** The contract accepts submissions from any caller. Recording a CID does not establish the truth of the detection or the authenticity of the original image.
- **Storage scope:** Content addressing identifies image bytes; it does not guarantee permanent image availability or make the whole application tamper-proof.
- **Access control:** The upload route does not authenticate callers. Supabase credentials, schema, and access policies need configuration; complete application access control is not established.
- **Deployment and cost:** No production deployment or guaranteed zero-cost operation is claimed. External services have their own availability and usage limits.

## Local development

Prerequisites: Python, Node.js/npm, Flutter, Docker Compose, a webcam, and configured Pinata and Supabase projects.

### 1. Start MQTT

From the repository root:

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 2. Compile and deploy the local contract

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat node
```

Keep the node running. In another terminal, from `contracts/`:

```bash
node scripts/deploy.js
```

Record the deployed address. The deploy script uses a publicly known Hardhat development account intended only for local testing.

### 3. Configure the backend

Create `backend/.env` with your own values:

```dotenv
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_backend_supabase_key
PINATA_JWT=your_pinata_token
ETH_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=your_local_hardhat_test_account_key
CONTRACT_ADDRESS=your_deployed_contract_address
```

Create the Supabase `violations` table and compatible camera-ID/schema configuration for the fields used in [the insert call](backend/main.py). The Flutter view also expects `created_at`. These resources are not provisioned by starting the backend.

In a Python virtual environment, from `backend/`:

```bash
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

The backend needs the compiled contract artifact generated in step 2. Check dependency/API compatibility if transaction submission fails.

### 4. Run the edge script

Create `edge_ai/.env`:

```dotenv
CAMERA_ID=your_compatible_camera_id
BACKEND_URL=http://127.0.0.1:8000/api/violations
MQTT_BROKER_URL=127.0.0.1
MQTT_PORT=1883
```

In a Python virtual environment, from `edge_ai/`:

```bash
pip install -r requirements.txt
python main.py
```

A person standing in view triggers the simulation after the frame threshold; press `q` to stop. Timing depends on the actual frame rate.

### 5. Configure the Flutter viewer

Replace placeholder Supabase values in `sitesight_app/lib/main.dart` with the appropriate project URL and client key. Configure database access policies for your own setup. Keep backend service credentials out of the mobile client.

```bash
cd sitesight_app
flutter pub get
flutter run
```

Until the explorer integration is changed, inspect transactions through the local Ethereum RPC rather than relying on the app's Etherscan button.

## Next improvements

- Train and integrate a real safety-equipment detector.
- Complete event subscriptions/mobile alerts and buffered-upload replay.
- Authenticate uploads and configure record access rules.
- Replace the explorer button with verification for the configured chain.
- Add integration tests and a reproducible local demo before deployment.

## Author and license

Syed Muhammad Wasay — BS Artificial Intelligence student, ITU Lahore.

[GitHub](https://github.com/wasay49222) | [MIT License](LICENSE)

