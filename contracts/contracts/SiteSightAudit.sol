// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SiteSightAudit {
    // Struct to hold the immutable violation data
    struct Violation {
        string ipfsCid;      // The content hash of the image on IPFS
        uint256 timestamp;   // Exact time of detection (Unix timestamp)
        string cameraId;     // UUID of the edge camera
        string violationType;// e.g., "no_hard_hat"
    }

    // Mapping to store violations by their unique sequential ID
    mapping(uint256 => Violation) public violations;
    
    // Counter to keep track of total violations logged
    uint256 public violationCount;

    // Event emitted when a new violation is logged. 
    // Why? Our Python backend can "listen" for this event to confirm the transaction succeeded.
    event ViolationLogged(
        uint256 indexed violationId, 
        string ipfsCid, 
        string cameraId, 
        string violationType, 
        uint256 timestamp
    );

    // Function to log a new violation
    function logViolation(
        string memory _cid, 
        string memory _cameraId, 
        string memory _type
    ) public returns (uint256) {
        violationCount++;
        
        violations[violationCount] = Violation({
            ipfsCid: _cid,
            timestamp: block.timestamp,
            cameraId: _cameraId,
            violationType: _type
        });

        emit ViolationLogged(
            violationCount, 
            _cid, 
            _cameraId, 
            _type, 
            block.timestamp
        );

        return violationCount;
    }
}