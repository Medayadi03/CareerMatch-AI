# État réel — mise à jour du 25 novembre 2026

## Présentation GitHub
README réorganisé pour les visiteurs : objectif, état actuel, fonctionnalités prévues, stack, principes et démarrage rapide. Les instructions détaillées de l'ancien README sont conservées dans DEVELOPMENT.md. Liens locaux du nouveau README vérifiés ; modification documentaire uniquement, sans changement applicatif ni nouvelle exécution des tests.

## Phase 1 — parsing PDF local autorisé et implémenté
L'utilisateur a validé le démarrage de la phase 1, limité au parsing du CV PDF. Cette section remplace les mentions historiques « phase 1 non commencée » ci-dessous. L'extraction sémantique du profil, ESCO, retrieval, scoring, persistance et upload HTTP ne sont pas autorisés dans cette sous-étape.

Ajouts : `backend/app/documents/{__init__,__main__,models,parser}.py`, `backend/tests/test_pdf_parser.py`, `backend/scripts/create_sample_cv.py` et `docs/PDF_PARSING.md`. Mise à jour des règles AGENTS.md, documentation, dépendances/lockfile et périmètre mypy dans la CI. Parsing local sans LLM : texte par page/bloc, coordonnées, empreinte SHA-256, version du moteur, limites de lecture/pages/caractères, erreurs typées et avertissements d'extraction vide/partielle.

Validation réelle : synchronisation `uv sync --locked` réussie ; PyMuPDF 1.26.7 installé, les dix dépendances inutiles de la résolution initiale 2.1 retirées. Ruff et formatage réussis sur 14 fichiers ; mypy réussi sur 14 fichiers (import PyMuPDF non typé exempté explicitement). **21 tests réussis** (14 nouveaux + 7 existants) en 0,85 s ; un avertissement de dépréciation Starlette/AnyIO subsiste. Première exécution en sandbox : 19 succès, 2 erreurs de permissions des fichiers temporaires ; exécution complète hors sandbox réussie avec cache Pytest désactivé.

Commande de démonstration réellement exécutée : `python scripts/create_sample_cv.py`, puis `python -m app.documents ../.runtime/cv-synthetique.pdf`. Résultat : 2 pages, 3 blocs, 150 caractères, aucun avertissement. Durée CLI observée : 25,656 ms (hors imports/démarrage Python, incluant sérialisation/écriture) ; mesure unique sur document synthétique, pas une preuve de gain ni un benchmark représentatif. Le PDF synthétique est ignoré par Git.

Limites : pas d'OCR, pas de reconstruction fiable des colonnes, pas de vérification de vérité du texte ; pas de timeout ou limite mémoire native stricte. Interface locale uniquement, isolation à prévoir avant upload public. L'image Docker en cours d'exécution reste celle du socle précédent : ce parsing est testé dans l'environnement Python local, pas encore dans une image reconstruite. Frontend inchangé. Aucun commit ni push ; validation pédagogique de cette sous-étape attendue avant la suite.

## Validation Docker du 25 novembre — remplace les limitations Docker ci-dessous
Docker Desktop démarré, Engine 29.8.0 disponible. `.env` local créé avec mot de passe aléatoire, confirmé ignoré par Git, sans affichage du secret. Depuis la racine : `docker compose config --quiet`, construction des images et `docker compose up -d --wait` réussis après deux correctifs : nom du binaire BusyBox pour la sonde Qdrant, et réseau `access` réservé au backend pour rendre sa publication locale effective.

`docker compose ps` confirme les quatre services **healthy** : backend, PostgreSQL, Qdrant et Redis. Backend publié exclusivement sur `127.0.0.1:8000` ; aucun port hôte pour les bases. Volumes créés. Requêtes depuis Windows : live répond `alive`, ready répond `ready`, Swagger HTTP 200. Les conteneurs restent démarrés à la demande de l'utilisateur ; arrêt possible avec `docker compose down` (sans `-v` pour conserver les données).

Les contrôles navigateur restent à effectuer. Phase 1 non commencée ; aucun commit ni push. Les résultats historiques du 24 novembre ci-dessous sont conservés pour traçabilité ; les étapes manuelles Docker 1 à 4 sont désormais réalisées.

Phase 0 implémentée, validation utilisateur en attente. Phase 1 non commencée. Aucun commit, push ou déploiement.

## Réalisé
- Monorepo initialement vide (seul .git existait), 39 fichiers de projet créés.
- API FastAPI : configuration centralisée, environnement, logs JSON du cycle de vie, arrêt propre, CORS restrictif, OpenAPI, liveness/readiness et sept tests.
- Frontend React/TypeScript : titre, état de connexion, indisponibilité, timeout et rafraîchissement ; aucun dashboard métier.
- Compose : backend non-root, PostgreSQL, Qdrant avec sonde HTTP BusyBox, Redis ; réseau interne et volumes ; seul le port backend loopback est publié.
- Ruff, mypy strict, Pytest, ESLint, TypeScript, builds, lockfiles et CI sans déploiement.
- Documentation permanente et règles AGENTS.md.

