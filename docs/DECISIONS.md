# Décisions d'architecture

## ADR-008 — Parsing local avant extraction sémantique
Accord utilisateur du 25 novembre 2026 limité au parsing PDF. Module réutilisable et CLI pour comprendre/tester l'extraction indépendamment de HTTP, stockage et LLM. PyMuPDF 1.26.7, contrats Pydantic, preuves par page/bloc, limites explicites ; pas de normalisation agressive. Aucune conclusion sur les compétences à partir du texte brut. Une exposition HTTP nécessitera isolation du parser et budgets d'exécution. Détails et sources : PDF_PARSING.md.

## Correctif Docker — 25 novembre 2026
La validation réelle a révélé deux problèmes : BusyBox renommé `probe` refuse de lancer ses applets ; il conserve désormais son nom `busybox`. Docker Engine 29.8 ne publiait pas le port backend avec le seul réseau interne (port effectif vide). Un réseau `access` est ajouté au backend uniquement, avec publication sur 127.0.0.1 ; les trois bases restent exclusivement sur `internal`. Le backend dispose ainsi aussi d'une sortie réseau, à encadrer lors des intégrations externes.

## ADR-001 — Monorepo modulaire
Accepté en phase 0. Un backend et un frontend ; frontières Python simples. Réduit le coût d'exploitation dans un projet de 30 jours tout en permettant une extraction ultérieure du service IA.

## ADR-002 — Dépendances minimales et verrouillées
FastAPI/Pydantic/settings/Uvicorn seulement en production backend. uv.lock et package-lock.json enregistrent les dépendances transitives ; CI installe sans résolution libre. Les outils IA/ORM arrivent avec leurs cas d'usage. Versions choisies explicitement, sans prétendre qu'elles sont les plus récentes. Les images utilisent des tags de version ; ces tags ne garantissent pas l'immuabilité d'un digest. Un verrouillage par digest restera à effectuer avant déploiement.

## ADR-003 — Readiness honnête
Le démarrage et l'arrêt pilotent un booléen de disponibilité ; les trois bases inutilisées ne conditionnent pas l'API. Liveness reste indépendant. Ajouter de vrais contrôles de dépendances dès que du métier les nécessite.

## ADR-004 — Infrastructure privée
Aucun port base publié ; backend lié au loopback hôte. Qdrant reçoit un binaire BusyBox musl pour vérifier `/readyz` sans supposer la présence de curl. Les sondes PostgreSQL et Redis utilisent leurs clients natifs. Vérification HTTP Qdrant : https://api.qdrant.tech/api-reference/service/readyz.

## ADR-005 — Frontend limité
React/TypeScript/Vite avec fetch natif, abort après 5 secondes et rafraîchissement 10 secondes. Pas de routeur, TanStack Query ou UI framework pour une page unique. Statut accessible avec `role=status`, erreurs explicites. URL API publique configurable au build.

## ADR-006 — Logs et confidentialité
Événements de cycle de vie en JSON, sans configuration, payload ou données utilisateur. Les commandes désactivent les access logs Uvicorn pour éviter les URLs sensibles futures. Les logs serveur Uvicorn restent au format natif ; centralisation et OpenTelemetry sont planifiés.

## ADR-007 — Construction backend
Image Python 3.12, uv versionné, synchronisation `--locked --no-dev`, exécution non-root. Contexte Docker racine filtré. Référence : https://docs.astral.sh/uv/guides/integration/docker/.
