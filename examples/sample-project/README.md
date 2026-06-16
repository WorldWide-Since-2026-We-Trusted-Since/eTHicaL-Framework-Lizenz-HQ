# Beispielkomponente (UECF Covered Work)

Diese Mini-Komponente zeigt, wie ein nachgelagertes Projekt UECF-konform wird:

1. Jede Quelldatei trägt den SPDX-Ausdruck
   `LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0`
   (siehe [`src/widget.py`](./src/widget.py)).
2. Das zugehörige Manifest ist
   [`../../implementation/example-implementation.json`](../../implementation/example-implementation.json).
3. Validierung:

   ```bash
   python3 tools/uecf_validate.py implementation/example-implementation.json
   ```
