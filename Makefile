# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
.PHONY: help install reuse ingest ingest-live validate validate-all test-py test-sol test all

help:
	@echo "UECF Proof of Best Practices Concept - make targets:"
	@echo "  install     install python deps (jsonschema, reuse, pytest)"
	@echo "  reuse       run 'reuse lint' (SPDX/REUSE conformance)"
	@echo "  ingest      run the data pipeline offline (parse IXP table, build manifests)"
	@echo "  ingest-live fetch live data (PeeringDB/PCH/CAIDA) + build manifests"
	@echo "  validate    run the compliance validator on the example manifest"
	@echo "  validate-all validate every implementation manifest"
	@echo "  test-py     run python validator tests"
	@echo "  test-sol    run Solidity (forge) contract tests"
	@echo "  test        run reuse lint + python tests + forge tests"
	@echo "  all         alias for 'test'"

install:
	python3 -m pip install -r requirements.txt charset-normalizer

reuse:
	python3 -m reuse lint

ingest:
	python3 -m ingest.pipeline --offline

ingest-live:
	python3 -m ingest.pipeline

validate:
	python3 tools/uecf_validate.py implementation/example-implementation.json

validate-all:
	@for m in implementation/*.json; do echo "== $$m"; python3 tools/uecf_validate.py "$$m" || exit 1; done

test-py:
	python3 -m pytest -q

test-sol:
	forge test

test: reuse ingest test-py validate-all test-sol

all: test
