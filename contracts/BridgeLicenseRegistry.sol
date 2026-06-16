// SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
// SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
pragma solidity ^0.8.20;

import {IEthicalAxioms} from "./interfaces/IEthicalAxioms.sol";

/// @title BridgeLicenseRegistry (Synchronisation layer)
/// @notice Records, immutably and publicly, the binding between a component,
///         its SPDX expression and the Headquarter axioms. Implements the
///         license lifecycle from the Headquarter license: registration,
///         automatic termination on a reported axiom breach, and a 30-day cure
///         window (Section 5 of LicenseRef-UECF-Headquarter-1.0).
/// @dev Self-contained (no external dependencies) to keep the PoC auditable.
///      Security best practices applied: custom errors, role-gated mutations
///      (`onlyArbiter`), a validity guard (`onlyValid`) and an explicit
///      emergency kill-switch (`revokeCompliance`) keyed by the GLEIF Legal
///      Entity Identifier (LEI) — the universal key of the institutional layer.
contract BridgeLicenseRegistry {
    /// @notice The cure window from Headquarter license Section 5.2.
    uint256 public constant CURE_WINDOW = 30 days;

    /// @notice keccak256 of the canonical Headquarter license text.
    bytes32 public immutable headquarterLicenseHash;

    /// @notice Address authorised to report axiom breaches (e.g. a DSA arbiter).
    address public immutable arbiter;

    enum Status {
        Unregistered,
        Active,
        Terminated
    }

    struct Record {
        address registrant;
        string lei;
        string spdxExpression;
        string sourceUrl;
        Status status;
        uint64 registeredAt;
        uint64 breachReportedAt;
        IEthicalAxioms.Axiom breachedAxiom;
    }

    mapping(bytes32 => Record) private _records;

    /// @notice Emergency kill-switch state, keyed by keccak256(LEI). When true,
    ///         every component registered under that Legal Entity Identifier is
    ///         treated as non-covered, bypassing the cure window.
    mapping(bytes32 => bool) public isRevoked;

    event Registered(bytes32 indexed componentId, address indexed registrant, string lei, string spdxExpression);
    event BreachReported(bytes32 indexed componentId, IEthicalAxioms.Axiom axiom, uint256 deadline);
    event Cured(bytes32 indexed componentId);
    event Terminated(bytes32 indexed componentId);
    event ComplianceRevoked(bytes32 indexed leiHash, string lei);
    event ComplianceReinstated(bytes32 indexed leiHash, string lei);

    error NotArbiter();
    error NotRegistrant();
    error AlreadyRegistered();
    error UnknownComponent();
    error InvalidState();
    error MissingHeadquarterBinding();
    error CureWindowClosed();
    error EmptyLei();
    error LeiRevoked();

    constructor(bytes32 licenseHash, address arbiter_) {
        require(licenseHash != bytes32(0), "empty license hash");
        require(arbiter_ != address(0), "empty arbiter");
        headquarterLicenseHash = licenseHash;
        arbiter = arbiter_;
    }

    /// @notice Restricts a mutation to the configured arbiter (e.g. DSA body).
    modifier onlyArbiter() {
        if (msg.sender != arbiter) {
            revert NotArbiter();
        }
        _;
    }

    /// @notice Reverts when the given LEI has been revoked via the kill-switch.
    modifier onlyValid(string calldata lei) {
        if (isRevoked[_leiHash(lei)]) {
            revert LeiRevoked();
        }
        _;
    }

    /// @notice Registers a component as a UECF Covered Work.
    /// @param componentId keccak256 of the component identifier.
    /// @param lei GLEIF Legal Entity Identifier of the registering entity.
    /// @param spdxExpression Must contain the Headquarter LicenseRef.
    /// @param sourceUrl Publicly retrievable source (Axiom A1).
    function register(
        bytes32 componentId,
        string calldata lei,
        string calldata spdxExpression,
        string calldata sourceUrl
    ) external onlyValid(lei) {
        if (bytes(lei).length == 0) {
            revert EmptyLei();
        }
        if (_records[componentId].status != Status.Unregistered) {
            revert AlreadyRegistered();
        }
        if (!_containsHeadquarter(spdxExpression)) {
            revert MissingHeadquarterBinding();
        }
        _records[componentId] = Record({
            registrant: msg.sender,
            lei: lei,
            spdxExpression: spdxExpression,
            sourceUrl: sourceUrl,
            status: Status.Active,
            registeredAt: uint64(block.timestamp),
            breachReportedAt: 0,
            breachedAxiom: IEthicalAxioms.Axiom.InformationFreedom
        });
        emit Registered(componentId, msg.sender, lei, spdxExpression);
    }

    /// @notice Arbiter reports an axiom breach, opening the cure window.
    function reportBreach(bytes32 componentId, IEthicalAxioms.Axiom axiom) external onlyArbiter {
        Record storage record = _records[componentId];
        if (record.status != Status.Active) {
            revert InvalidState();
        }
        record.breachReportedAt = uint64(block.timestamp);
        record.breachedAxiom = axiom;
        emit BreachReported(componentId, axiom, block.timestamp + CURE_WINDOW);
    }

    /// @notice Registrant cures a reported breach within the cure window.
    function cure(bytes32 componentId) external {
        Record storage record = _records[componentId];
        if (record.status == Status.Unregistered) {
            revert UnknownComponent();
        }
        if (msg.sender != record.registrant) {
            revert NotRegistrant();
        }
        if (record.breachReportedAt == 0) {
            revert InvalidState();
        }
        if (block.timestamp > record.breachReportedAt + CURE_WINDOW) {
            revert CureWindowClosed();
        }
        record.breachReportedAt = 0;
        emit Cured(componentId);
    }

    /// @notice Finalises termination once the cure window has elapsed.
    /// @dev Callable by anyone (permissionless enforcement) after the deadline.
    function finalizeTermination(bytes32 componentId) external {
        Record storage record = _records[componentId];
        if (record.status != Status.Active) {
            revert InvalidState();
        }
        if (record.breachReportedAt == 0) {
            revert InvalidState();
        }
        if (block.timestamp <= record.breachReportedAt + CURE_WINDOW) {
            revert CureWindowClosed();
        }
        record.status = Status.Terminated;
        emit Terminated(componentId);
    }

    /// @notice Returns the stored record for a component.
    function getRecord(bytes32 componentId) external view returns (Record memory) {
        Record memory record = _records[componentId];
        if (record.status == Status.Unregistered) {
            revert UnknownComponent();
        }
        return record;
    }

    /// @notice True iff the component is Active AND its LEI is not revoked.
    /// @dev The kill-switch takes precedence over the lifecycle state.
    function isCovered(bytes32 componentId) external view returns (bool) {
        Record storage record = _records[componentId];
        if (record.status != Status.Active) {
            return false;
        }
        return !isRevoked[_leiHash(record.lei)];
    }

    /// @notice Emergency kill-switch: revokes UECF compliance for an entire
    ///         Legal Entity Identifier (LEI), bypassing the cure window.
    /// @dev Only the arbiter may pull the switch. Idempotent and reversible.
    function revokeCompliance(string calldata lei) external onlyArbiter {
        if (bytes(lei).length == 0) {
            revert EmptyLei();
        }
        bytes32 leiHash = _leiHash(lei);
        if (!isRevoked[leiHash]) {
            isRevoked[leiHash] = true;
            emit ComplianceRevoked(leiHash, lei);
        }
    }

    /// @notice Reinstates a previously revoked LEI (governance counterpart).
    function reinstateCompliance(string calldata lei) external onlyArbiter {
        if (bytes(lei).length == 0) {
            revert EmptyLei();
        }
        bytes32 leiHash = _leiHash(lei);
        if (isRevoked[leiHash]) {
            isRevoked[leiHash] = false;
            emit ComplianceReinstated(leiHash, lei);
        }
    }

    /// @notice Convenience view: true iff the given LEI is revoked.
    function isLeiRevoked(string calldata lei) external view returns (bool) {
        return isRevoked[_leiHash(lei)];
    }

    function _leiHash(string memory lei) private pure returns (bytes32) {
        return keccak256(bytes(lei));
    }

    function _containsHeadquarter(string calldata expression) private pure returns (bool) {
        bytes memory needle = bytes("LicenseRef-UECF-Headquarter-1.0");
        bytes memory haystack = bytes(expression);
        if (haystack.length < needle.length) {
            return false;
        }
        for (uint256 i = 0; i <= haystack.length - needle.length; ++i) {
            bool matched = true;
            for (uint256 j = 0; j < needle.length; ++j) {
                if (haystack[i + j] != needle[j]) {
                    matched = false;
                    break;
                }
            }
            if (matched) {
                return true;
            }
        }
        return false;
    }
}
