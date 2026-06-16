// SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
// SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {HeadquarterLicense} from "../contracts/HeadquarterLicense.sol";
import {IEthicalAxioms} from "../contracts/interfaces/IEthicalAxioms.sol";

contract Harness is HeadquarterLicense {
    constructor(bytes32 h) HeadquarterLicense(h) {}

    function gated(bool[4] memory a) external onlyCompatible(a) returns (bool) {
        return true;
    }
}

contract HeadquarterLicenseTest is Test {
    bytes32 internal constant LICENSE_HASH = keccak256("uecf-headquarter-1.0");

    function test_constructor_anchors_hash_and_spdx() public {
        Harness hq = new Harness(LICENSE_HASH);
        assertEq(hq.headquarterLicenseHash(), LICENSE_HASH);
        assertEq(hq.headquarterSpdxId(), "LicenseRef-UECF-Headquarter-1.0");
        assertEq(hq.axiomCount(), 4);
    }

    function test_constructor_rejects_zero_hash() public {
        vm.expectRevert(HeadquarterLicense.EmptyLicenseHash.selector);
        new Harness(bytes32(0));
    }

    function test_checkCompliance_all_true() public {
        Harness hq = new Harness(LICENSE_HASH);
        assertTrue(hq.checkCompliance([true, true, true, true]));
    }

    function test_checkCompliance_any_false() public {
        Harness hq = new Harness(LICENSE_HASH);
        assertFalse(hq.checkCompliance([true, false, true, true]));
    }

    function test_onlyCompatible_passes_when_all_attested() public {
        Harness hq = new Harness(LICENSE_HASH);
        assertTrue(hq.gated([true, true, true, true]));
    }

    function test_onlyCompatible_reverts_on_peace_violation() public {
        Harness hq = new Harness(LICENSE_HASH);
        vm.expectRevert(
            abi.encodeWithSelector(HeadquarterLicense.AxiomViolation.selector, IEthicalAxioms.Axiom.Peace)
        );
        hq.gated([true, false, true, true]);
    }
}
