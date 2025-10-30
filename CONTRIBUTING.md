# Contribuer à IACP Protocol — Core (S0)

## Branches
- `main` : stable, protégée (PR + CI).
- `dev` : travail courant (CI obligatoire).

## Commits
- Conventionnels : `feat:`, `fix:`, `docs:`, `chore:`, `ci:`, `test:`.
- Préférence petits commits clairs > gros commits opaques.

## PR
- Depuis `dev` → `main` (ou branches feature → `dev`).
- Checklist PR : tests locaux OK (`pytest -q`), CI verte, impact doc/spec évalué.

## Tests
- Lancer en local : `pytest -q` (pas besoin du serveur).
- Sandbox local : `./run_local.sh` puis `curl` pour tester /health et /iacp.

## Versions
- CI/Docker : Python 3.12 (référence). Local : 3.12 recommandé.
