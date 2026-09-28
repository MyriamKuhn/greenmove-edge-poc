# Bloc 3 - Industrialisation GreenMove Edge

Cette branche conserve tout le travail du Bloc 2 et ajoute les elements necessaires a la demonstration du Bloc 3.

Objectifs : audit du code initial, refactoring Python, persistance SQLite, synchronisation differee, tests, CI, OTA et rollback N-1.

Commandes video :

- git branch --show-current
- python -m pytest -q tests/bloc3
- python run_bloc3_demo.py
- python -m src.ota.check_manifest
- python -m src.ota.simulate_update --version 2.3.0
- python -m src.ota.simulate_update --version 2.4.0 --fail-install

Methode d'investigation : Reproduire -> Observer -> Isoler -> Identifier la cause racine -> Corriger -> Ajouter un test de non-regression.
