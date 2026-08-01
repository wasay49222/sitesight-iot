import os
import json
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from supabase import create_client, Client
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="SiteSight IoT Backend")

# Allow CORS for Flutter app later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Initialize Supabase ---
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_KEY")
)

# --- 2. Initialize Web3 (Blockchain) ---
w3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC_URL")))
if not w3.is_connected():
    print("❌ Failed to connect to Ethereum node. Is Hardhat running?")
else:
    print("✅ Connected to local Hardhat node")

# Load Smart Contract ABI and Address
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# Hardhat saves the ABI here automatically after compilation
ARTIFACT_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "artifacts", "contracts", "SiteSightAudit.sol", "SiteSightAudit.json")

try:
    with open(ARTIFACT_PATH, "r") as f:
        artifact = json.load(f)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=artifact["abi"])
    account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
except Exception as e:
    print(f"❌ Error loading contract: {e}. Make sure the contract is deployed and .env is updated.")

# --- 3. IPFS Upload Function (Pinata) ---
def upload_to_ipfs(file_content: bytes, filename: str) -> str:
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "Authorization": f"Bearer {os.getenv('PINATA_JWT')}"
    }
    files = {
        "file": (filename, file_content, "image/jpeg")
    }
    
    response = requests.post(url, files=files, headers=headers)
    
    if response.status_code == 200:
        return response.json()["IpfsHash"]
    else:
        raise HTTPException(status_code=500, detail=f"IPFS Upload Failed: {response.text}")

# --- 4. Main Endpoint ---
@app.post("/api/violations")
async def receive_violation(
    image: UploadFile = File(...),
    msg_id: str = Form(...),
    camera_id: str = Form(...),
    violation_type: str = Form(...)
):
    print(f"📥 Received violation: {msg_id} from {camera_id}")
    
    try:
        # A. Upload Image to IPFS
        print("⬆️ Uploading image to IPFS...")
        ipfs_cid = upload_to_ipfs(await image.read(), image.filename)
        print(f"✅ IPFS CID: {ipfs_cid}")
        
        # B. Log to Blockchain (Smart Contract)
        print("⛓️ Logging to Smart Contract...")
        # Build the transaction
        tx = contract.functions.logViolation(ipfs_cid, camera_id, violation_type).build_transaction({
            'from': account.address,
            'gas': 2000000, # High gas limit for safety
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Blockchain TX Hash: {tx_hash.hex()}")
        
        # C. Save to Supabase Database
        print("💾 Saving to Supabase...")
        supabase.table("violations").insert({
            "camera_id": camera_id, # In a real app, map this to the UUID from DB
            "violation_type": violation_type,
            "ipfs_cid": ipfs_cid,
            "tx_hash": tx_hash.hex(),
            "resolved": False
        }).execute()
        
        return {"status": "success", "cid": ipfs_cid, "tx_hash": tx_hash.hex()}
        
    except Exception as e:
        print(f"❌ Error processing violation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "SiteSight Backend is running"}