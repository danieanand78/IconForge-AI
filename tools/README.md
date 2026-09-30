# Validateur SVG paramétrable

Le contrôle complet utilise **Inkscape**, logiciel libre, pour mesurer l’emprise visuelle réelle, contours compris. Sans option supplémentaire, ce validateur applique uniquement le profil de la charte publique de développement.

## Validation d’un dossier

```bash
python tools/validate_svg.py outputs/public/ \
  --requests benchmark/public-concepts.json
```

Le validateur contrôle notamment :

- XML et `viewBox` ;
- couleurs explicites et palette ;
- maximum quatre couleurs ;
- attributs de contour ;
- scripts, CSS, liens, images et effets interdits ;
- zone utile stricte `5…59` ;
- nombre et noms des fichiers attendus.

Réussir ce contrôle ne démontre pas l’adaptation à une nouvelle charte. Lors de l’évaluation, le jury utilisera le même outil avec un profil confidentiel via `--profile`.

Vous pouvez créer votre propre profil de contrôle pour tester une charte variante :

```bash
python tools/validate_svg.py outputs/variant/ \
  --requests benchmark/public-concepts.json \
  --profile chemin/vers/votre-profil.json
```

## Utiliser la spécification extraite

Le validateur accepte directement le fichier produit par `extraire_specification.py`.
Les contraintes de palette, de géométrie et de traits sont alors lues à l'exécution :

```bash
python tools/validate_svg.py output.svg \
  --profile specification.json
```

Le format de profil plat historique reste accepté pour les profils personnalisés.

## Contrôle préliminaire sans Inkscape

```bash
python tools/validate_svg.py outputs/public/ --xml-only
```

Ce mode ignore la zone utile et ne constitue donc pas une validation finale.

## Évaluation qualitative et cohérence de collection

L'évaluateur de l'étape 4 calcule des indicateurs reproductibles à partir de la
collection : diversité de palette, dispersion du nombre de formes, densité des
formes pleines et occupation géométrique. Il utilise d'abord `validate_svg.py`
pour exclure les SVG techniquement invalides.

```bash
python evaluation/evaluate_collection.py outputs/public/ \
  --profile specification.json \
  --json
```

Le jugement de fidélité au concept ne peut pas être déduit de façon fiable du
XML seul. Il peut être ajouté explicitement dans un fichier d'annotations :

```json
{
  "cloud.svg": { "semantic_score": 0.9, "readability_score": 0.85 },
  "security.svg": { "semantic_score": 0.8, "readability_score": 0.9 }
}
```

```bash
python evaluation/evaluate_collection.py outputs/public/ \
  --profile specification.json \
  --annotations evaluation/annotations.json
```

Les scores sont normalisés entre 0 et 1. Le rapport expose les composantes de
cohérence afin que chaque gain soit vérifiable avant/après.

## Boucle Generate - Evaluate - Refine

L'étape 5 est orchestrée par `evaluation/refine_collection.py`. Elle exécute
une génération initiale pour chaque requête, évalue la collection complète,
écrit un feedback JSON par fichier, puis demande au générateur une nouvelle
version. Une nouvelle collection n'est conservée que si le tuple suivant est
strictement meilleur, dans cet ordre :

```text
(taux de validité technique, cohérence de collection, lisibilité)
```

La boucle s'arrête au premier candidat non améliorant ou après `--attempts`.
Le générateur est volontairement injecté par commande afin de rester compatible
avec un générateur local, paramétrique ou distant documenté.

La commande doit accepter les placeholders suivants :

- `{id}` : identifiant de la requête ;
- `{concept}` : concept en langage naturel ;
- `{context}` : contexte facultatif ;
- `{output}` : chemin du SVG à produire ;
- `{feedback}` : chemin du feedback JSON, vide pour la génération initiale.

Exemple avec un générateur local :

```bash
python evaluation/refine_collection.py \
  --input benchmark/public-concepts.json \
  --output outputs/public \
  --profile specification.json \
  --generator 'python generate_one.py --concept "{concept}" --output "{output}" --feedback "{feedback}"' \
  --attempts 2 \
  --json
```

`generate_one.py` doit écrire exactement un fichier SVG au chemin fourni. Le
feedback contient les erreurs techniques, les indicateurs mesurés et le score
du candidat précédent : le générateur peut s'en servir pour corriger sa sortie.
Les scores sémantiques peuvent être fournis avec `--annotations`; ils sont
évalués séparément car ils nécessitent un jugement explicite.
