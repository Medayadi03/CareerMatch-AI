# Guide de développement — CareerMatch AI

**Multi-Agent Career Intelligence & Skill Gap Analysis Platform**

Projet PFE d'aide au développement professionnel : comparer un CV aux exigences d'un poste, expliquer les correspondances et proposer une progression. Ce n'est pas un outil de sélection automatisée pour employeurs.

## État actuel

Phase 0 : API de santé, configuration, logs JSON, frontend de statut, infrastructure locale et CI. Phase 1 : parsing PDF local en pages/blocs textuels, avec validations et provenance. Aucune extraction sémantique de profil, aucun matching, agent, appel LLM ou scoring. Voir [PROGRESS](PROGRESS.md) et l'[atelier parsing PDF](PDF_PARSING.md).

## Prérequis

- Python 3.12 (uv peut le télécharger), uv 0.9.11.
- Node.js >=22.12, npm (validation locale avec Node 24.14.0 / npm 11.11.1).
- Docker Desktop avec moteur Linux démarré et Docker Compose v2.
- Git. Aucun compte cloud ou fournisseur IA requis.

## Installation locale — PowerShell

Depuis la racine, copier les exemples puis remplacer le mot de passe PostgreSQL local :

```powershell
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env
cd backend
uv sync --locked
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log
```

Dans un deuxième terminal :

```powershell
cd frontend
npm ci
npm run dev
```

Lors de cette initialisation, uv a été installé uniquement dans `.tools/bin/uv.exe`, avec Python et le cache dans `.runtime`. Pour le réutiliser depuis `backend` :

```powershell
$env:UV_CACHE_DIR="$PWD\..\.runtime\uv-cache"
$env:UV_PYTHON_INSTALL_DIR="$PWD\..\.runtime\python"
..\.tools\bin\uv.exe sync --locked
..\.tools\bin\uv.exe run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

## Docker

Depuis la racine après création du `.env` :

```powershell
docker compose config --quiet
docker compose up --build -d --wait
docker compose ps
docker compose logs backend
docker compose down
```

Les volumes sont conservés par `down`. `down -v` détruit les données locales : ne l'utiliser que volontairement. Le frontend se lance séparément avec Vite. Arrêter l'API locale avant de lancer le backend Docker sur le même port.

| Conteneur | Rôle actuel / futur |
| --- | --- |
| backend | API santé effective ; futures routes métier |
| postgres | Provisionné, non utilisé ; futurs profils et analyses |
| qdrant | Provisionné, non utilisé ; futurs index vectoriels |
| redis | Provisionné, non utilisé ; futur cache |

Seul le backend est publié sur `127.0.0.1:8000`, via un réseau `access` distinct. Les bases restent exclusivement sur un réseau interne sans ports hôte. Le backend dispose d'une sortie réseau via `access` ; les futurs appels fournisseurs devront être encadrés au niveau applicatif.

## URLs et configuration

- Frontend : http://localhost:5173
- Liveness : http://localhost:8000/api/v1/health/live
- Readiness : http://localhost:8000/api/v1/health/ready
- Swagger : http://localhost:8000/docs ; schéma : http://localhost:8000/openapi.json
- Backend : `APP_ENV`, `LOG_LEVEL`, `CORS_ORIGINS` (tableau JSON d'origines explicites).
- Frontend : `VITE_API_URL` dans `frontend/.env`. Variable publique injectée au build : jamais de secret. Redémarrer Vite/reconstruire après changement.
- `BACKEND_PORT` modifie le port Docker ; adapter également `VITE_API_URL`.

Le backend charge `../.env` lorsqu'il est lancé depuis `backend`. Docker injecte les variables par Compose. Les variables du processus ont priorité. Readiness vérifie la fin du démarrage de l'application ; aucune base n'est requise en phase 0.

## Qualité

```powershell
cd backend
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy app tests scripts
uv run --locked pytest -q
cd ../frontend
npm run lint
npm run build
```

`build` comprend la vérification TypeScript. GitHub Actions exécute ces contrôles et valide Compose, sans déploiement. Les résultats locaux et limites Docker sont consignés dans [PROGRESS](PROGRESS.md).

## Structure

```text
backend/          API, configuration, tests, pyproject.toml, uv.lock, Dockerfile
frontend/         React/TypeScript/Vite, package-lock.json
infrastructure/   Image Qdrant avec sonde HTTP autonome
datasets/         Conventions de données, aucune donnée personnelle
experiments/      Conventions de futurs benchmarks
docs/             Spécification, architecture, décisions, roadmap, suivi
.github/workflows/ Vérifications CI
```

## Dépannage

- Docker indique un pipe introuvable : démarrer Docker Desktop, sélectionner les conteneurs Linux et vérifier `docker info`.
- Port 8000 occupé : arrêter l'autre API ou changer `BACKEND_PORT` et `VITE_API_URL`.
- Backend indisponible : vérifier `/api/v1/health/ready`, les logs, l'URL et les origines CORS ; la page réessaie toutes les 10 secondes avec délai maximal de 5 secondes.
- Erreur de mot de passe Compose : créer `.env` et définir `POSTGRES_PASSWORD`. Un changement de variable ne change pas le mot de passe d'un volume PostgreSQL déjà initialisé.
- `uv` absent : installer la version indiquée ou utiliser l'exécutable local ci-dessus.
- Réseau restreint : les premiers téléchargements Python/npm/Docker nécessitent un accès aux registres. Ne pas modifier les lockfiles pour contourner un problème réseau.
- Pas d'authentification en phase 0 : usage local uniquement, ne pas envoyer de CV réels.
