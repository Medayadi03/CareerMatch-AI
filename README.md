# CareerMatch AI

Comprendre les exigences d’un poste, identifier ses compétences à renforcer et construire un parcours de progression personnalisé.

CareerMatch AI est une application en développement qui vise à rapprocher le profil d’un candidat des besoins du marché de l’emploi. À partir d’un CV et d’une offre, elle proposera une analyse explicable des correspondances, des lacunes et des prochaines étapes d’apprentissage.

> **Étape actuelle : phase 1 — parsing des CV au format PDF.**
> Le socle technique est opérationnel. L’extraction locale du texte des PDF est implémentée ; l’analyse des compétences et le matching sont à venir.

## Objectif

Aider les étudiants, jeunes diplômés et ingénieurs à répondre à trois questions :

- Quelles exigences du poste mon CV permet-il de justifier ?
- Quelles compétences dois-je développer ou mieux démontrer ?
- Quels projets et apprentissages peuvent m’aider à progresser ?

Le projet est conçu pour accompagner le candidat dans son développement professionnel. Chaque correspondance devra être reliée à des éléments vérifiables de son CV.

## Avancement

| Étape | État |
| --- | --- |
| Initialisation du monorepo et de l’environnement Docker | Réalisée |
| Extraction du texte des PDF, par page et par bloc | Implémentée en ligne de commande |
| Extraction structurée des compétences, expériences et formations | À développer |
| Normalisation des compétences avec ESCO | Planifiée |
| Recherche lexicale BM25 et recherche sémantique | Planifiées |
| Matching et score de compatibilité explicable | Planifiés |
| Analyse du marché et recommandations personnalisées | Planifiées |

**Disponible aujourd’hui :** une API FastAPI avec endpoints de santé, une page React affichant l’état de connexion, un parser PDF local et un environnement Docker Compose. Le backend dispose de 21 tests réussis lors de la dernière validation documentée.

Le parser produit du JSON contenant les pages, le texte, les coordonnées des blocs et les références de source. Les PDF scannés nécessitant un OCR ne sont pas encore pris en charge. L’import de CV depuis l’interface et l’extraction d’un profil métier ne sont pas encore disponibles.

## Fonctionnalités prévues

- **CV et offre d’emploi :** extraire les informations du candidat et les exigences du poste.
- **Matching explicable :** retrouver les passages justificatifs et distinguer les exigences démontrées, partielles ou non démontrées.
- **Analyse des écarts :** calculer un score déterministe et configurable, en affichant séparément les exigences obligatoires non satisfaites.
- **Veille du marché :** agréger les compétences demandées à partir de sources autorisées.
- **Roadmap personnalisée :** proposer des apprentissages, projets et ressources sur 30, 60 ou 90 jours.
- **Amélioration du CV et rapport :** suggérer des reformulations fondées sur les faits et produire un rapport exportable.

## Architecture et technologies

Le projet utilise un **monorepo modulaire**, avec un frontend et un backend. Les composants IA seront ajoutés progressivement selon les besoins.

| Couche | Technologies | Usage actuel |
| --- | --- | --- |
| Backend | Python 3.12, FastAPI, Pydantic | API et contrats de données |
| Parsing documentaire | PyMuPDF | Extraction locale du texte et de sa provenance |
| Frontend | React, TypeScript, Vite | Page de statut de connexion |
| Données | PostgreSQL, Qdrant, Redis | Services Docker provisionnés, pas encore utilisés par l’application |
| Qualité | Pytest, Ruff, mypy, ESLint, TypeScript | Tests et vérifications statiques |
| Environnement | uv, npm, Docker Compose, GitHub Actions | Dépendances verrouillées, environnement local et workflow CI configuré |

**À venir :** LangGraph pour l’orchestration, MCP pour les outils externes, ESCO pour la normalisation et un moteur de recherche hybride pour retrouver les preuves. Aucun appel LLM n’est nécessaire au parsing actuel.

## Principes de conception

- **Traçabilité :** conserver la source et les passages qui justifient les résultats.
- **Fiabilité :** ne jamais inventer une compétence, une expérience ou un diplôme.
- **Explicabilité :** distinguer une similarité de texte d’une preuve de maîtrise ; le score ne représentera pas une probabilité de recrutement.
- **Confidentialité :** limiter les données conservées ou transmises ; le parser actuel fonctionne localement.
- **Efficacité mesurée :** établir une baseline avant d’ajouter du cache, du parallélisme ou des modèles plus complexes.
- **Développement progressif :** tester chaque brique et documenter les choix techniques.

## Essayer le projet

Prérequis : Python 3.12, uv 0.9.11, Node.js ≥ 22.12 et npm. Docker Desktop avec moteur Linux est nécessaire pour les services conteneurisés.

### Tester le parsing PDF

Depuis la racine du dépôt :

```powershell
cd backend
uv sync --locked
uv run --locked python scripts/create_sample_cv.py
uv run --locked python -m app.documents ../.runtime/cv-synthetique.pdf
```

Le générateur crée un document synthétique de deux pages et refuse d’écraser un fichier existant. Le parser affiche son résultat en JSON. Aucun compte fournisseur IA n’est requis.

### Lancer l’application locale

Depuis la racine, créer `.env` à partir de `.env.example` s’il n’existe pas, puis remplacer la valeur de démonstration de `POSTGRES_PASSWORD` par un mot de passe local.

```powershell
docker compose up --build -d --wait
```

Dans un autre terminal, depuis la racine :

```powershell
cd frontend
npm ci
npm run dev
```

- Interface : http://127.0.0.1:5173
- Documentation API : http://127.0.0.1:8000/docs
- Santé du backend : http://127.0.0.1:8000/api/v1/health/ready

L’interface affiche actuellement la connexion au backend. Les bases ne publient aucun port sur l’hôte. L’application reste destinée au développement local ; l’authentification n’est pas encore implémentée.

Pour arrêter les conteneurs en conservant leurs volumes : `docker compose down`.

## Organisation du dépôt

```text
backend/          API, parsing documentaire et tests
frontend/         Interface React et TypeScript
infrastructure/   Configuration complémentaire Docker
datasets/         Conventions pour les données synthétiques
experiments/      Futurs benchmarks reproductibles
docs/             Architecture, décisions et suivi du projet
.github/workflows/ Vérifications CI
```

## Documentation

- [Guide de développement et dépannage](docs/DEVELOPMENT.md)
- [Comprendre et tester le parsing PDF](docs/PDF_PARSING.md)
- [Spécification fonctionnelle](docs/PROJECT_SPEC.md)
- [Architecture](docs/ARCHITECTURE.md) et [décisions techniques](docs/DECISIONS.md)
- [Roadmap](docs/ROADMAP.md) et [état détaillé de l’avancement](docs/PROGRESS.md)
- [Stack technique](docs/TECH_STACK.md) et [stratégie d’évaluation](docs/EVALUATION.md)

---

Projet de portfolio et de fin d’études, construit progressivement autour du Data Engineering, du RAG et de l’ingénierie des systèmes IA.
