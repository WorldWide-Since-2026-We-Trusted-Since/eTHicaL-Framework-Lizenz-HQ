// SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
// SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
pragma solidity ^0.8.20;

import {HeadquarterLicense} from "./HeadquarterLicense.sol";

/// @title ImplementationLicense (Child layer)
/// @notice A concrete component's license, modelled as a child contract that
///         inherits the Headquarter axioms. The SPDX expression is exposed
///         on-chain so the Bridge can record it immutably.
/// @dev Inheritance here is the on-chain analogue of the SPDX expression
///      "LicenseRef-UECF-Headquarter-1.0 AND <implementation>".
contract ImplementationLicense is HeadquarterLicense {
    /// @notice SPDX identifier of the implementation layer, e.g. "Apache-2.0".
    string public implementationSpdxId;

    /// @notice Full SPDX expression binding both layers.
    string public spdxExpression;

    event ModuleDeployed(address indexed deployer, string spdxExpression);

    error EmptyImplementationId();

    /// @param licenseHash keccak256 of the canonical Headquarter license text.
    /// @param implementationSpdxId_ SPDX id of the implementation license.
    constructor(bytes32 licenseHash, string memory implementationSpdxId_)
        HeadquarterLicense(licenseHash)
    {
        if (bytes(implementationSpdxId_).length == 0) {
            revert EmptyImplementationId();
        }
        implementationSpdxId = implementationSpdxId_;
        spdxExpression = string.concat(
            "LicenseRef-UECF-Headquarter-1.0 AND ", implementationSpdxId_
        );
    }

    /// @notice Deploys/activates a module only if all axioms are attested.
    /// @param attestation A1-A4 attestation flags; all must be true.
    function deployModule(bool[4] memory attestation)
        external
        onlyCompatible(attestation)
    {
        emit ModuleDeployed(msg.sender, spdxExpression);
    }
}
