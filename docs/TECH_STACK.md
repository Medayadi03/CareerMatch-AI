# Stack technique

## Ajout phase 1 — parsing local
PyMuPDF **1.26.7**, verrouillé dans pyproject.toml et uv.lock, pour extraire texte et coordonnées sans dépendance d'inférence obligatoire. Aucune installation d'OCR, de LLM ou de service documentaire supplémentaire. Voir PDF_PARSING.md pour les compromis, la licence annoncée et les limites.

## Installée / configurée en phase 0
| Composant | Version | Motif |
| --- | --- | --- |
| Python | 3.12, image 3.12.12 | Cible demandée |
| uv | 0.9.11 | Environnement et lockfile |
| FastAPI | 0.121.2 | API typée et OpenAPI |
| Pydantic / settings | 2.12.4 / 2.12.0 | Contrats et environnement |
| Uvicorn | 0.38.0 | Serveur ASGI |
| HTTPX / Pytest | 0.28.1 / 9.0.1 | Tests HTTP |
| Ruff / mypy | 0.14.5 / 1.18.2 | Lint, formatage et typage strict |
| React / React DOM | 19.2.0 | Interface minimale |
| TypeScript / Vite | 5.9.3 / 7.3.8 | Typage et build |
| ESLint / typescript-eslint | 10.15.0 / 8.74.0 | Qualité frontend |
| PostgreSQL | 17.6-bookworm | Future persistance relationnelle |
| Qdrant | v1.15.5 | Future recherche vectorielle |
| Redis | 7.4.7-alpine | Futur cache |
| BusyBox | 1.37.0-musl | Sonde HTTP Qdrant |

Les manifestes et lockfiles sont la référence exhaustive. Compatibilité vérifiée par installation et checks locaux, sous réserve des limites signalées dans PROGRESS. Versions fixes ne signifie pas absence de vulnérabilités ; réévaluer avant exposition externe.

## Planifiée, non installée
SQLAlchemy 2/Alembic, LangGraph, LangChain si utile, MCP Python SDK, Sentence Transformers, BM25, cross-encoder, PyMuPDF, ESCO ; Tailwind/shadcn/ui/Recharts/TanStack Query/React Router selon fonctionnalités. PostgreSQL/Qdrant/Redis ne sont pas encore utilisés par l'application.

## Optionnelle ou à évaluer
BGE-M3 multilingue selon ressources et mesures ; Docling si parsing insuffisant ; Ollama et quantification selon matériel ; S3/EC2/HTTPS au déploiement ; OpenTelemetry/Langfuse/Prometheus/Grafana progressivement ; Playwright et Locust pour les phases correspondantes. Aucun outil lourd installé dès maintenant.
