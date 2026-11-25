# Atelier 1 — extraire le texte d'un CV PDF

## Objectif et frontière
Un PDF décrit l'affichage d'un document. Il ne contient pas nécessairement des champs « compétences » ou « expériences », ni même du texte : un scan contient souvent des images. Notre première brique transforme un PDF en pages et blocs textuels, sans interpréter leur sens.

`PDF local → validation → extraction par page → blocs avec coordonnées → contrat Pydantic → JSON`

Le résultat est une structure documentaire, pas encore un profil candidat. « Python » dans le texte reste une observation ; le parser ne conclut pas que le candidat maîtrise Python. ESCO, LLM, OCR, matching et scoring ne font pas partie de cet atelier.

## Les fichiers à lire dans l'ordre
1. `backend/app/documents/models.py` : les contrats de sortie et les limites. Pydantic valide la forme des données, pas la vérité de leur contenu.
2. `backend/app/documents/parser.py` : le traitement déterministe, sans dépendance HTTP ni base de données. `parse_pdf(bytes)` peut être réutilisé plus tard derrière une API ; `parse_pdf_file(Path)` lit un fichier local avec une borne de taille.
3. `backend/app/documents/__main__.py` : la commande utilisateur. Elle traduit les erreurs en messages stables et écrit le JSON sur stdout. La durée seulement est écrite sur stderr en cas de succès.
4. `backend/tests/test_pdf_parser.py` : des PDF construits en mémoire avec des contenus synthétiques connus. Les assertions comparent le résultat à ce contenu attendu.

## Pourquoi conserver les blocs ?
Un texte global perd sa provenance. Chaque bloc possède un identifiant local (ex. `p2-b1`), un texte et un rectangle `bbox = [x0, y0, x1, y1]`. Les coordonnées sont celles retournées par PyMuPDF dans le repère de la page non tournée, en points PDF ; la rotation est fournie séparément. La numérotation de pages commence à 1 pour l'utilisateur.

La provenance complète d'un passage est : empreinte du document + version du parser + numéro de page + identifiant du bloc. Le SHA-256 identifie les octets du fichier ; ce n'est ni une anonymisation, ni un identifiant utilisateur, ni un cache déjà implémenté. Des fichiers visuellement identiques peuvent avoir des empreintes différentes.

Le tri géométrique `sort=True` améliore certains documents dont l'ordre interne du texte est différent de l'affichage. Il ne reconstitue pas à lui seul l'ordre sémantique de plusieurs colonnes. Le texte extrait est conservé sans reformulation et sans suppression des accents ; les blocs entièrement blancs sont ignorés. Le texte de page est la concaténation des blocs. Aucun nettoyage agressif ne supprime des preuves potentielles.

## Validations et résultats
| Cas | Résultat |
| --- | --- |
| Fichier vide | `empty_file` |
| Plus de 10 Mio | `file_too_large` |
| Signature différente de `%PDF-` ou document illisible | `invalid_pdf` |
| PDF nécessitant un mot de passe | `encrypted_pdf` |
| Plus de 20 pages | `too_many_pages` |
| Plus de 200 000 caractères extraits | `too_much_text` |
| Fichier local inaccessible | `file_unreadable` |
| Page sans texte extractible | Avertissement `no_extractable_text` ; page conservée |
| Certaines pages sans texte | Avertissement document `partial_text` |
| Toutes les pages sans texte | Avertissement document `no_extractable_text` |
| PDF réparé à l'ouverture par le moteur | Avertissement `pdf_repaired` |

Une page sans texte peut être blanche, scannée ou contenir du texte sous forme de tracés. Nous ne l'appelons pas automatiquement « scan détecté ». Un PDF avec une couche OCR existante peut fournir du texte, dont l'exactitude n'est pas garantie. Les tableaux, annotations et champs de formulaire ne bénéficient pas d'une extraction spécialisée.

## Exercice local
Depuis `C:\Users\Admin\CareerMatchAI\backend` :

```powershell
.\.venv\Scripts\python.exe scripts/create_sample_cv.py
.\.venv\Scripts\python.exe -m app.documents ../.runtime/cv-synthetique.pdf
```

La première commande crée un CV **synthétique** de deux pages dans `.runtime`, ignoré par Git. Elle refuse d'écraser un fichier existant : ne la relancer que si le fichier n'existe pas. La seconde commande affiche le JSON, sans enregistrer le résultat sur disque. Si tu choisis une redirection vers un fichier, c'est cette redirection qui persiste les données.

Pour lire ton propre fichier local :

```powershell
.\.venv\Scripts\python.exe -m app.documents 'C:\chemin\cv.pdf'
```

Aucune donnée n'est envoyée à un fournisseur ou une base par cette commande. Le texte est affiché dans ton terminal : ne partage pas sa sortie s'il contient des données personnelles. Cette brique n'ajoute pas encore de bouton d'import au frontend ni de route HTTP.

Expériences pour comprendre :
1. Vérifie `page_count = 2` et retrouve « FastAPI » sur les bonnes pages.
2. Observe `p2-b1` et son rectangle : quel passage pourra-t-on citer plus tard ?
3. Relance sur le même fichier : l'empreinte et les données sont identiques, la durée peut varier.
4. Ajoute `--max-pages 1` : tu dois obtenir `too_many_pages` et un code de sortie 2 (`$LASTEXITCODE`).
5. Essaie un scan sans couche texte : vérifie l'avertissement, sans attendre de texte inventé.

## Efficacité et limites opérationnelles
Un seul passage d'extraction par page, sans rendu des images ni appel réseau/LLM. Le fichier lu est borné à `max_bytes + 1`, le nombre de pages est vérifié avant extraction, et le volume de texte est borné. Les limites peuvent être modifiées par arguments CLI ; elles sont des choix initiaux, pas des seuils optimisés scientifiquement.

La durée CLI mesure lecture, extraction, validation et écriture du JSON, hors démarrage/import Python. Une exécution sur un PDF synthétique n'est pas un benchmark représentatif. Aucun gain relatif n'est annoncé ; un futur protocole devra comparer un corpus fixe, qualité, mémoire et latences répétées.

Cette version locale ne possède pas de timeout de parsing ni de limite stricte sur la mémoire native utilisée pour décoder une page. Les limites de taille/pages/caractères ne protègent pas de tous les PDF malveillants ou très compressés. Avant une route d'upload accessible à des tiers, isoler le parsing dans un processus avec budgets temps/mémoire et contrôle de concurrence. Ne pas lancer PyMuPDF concurremment dans plusieurs threads sans traiter ses contraintes.

## Choix de dépendance
PyMuPDF 1.26.7 est verrouillé et n'ajoute pas de dépendances obligatoires d'inférence. La résolution initiale de la version 2.1 avait ajouté des composants de layout et ONNX inutiles pour cet atelier ; le manifeste et le lockfile retiennent la version légère. Son intégration mypy est limitée par l'absence de stubs : seule la bibliothèque externe est exemptée de l'analyse d'import, le code applicatif reste en mode strict.

La distribution annonce une licence AGPL ou commerciale ; le choix de distribution du projet devra en tenir compte. Ce document ne fixe pas la licence du repository.

Sources : [extraction par blocs et tri](https://pymupdf.readthedocs.io/en/latest/page.html), [distribution et licence PyMuPDF 1.26.7](https://pypi.org/project/PyMuPDF/1.26.7/).
