# IACP Protocol — Core

Layer-1 d’interopérabilité universelle entre IA (objectif : le “HTTP de l’IA”).
Ce dépôt contient le **cœur technique**, la **sandbox d’interopérabilité minimale (S0)** et l’outillage **CI/CD**.

## Objectifs (S0)

![CI](https://github.com/iacp-protocol/Core/actions/workflows/ci.yml/badge.svg)
- Répo public propre et structuré
- CI/CD de base (lint, tests, build)
- Sandbox minimale : échange ping ↔ pong entre deux agents
- Documentation développeur (setup, contribution)

## Structure prévue
- `docs/` — guides dev (SETUP, CONTRIBUTING, STRUCTURE, SANDBOX)
- `spec/` — brouillons de spécifications (alignés avec P1)
- `src/` — code source
- `examples/` — démos d’interopérabilité
- `tests/` — tests et vérifications
- `sandbox/` — serveur minimal + agents ping-pong + logs

## Roadmap (extrait)
- **S0** : dépôt, CI/CD, sandbox ping-pong, docs de base
- **S1** : schéma de message stabilisé, transports initiaux, harness de test
- **S2+** : SDKs, extensions, conformité et interop élargie

## Contribution (S0)
- Branche `dev` pour le travail courant ; `main` protégée
- Commits conventionnels : `feat:`, `fix:`, `docs:`, `ci:`, `chore:`, `test:`
- PR avec checks verts obligatoires (CI)

## Licence
Ce dépôt est placé sous licence Apache-2.0 (voir `LICENSE`).
La licence finale et la gouvernance seront confirmées avec P1.

