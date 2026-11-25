# Stratégie d'évaluation — planifiée

Aucun benchmark IA ni gain mesuré en phase 0. Les tests actuels portent uniquement sur la fondation technique.

## Données et protocole
CV synthétiques/anonymisés et offres exploitables avec provenance/licence. Annoter exigences, compétences normalisées, extraits et pertinence des correspondances ; conserver les désaccords et règles d'annotation. Séparer train/développement/test par candidat et offre, puis dédoublonner avant partition pour prévenir les fuites. Ne pas ajuster prompts ou poids sur le test final.

## Comparaisons contrôlées
- Retrieval : mots-clés exacts, BM25, dense, hybride, hybride + reranking.
- Architecture : LLM unique, RAG simple, multi-agents.
- Optimisation : baseline, cache, routing, parallélisme, combinaison.

Garder corpus, requêtes, matériel et budgets comparables ; figer versions de modèles, prompts, paramètres, seeds et commit. Mesurer froid/chaud séparément ; plusieurs répétitions et dispersion, coûts fondés sur usage réellement observé et tarifs datés.

## Métriques
Extraction/classification : précision, rappel, F1 et macro-F1. Retrieval : Recall@K et MRR avec K annoncé. Système : P50/P95, tokens, coût par analyse, cache hit rate, workflow success rate ; rapporter taille d'échantillon et échecs. Scoring : cas limites, valeurs absentes, non-double-comptage et obligations affichées séparément.

Un manifeste d'expérience doit conserver configuration, identifiants de partition, environnement, résultats bruts et commande reproductible. Aucun gain ne sera annoncé sans baseline et mesure réelle. Seuils d'acceptation à fixer sur le jeu de développement avant le test final.
