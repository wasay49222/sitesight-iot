import { ethers } from "ethers";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

// ESM equivalents for __dirname and __filename
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  console.log("Deploying SiteSightAudit contract to local Hardhat network...");

  // 1. Connect to the local Hardhat node (Provider)
  const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
  
  // 2. Use the first default Hardhat account (Account #0 from your node output)
  // This account has 10,000 fake ETH, so it can pay for deployment "gas"
  const privateKey = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
  const signer = new ethers.Wallet(privateKey, provider);

  // 3. Read the compiled contract artifact (ABI and Bytecode)
  const artifactPath = path.join(__dirname, "..", "artifacts", "contracts", "SiteSightAudit.sol", "SiteSightAudit.json");
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

  // 4. Create a Contract Factory
  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, signer);

  // 5. Deploy the contract
  console.log("Sending deployment transaction...");
  const contract = await factory.deploy();
  
  // 6. Wait for the transaction to be mined
  await contract.waitForDeployment();

  // 7. Get the deployed address
  const address = await contract.getAddress();
  console.log("✅ SiteSightAudit successfully deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});