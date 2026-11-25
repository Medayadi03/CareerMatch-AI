# Spécification fonctionnelle

## Objectif
CareerMatch AI aide étudiants, jeunes diplômés et ingénieurs à comprendre leur adéquation à un poste et à progresser. Horizon : environ 30 jours intensifs. La compréhension et l'explication des décisions techniques font partie du livrable PFE.

## Implémenté — phase 0
API de santé, page React affichant le statut de connexion, configuration et socle qualité. Aucun traitement métier.

## Extension phase 1 — parsing PDF uniquement
Lecture locale du texte des PDF en pages et blocs avec coordonnées, version du parser et empreinte de source ; erreurs typées et avertissements d'extraction vide/partielle. Commande CLI et tests synthétiques. Aucun profil sémantique, OCR, import frontend ou stockage de CV.

## Planifié
1. **Resume & Job Matching** : PDF et offre texte en entrée ; extraction structurée des compétences, expériences, formations et projets ; exigences obligatoires/facultatives ; score global/par catégorie, preuves paginées, correspondances partielles et lacunes.
2. **Market Intelligence** : poste, localisation, expérience et contrat ; APIs autorisées, normalisation ESCO, dédoublonnage et fréquence des compétences ; sources conservées et biais d'échantillonnage expliqués.
3. **Career Roadmap** : profil et lacunes vers plan 30/60/90 jours avec ressources vérifiées, projets, certifications et critères de validation.
4. **Resume Optimization** : reformulations fondées uniquement sur les faits existants ; aucune invention.
5. Rapport PDF exportable.

## Contraintes
Traçabilité des sources et passages ; absence de preuve distincte d'une absence de compétence. Une similarité sémantique ne prouve pas la maîtrise. Score déterministe configurable : technique 45 %, expérience 25 %, projets 15 %, exigences spécifiques 10 %, formation 5 % (hypothèses à valider). Pas de double comptage ; valeurs inconnues explicites ; exigences obligatoires non satisfaites affichées séparément. Le score n'est pas une probabilité de recrutement.

Données synthétiques/anonymisées ; aucun attribut personnel hors compétences dans le score. Isolation par utilisateur, validation PDF, limites, suppression, rétention, protection contre injections et minimisation des transmissions avant utilisation réelle.

## Sources candidates, non intégrées
France Travail (https://francetravail.io/), Adzuna (https://developer.adzuna.com/), ESCO (https://esco.ec.europa.eu/), GitHub (https://docs.github.com/en/rest), catalogues officiels. Vérifier accès, licences et quotas au moment de l'intégration. Saisie manuelle d'offre toujours possible ; aucun scraping LinkedIn non autorisé.