## Vérifications réellement exécutées
| Vérification | Résultat |
| --- | --- |
| Installation uv 0.9.11 locale et Python 3.12.12 | Réussie dans .tools/.runtime, sans changer Python système |
| Installation backend / résolution uv.lock | Réussie, 28 paquets installés |
| Ruff check et format --check | Réussis, 8 fichiers Python formatés |
| mypy app tests | Réussi, 8 fichiers sans erreur |
| Pytest | 7 tests réussis en 1,31 s, 2 avertissements ci-dessous |
| Installation frontend / package-lock.json | Réussie après mises à jour ciblées |
| Audit npm final lors de l'installation | 0 vulnérabilité signalée sur 169 paquets audités |
| ESLint | Réussi sans avertissement après séparation App.tsx/main.tsx |
| TypeScript + build Vite | Réussis hors sandbox, 29 modules, build 767 ms |
| Compose config --quiet | Réussi avec mot de passe factice de validation |
| Compose up --build -d --wait | Échec : moteur Docker Linux absent (pipe dockerDesktopLinuxEngine introuvable) |
| Images, démarrage et santé des quatre conteneurs | Non vérifiés : moteur Docker indisponible |
| API native Uvicorn | HTTP 200 sur live, ready et docs ; réponses alive/ready correctes |
| CORS réel | Origines localhost:5173 et 127.0.0.1:5173 autorisées ; origine hostile rejetée par tests |
| Serveur frontend | Vite démarré, HTML et module App.tsx servis en HTTP 200 |
| Communication frontend/backend | URL de fetch et réponse API/CORS vérifiées ; pas de validation de l'exécution JavaScript dans un navigateur |
| Recherche de secrets | Aucun motif de clé AWS/OpenAI/GitHub ou clé privée détecté dans les sources ; exemples factices revus ; environnements et caches ignorés |
| CI distante | Configurée, non exécutée (aucun push) |

## Erreurs résolues et limitations
Accès registre initial bloqué par sandbox : téléchargements autorisés ensuite. L'audit npm initial indiquait huit vulnérabilités, corrigées avec Vite 7.3.8 et typescript-eslint 8.74.0. La première mise à jour groupée ESLint a rencontré un conflit de résolution ; migration en deux étapes réussie vers ESLint 10.15.0. Vite/esbuild était bloqué par `spawn EPERM` ; build et lancement réussis hors sandbox.

Pytest a signalé une dépréciation `anyio.abc.BlockingPortal` dans Starlette TestClient et un refus de création de cache lié aux permissions Windows. Les assertions ont toutes réussi ; le dossier temporaire de cache est ignoré. Ces avertissements ne sont pas présentés comme corrigés.

Pas d'outil de contrôle navigateur disponible : rendu, transitions connecté/indisponible et délai de reconnexion restent à vérifier manuellement. Aucun test navigateur automatisé ajouté. Pas d'audit complet des dépendances Python ou des images. Tags Docker explicites mais non verrouillés par digest ; construction Linux et téléchargement des tags restent à confirmer.

## Validation manuelle restante
1. Démarrer Docker Desktop (moteur Linux), vérifier `docker info`.
2. Copier `.env.example` vers `.env`, choisir un mot de passe local ; `docker compose config --quiet`.
3. Arrêter toute API locale sur 8000 ; `docker compose up --build -d --wait`, puis `docker compose ps` : quatre services sains attendus.
4. Vérifier `Invoke-RestMethod http://localhost:8000/api/v1/health/ready` et `/docs`.
5. `cd frontend`, `npm ci`, `npm run dev` ; ouvrir http://127.0.0.1:5173 et observer « Backend connecté et prêt ».
6. `docker compose stop backend` : la page doit signaler l'indisponibilité sous environ 15 secondes ; `docker compose start backend` : elle doit retrouver la connexion.
7. Confirmer volumes et absence de ports base publiés ; exécuter la CI après un push effectué uniquement par l'utilisateur.

## Git
Branche `master`, aucun commit initial. Tous les fichiers du projet sont nouveaux et non suivis ; rien n'a été ajouté à l'index. `git diff --stat` et `git diff --check` sont vides car les fichiers sont non suivis : cela ne constitue pas une revue de leur contenu. Les environnements locaux et artefacts ne font pas partie des fichiers versionnables.

Message de commit proposé : `chore: initialize CareerMatch AI phase 0 foundations`.

## Critères de validation de phase
Qualité backend/frontend locale réussie ; lockfiles présents ; API et CORS vérifiés ; documentation conforme au périmètre. Validation finale encore conditionnée au démarrage Docker, aux quatre health checks et au contrôle navigateur ci-dessus, puis à l'accord explicite de l'utilisateur. Ne pas commencer la phase 1 avant cet accord.

## Arborescence finale / liste des fichiers créés
```text
CareerMatchAI/
├── .dockerignore
├── .env.example
├── .gitignore
├── .github/workflows/ci.yml
├── AGENTS.md
├── README.md
├── compose.yaml
├── backend/
│   ├── .python-version
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/__init__.py
│   │   ├── api/health.py
│   │   ├── core/__init__.py
│   │   ├── core/config.py
│   │   └── core/logging.py
│   └── tests/test_health.py
├── frontend/
│   ├── .env.example
│   ├── package.json
│   ├── package-lock.json
│   ├── index.html
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── eslint.config.js
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       └── style.css
├── infrastructure/qdrant.Dockerfile
├── datasets/README.md
├── experiments/README.md
└── docs/
    ├── PROJECT_SPEC.md
    ├── ARCHITECTURE.md
    ├── ROADMAP.md
    ├── TECH_STACK.md
    ├── DECISIONS.md
    ├── EVALUATION.md
    └── PROGRESS.md
```

Artefacts locaux ignorés : .tools, .runtime, backend/.venv, caches Python, frontend/node_modules et frontend/dist. Les serveurs de validation sont arrêtés à la fin de la session ; lancement décrit dans README.md.
