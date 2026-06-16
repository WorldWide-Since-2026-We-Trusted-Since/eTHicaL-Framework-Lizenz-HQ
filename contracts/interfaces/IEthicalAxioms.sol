// SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
// SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
pragma solidity ^0.8.20;

/// @title IEthicalAxioms
/// @notice Read-only interface exposing the four non-derogable UECF axioms.
/// @dev The on-chain enum mirrors the machine-readable Headquarter license
///      (`headquarter/headquarter-license.json`). Order is part of the ABI and
///      MUST NOT change within major version 1.x.
interface IEthicalAxioms {
    enum Axiom {
        InformationFreedom, // A1
        Peace, // A2
        Compassion, // A3
        DsaConformity // A4
    }

    /// @notice Emitted once when the immutable axiom set is anchored.
    event AxiomsAnchored(bytes32 indexed axiomsHash, string spdxLicenseId);

    /// @notice Returns the keccak256 hash of the canonical Headquarter license text.
    function headquarterLicenseHash() external view returns (bytes32);

    /// @notice Returns the SPDX identifier of the Headquarter layer.
    function headquarterSpdxId() external pure returns (string memory);
}
