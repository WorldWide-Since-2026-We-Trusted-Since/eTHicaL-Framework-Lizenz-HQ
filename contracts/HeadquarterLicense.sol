// SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
// SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
pragma solidity ^0.8.20;

import {IEthicalAxioms} from "./interfaces/IEthicalAxioms.sol";

/// @title HeadquarterLicense (Root Trust Authority)
/// @notice Axiomatic, immutable root layer of the UECF. It anchors the hash of
///         the canonical Headquarter license text and exposes a compliance gate
///         (`onlyCompatible`) that downstream Implementation contracts inherit.
/// @dev "Best practices" applied here:
///      - custom errors instead of revert strings (gas + clarity),
///      - `immutable` storage for the anchored hash (no post-deploy mutation),
///      - no owner / no upgrade path: the axioms are unumstößlich by design.
contract HeadquarterLicense is IEthicalAxioms {
    /// @dev keccak256 of the canonical LICENSES/LicenseRef-UECF-Headquarter-1.0.txt.
    bytes32 public immutable headquarterLicenseHash;

    string private constant _SPDX_ID = "LicenseRef-UECF-Headquarter-1.0";

    error AxiomViolation(Axiom axiom);
    error EmptyLicenseHash();

    /// @param licenseHash keccak256 of the canonical Headquarter license text.
    constructor(bytes32 licenseHash) {
        if (licenseHash == bytes32(0)) {
            revert EmptyLicenseHash();
        }
        headquarterLicenseHash = licenseHash;
        emit AxiomsAnchored(licenseHash, _SPDX_ID);
    }

    /// @inheritdoc IEthicalAxioms
    function headquarterSpdxId() external pure returns (string memory) {
        return _SPDX_ID;
    }

    /// @notice The number of non-derogable axioms (A1-A4).
    function axiomCount() external pure returns (uint256) {
        return uint256(Axiom.DsaConformity) + 1;
    }

    /// @notice Reverts unless every axiom in `attestation` is satisfied (true).
    /// @dev `attestation[i]` corresponds to `Axiom(i)`. The gate is pure-logic;
    ///      legal compliance still requires off-chain review and the
    ///      `uecf_validate.py` checks.
    modifier onlyCompatible(bool[4] memory attestation) {
        _requireAxioms(attestation);
        _;
    }

    function _requireAxioms(bool[4] memory attestation) internal pure {
        for (uint256 i = 0; i < attestation.length; ++i) {
            if (!attestation[i]) {
                revert AxiomViolation(Axiom(i));
            }
        }
    }

    /// @notice Convenience view: true iff all four axioms are attested.
    function checkCompliance(bool[4] memory attestation) public pure returns (bool) {
        for (uint256 i = 0; i < attestation.length; ++i) {
            if (!attestation[i]) {
                return false;
            }
        }
        return true;
    }
}
