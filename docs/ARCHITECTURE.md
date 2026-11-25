# Architecture

## Extension autorisée — phase 1, parsing local
`python -m app.documents fichier.pdf` appelle le module documentaire indépendant de FastAPI. Un contrat Pydantic décrit les pages et blocs ; PyMuPDF extrait le texte ; la CLI affiche le JSON sans persistance. Pas de connexion aux bases ni de route upload à ce stade. Voir PDF_PARSING.md pour le flux, les limites et les prérequis avant exposition HTTP.

## Actuelle — phase 0
Correction du 25 novembre : le backend rejoint également un réseau `access` pour publier son port loopback. PostgreSQL, Qdrant et Redis restent uniquement sur `internal`. La sortie réseau du backend est possible ; les intégrations externes restent non implémentées.
Navigateur React → HTTP GET readiness → FastAPI (routes, configuration Pydantic, cycle de vie, logs JSON).

FastAPI tourne localement ou dans Docker sous UID 10001. PostgreSQL, Qdrant et Redis sont provisionnés sur un réseau interne sans ports publiés, mais aucune connexion applicative n'existe encore. L'API est indépendante de leur disponibilité. Vite tourne sur l'hôte. Le backend ne possède ni authentification ni endpoints de données.

`api/` contient les contrats HTTP ; `core/` configuration et logging ; `main.py` assemble l'application. Un seul backend, aucun service IA séparé aujourd'hui.

## Cible — planifiée
Frontend React → Career API → orchestration IA LangGraph, organisée d'abord en modules séparables : Document Intelligence, Retrieval Engine, Recommendation Engine, LLM Gateway, Evaluation et Observability. MCP Market Intelligence sera une frontière d'outillage explicite. Aucun microservice par agent.

Agents : CV Extraction et Job Description indépendants ; Skills Matching pour retrouver les preuves ; Market Intelligence via MCP ; Gap Analysis avec scoring déterministe ; Recommendation pour roadmap. Shared state typé, routage conditionnel, parallélisme des branches indépendantes, délais, retries bornés, gestion d'erreurs, traces. Checkpointing seulement si nécessaire.

Pipeline : acquisition → parsing → nettoyage → extraction → normalisation → validation → dédoublonnage → embeddings → index → recherche lexicale/sémantique → reranking → preuves → score déterministe → gaps → recommandations.

## Évolutions conditionnelles
Service IA distinct si charge ou cycle de déploiement le justifie ; stockage S3 et worker si fichiers/tâches longues le nécessitent ; sortie réseau contrôlée lors des appels fournisseurs. SQLAlchemy et Alembic seront ajoutés avec le premier modèle persistant. L'API readiness vérifiera alors uniquement les dépendances requises, avec délais bornés.
