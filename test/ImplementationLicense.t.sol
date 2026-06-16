// SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
// SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {ImplementationLicense} from "../contracts/ImplementationLicense.sol";
import {HeadquarterLicense} from "../contracts/HeadquarterLicense.sol";

contract ImplementationLicenseTest is Test {
    bytes32 internal constant LICENSE_HASH = keccak256("uecf-headquarter-1.0");

    event ModuleDeployed(address indexed deployer, string spdxExpression);

    function test_builds_full_spdx_expression() public {
        ImplementationLicense impl = new ImplementationLicense(LICENSE_HASH, "Apache-2.0");
        assertEq(impl.implementationSpdxId(), "Apache-2.0");
        assertEq(impl.spdxExpression(), "LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0");
    }

    function test_rejects_empty_implementation_id() public {
        vm.expectRevert(ImplementationLicense.EmptyImplementationId.selector);
        new ImplementationLicense(LICENSE_HASH, "");
    }

    function test_deployModule_emits_when_compliant() public {
        ImplementationLicense impl = new ImplementationLicense(LICENSE_HASH, "MIT");
        vm.expectEmit(true, false, false, true);
        emit ModuleDeployed(address(this), "LicenseRef-UECF-Headquarter-1.0 AND MIT");
        impl.deployModule([true, true, true, true]);
    }

    function test_deployModule_reverts_when_not_compliant() public {
        ImplementationLicense impl = new ImplementationLicense(LICENSE_HASH, "MIT");
        vm.expectRevert();
        impl.deployModule([true, true, false, true]);
    }
}
