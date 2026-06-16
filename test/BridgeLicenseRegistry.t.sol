// SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
// SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {BridgeLicenseRegistry} from "../contracts/BridgeLicenseRegistry.sol";
import {IEthicalAxioms} from "../contracts/interfaces/IEthicalAxioms.sol";

contract BridgeLicenseRegistryTest is Test {
    bytes32 internal constant LICENSE_HASH = keccak256("uecf-headquarter-1.0");
    bytes32 internal constant COMPONENT = keccak256("example-widget");
    string internal constant LEI = "529900T8BM49AURSDO55";
    string internal constant EXPR = "LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0";
    string internal constant SRC = "https://github.com/EU-UNION-AI-PACT/uecf-poc";

    address internal arbiter = makeAddr("arbiter");
    address internal registrant = makeAddr("registrant");

    // Mirror of the registry events for vm.expectEmit (solc 0.8.20 cannot
    // reference events through the contract type).
    event ComplianceRevoked(bytes32 indexed leiHash, string lei);
    event ComplianceReinstated(bytes32 indexed leiHash, string lei);

    BridgeLicenseRegistry internal registry;

    function setUp() public {
        registry = new BridgeLicenseRegistry(LICENSE_HASH, arbiter);
    }

    function _register() internal {
        vm.prank(registrant);
        registry.register(COMPONENT, LEI, EXPR, SRC);
    }

    function test_register_marks_active() public {
        _register();
        assertTrue(registry.isCovered(COMPONENT));
        BridgeLicenseRegistry.Record memory rec = registry.getRecord(COMPONENT);
        assertEq(rec.registrant, registrant);
        assertEq(rec.lei, LEI);
        assertEq(uint8(rec.status), uint8(BridgeLicenseRegistry.Status.Active));
    }

    function test_register_rejects_expression_without_headquarter() public {
        vm.prank(registrant);
        vm.expectRevert(BridgeLicenseRegistry.MissingHeadquarterBinding.selector);
        registry.register(COMPONENT, LEI, "Apache-2.0", SRC);
    }

    function test_register_rejects_empty_lei() public {
        vm.prank(registrant);
        vm.expectRevert(BridgeLicenseRegistry.EmptyLei.selector);
        registry.register(COMPONENT, "", EXPR, SRC);
    }

    function test_register_rejects_duplicate() public {
        _register();
        vm.prank(registrant);
        vm.expectRevert(BridgeLicenseRegistry.AlreadyRegistered.selector);
        registry.register(COMPONENT, LEI, EXPR, SRC);
    }

    function test_only_arbiter_can_report_breach() public {
        _register();
        vm.expectRevert(BridgeLicenseRegistry.NotArbiter.selector);
        registry.reportBreach(COMPONENT, IEthicalAxioms.Axiom.Peace);
    }

    function test_cure_within_window_restores() public {
        _register();
        vm.prank(arbiter);
        registry.reportBreach(COMPONENT, IEthicalAxioms.Axiom.Peace);

        vm.warp(block.timestamp + 10 days);
        vm.prank(registrant);
        registry.cure(COMPONENT);

        BridgeLicenseRegistry.Record memory rec = registry.getRecord(COMPONENT);
        assertEq(rec.breachReportedAt, 0);
        assertEq(uint8(rec.status), uint8(BridgeLicenseRegistry.Status.Active));
    }

    function test_cure_after_window_reverts() public {
        _register();
        vm.prank(arbiter);
        registry.reportBreach(COMPONENT, IEthicalAxioms.Axiom.Peace);

        vm.warp(block.timestamp + 31 days);
        vm.prank(registrant);
        vm.expectRevert(BridgeLicenseRegistry.CureWindowClosed.selector);
        registry.cure(COMPONENT);
    }

    function test_finalizeTermination_after_window() public {
        _register();
        vm.prank(arbiter);
        registry.reportBreach(COMPONENT, IEthicalAxioms.Axiom.Peace);

        vm.warp(block.timestamp + 31 days);
        registry.finalizeTermination(COMPONENT);

        assertFalse(registry.isCovered(COMPONENT));
        BridgeLicenseRegistry.Record memory rec = registry.getRecord(COMPONENT);
        assertEq(uint8(rec.status), uint8(BridgeLicenseRegistry.Status.Terminated));
    }

    function test_finalizeTermination_before_window_reverts() public {
        _register();
        vm.prank(arbiter);
        registry.reportBreach(COMPONENT, IEthicalAxioms.Axiom.Peace);

        vm.expectRevert(BridgeLicenseRegistry.CureWindowClosed.selector);
        registry.finalizeTermination(COMPONENT);
    }

    function test_getRecord_unknown_reverts() public {
        vm.expectRevert(BridgeLicenseRegistry.UnknownComponent.selector);
        registry.getRecord(keccak256("nope"));
    }

    function test_revokeCompliance_only_arbiter() public {
        vm.prank(registrant);
        vm.expectRevert(BridgeLicenseRegistry.NotArbiter.selector);
        registry.revokeCompliance(LEI);
    }

    function test_revokeCompliance_rejects_empty_lei() public {
        vm.prank(arbiter);
        vm.expectRevert(BridgeLicenseRegistry.EmptyLei.selector);
        registry.revokeCompliance("");
    }

    function test_killswitch_makes_component_uncovered() public {
        _register();
        assertTrue(registry.isCovered(COMPONENT));

        vm.expectEmit(true, false, false, true);
        emit ComplianceRevoked(keccak256(bytes(LEI)), LEI);
        vm.prank(arbiter);
        registry.revokeCompliance(LEI);

        assertTrue(registry.isLeiRevoked(LEI));
        assertTrue(registry.isRevoked(keccak256(bytes(LEI))));
        // Kill-switch overrides the Active lifecycle state immediately.
        assertFalse(registry.isCovered(COMPONENT));
        assertEq(
            uint8(registry.getRecord(COMPONENT).status),
            uint8(BridgeLicenseRegistry.Status.Active)
        );
    }

    function test_killswitch_blocks_new_registration() public {
        vm.prank(arbiter);
        registry.revokeCompliance(LEI);

        vm.prank(registrant);
        vm.expectRevert(BridgeLicenseRegistry.LeiRevoked.selector);
        registry.register(COMPONENT, LEI, EXPR, SRC);
    }

    function test_reinstate_restores_coverage() public {
        _register();
        vm.prank(arbiter);
        registry.revokeCompliance(LEI);
        assertFalse(registry.isCovered(COMPONENT));

        vm.expectEmit(true, false, false, true);
        emit ComplianceReinstated(keccak256(bytes(LEI)), LEI);
        vm.prank(arbiter);
        registry.reinstateCompliance(LEI);

        assertFalse(registry.isLeiRevoked(LEI));
        assertTrue(registry.isCovered(COMPONENT));
    }

    function test_revoke_is_idempotent() public {
        vm.startPrank(arbiter);
        registry.revokeCompliance(LEI);
        // A second revoke must not emit again but leaves the switch engaged.
        registry.revokeCompliance(LEI);
        vm.stopPrank();
        assertTrue(registry.isLeiRevoked(LEI));
    }
}
