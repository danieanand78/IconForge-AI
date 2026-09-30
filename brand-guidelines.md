# IconForge AI — Charte « Hugging Face inspired »

> **Profil de développement.** Le jury remplacera ce fichier et le dossier `references/` aux mêmes emplacements lors de l’évaluation finale. Le système doit en extraire les contraintes à l’exécution ; aucune valeur de cette charte ne doit être considérée comme constante du challenge.

## 1. Positionnement

Cette charte est une **adaptation pédagogique non officielle** de certains éléments visibles de l’identité Hugging Face. Le challenge n’est ni produit, ni approuvé, ni sponsorisé par Hugging Face.

Les éléments authentiques retenus sont les couleurs publiées sur la page officielle des assets de marque :

- jaune : `#FFD21E` ;
- orange : `#FF9D00` ;
- gris : `#6B7280`.

Source : <https://huggingface.co/brand>

Le langage d’icônes décrit ci-dessous est créé spécialement pour le challenge. Il ne doit pas être présenté comme le système d’iconographie officiel de Hugging Face.

## 2. Utilisation de la marque

Le logo et l’emoji Hugging Face sont des **assets protégés**. S’ils sont fournis séparément par l’organisateur :

- ne pas les redessiner ou les reconstruire ;
- ne pas les déformer, recolorer ou découper ;
- ne pas intégrer leur visage dans une icône générée ;
- ne pas suggérer une affiliation officielle.

Les références du challenge reprennent une atmosphère chaleureuse et expressive, mais ne copient pas le logo.

## 3. Format SVG obligatoire

- SVG autonome et valide ;
- `viewBox="0 0 64 64"` ;
- fond transparent ;
- zone utile obligatoire : toute l’emprise visuelle, contours compris, doit rester dans `x = 5…59`, `y = 5…59` ;
- aucune image matricielle embarquée ;
- aucun texte, aucune police externe ;
- aucun script, lien externe ou animation ;
- aucun gradient, filtre, masque ou texture ;
- maximum **4 couleurs visibles** par icône.

## 4. Palette du challenge

| Rôle | Couleur | Statut |
|---|---:|---|
| Jaune principal | `#FFD21E` | couleur officielle publiée |
| Orange d’accent | `#FF9D00` | couleur officielle publiée |
| Gris secondaire | `#6B7280` | couleur officielle publiée |
| Encre sombre | `#111827` | couleur technique du challenge |
| Blanc | `#FFFFFF` | réserve ou détail intérieur |

Le jaune doit constituer la masse colorée dominante de la collection. L’orange sert à créer du rythme, une ombre plate ou un accent sémantique. L’encre sombre structure les silhouettes.

## 5. Langage graphique

- formes pleines, simples et généreuses ;
- silhouette douce, compacte et immédiatement reconnaissable ;
- contours sombres de `2.5` unités lorsqu’un contour est nécessaire ;
- `stroke-linecap="round"` et `stroke-linejoin="round"` ;
- coins arrondis et détails expressifs ;
- légère asymétrie autorisée pour éviter un rendu trop mécanique ;
- ombres uniquement sous forme d’aplats orange, sans flou ;
- vue frontale ou quasi frontale ;
- lisibilité à **24 px**, **32 px** et **64 px**.

### Grille de construction souple

Le canevas utilise une grille logique de 64 unités. L’alignement sur des coordonnées entières ou demi-entières est recommandé pour les formes principales, mais il n’est pas éliminatoire : des corrections optiques et des courbes peuvent s’écarter de cette grille. La grille relève donc de l’évaluation stylistique, contrairement au `viewBox` et à la zone utile, qui sont déterministes.

Le style recherché est accueillant, ludique et technologique. Il ne doit être ni enfantin, ni photoréaliste, ni surchargé.

## 6. Cohérence de collection

Les icônes doivent partager :

- une proportion comparable entre jaune, orange et encre sombre ;
- une épaisseur optique stable ;
- des rayons et terminaisons cohérents ;
- des masses compactes entourées d’un espace respirant ;
- un niveau de détail comparable ;
- un équilibre commun entre expressivité et lisibilité fonctionnelle.

La cohérence ne signifie pas que toutes les icônes doivent avoir la même forme extérieure. Une collection réussie doit rester reconnaissable même lorsque les concepts exigent des compositions différentes.

## 7. Interdictions stylistiques

- pas de copie du visage ou des mains du logo Hugging Face ;
- pas d’emoji existant simplement recoloré ;
- pas de 3D, photoréalisme, texture ou ombre floue ;
- pas de contours d’épaisseurs arbitrairement mélangées ;
- pas de détails décoratifs sans rôle sémantique ;
- pas de jaune trop clair sur fond blanc sans contour suffisant.

## 8. Références fournies

- `formation.svg` — livre ouvert et étincelle d’apprentissage ;
- `informatique.svg` — terminal de code ;
- `recherche.svg` — document analysé à la loupe ;
- `reseau.svg` — réseau distribué ;
- `innovation.svg` — ampoule et étincelles.

Ces fichiers constituent un *few-shot visuel*. Ils montrent le langage attendu sans couvrir les concepts secrets du benchmark. Leur contenu sera lui aussi remplacé avec la charte lors du test de généralisation stylistique.

## 9. Évaluation

### Contraintes déterministes

Validité SVG, `viewBox`, palette, nombre de couleurs, transparence, zone utile stricte, attributs de trait et absence d’éléments interdits.

### Contraintes qualitatives

Fidélité au concept, respect souple de la grille, lisibilité à petite taille, simplicité, qualité visuelle, caractère chaleureux, cohérence stylistique et cohérence de la collection complète.
