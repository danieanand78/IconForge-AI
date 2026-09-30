# [Institut Supérieur Polytechnique de Madagascar - ISPM](http://www.ispm-edu.com/)

## Examen de fin d’études - Master 2 AI Engineering

# Thème du Hackathon

## IconForge AI - Génération d’une famille cohérente d’icônes SVG

*****veuillez decompresser tous les fichiers zip dans les dossiers ou ils sont********

> Notre système consiste à générer automatiquement une collection d’icônes SVG cohérentes à partir d’une requête entrée par un utilisateur. Le processus consiste à analyser la demande afin d’identifier le concept et les mots-clés, à intégrer les spécifications de la charte graphique, puis à générer des éléments SVG en respectant un style, des couleurs, des proportions et des règles graphiques communs à l’ensemble de la collection.


# Liste des contributeurs

| Nom | Prénom(s) | Classe | Numéro | Rôle |
|---|---|---|---|---|
|     ANDRIAKOTO    |  Rah-Maesch   | IMTICIA 5 | 12 | NLP et SVG Generator |
|   ANDRIAMAHENINA  |   Aina Loïc   | IMTICIA 5 | 11 | NLP et SVG Generator |
| RANDRIANANTENAINA |  Jean Carlos  | IMTICIA 5 | 07 | SVG analyzer(extraction) |SVG Validator|
|       DANIE       |     Anand     | IMTICIA 5 | 04 | Design Interface et Extraction charte|
|  RANDRIAMANALINA  | Lalaina Jimmy | IMTICIA 5 | 10 | Design Interface et Extraction charte |


# Résumé du travail

## Problématique

Le problème traité est la géneration d'une collection de logo en SVG à partir de concepts et des spécifications graphique, le tout sous contrainte de charte commune. La cohérence est plus difficile car tous les icones doivent conserver les mêmes paramètres : couleur, proportions, épaisseur de traits..., même s'ils sont de concepts différents.


## Approche adoptée

Lecture à l’exécution de la charte et des références
Extraction du langage visuel
Génération du SVG
Validation
Evaluation et raffinement.

## Résultats obtenus

Présentez vos principaux résultats sur les concepts publics et une découverte importante issue de vos expériences.

## Mots-clés

`SVG`, `AI Engineering`, `évaluation`, `cohérence visuelle`, `génération`, ...

# Installation

## Prérequis

- système d’exploitation testé : Windows 10
- version de Python, Node.js ou autre runtime : Python 3.13.2 - React 19.2.0 - Lucidreact 0.575 - TailWind CSS - TypeScript 5.8.3 - Vite 8.1.5 - spacy - ntlk - wordnet - omw 2.0 - model :"fr_core_news_sm" - transformers torch sentecepiece - llama cpp
- ressources matérielles nécessaires : Gemini - ChatGPT - Lovable - Cloud - Copilot
- variables d’environnement :

## Commandes d’installation

```bash
pip install spacy nltk transformers torch sentencepiece

llama cpp

python -m spacy download fr_core_news_sm

dans python : import nltk
              nltk.download("wordnet")
              nltk.download("omw-1.4")


```

# Exécution

La commande de référence est :

```bash
python generate.py --input requests.json --output outputs/
```

Si votre stack utilise une autre commande, documentez l’adaptateur `run.sh` ou `run.bat` offrant le même contrat.

## Exemple reproductible

```bash
# Commande complète permettant de reproduire vos sorties publiques
```

# Architecture du système
Le système repose sur une architecture en pipeline permettant de transformer une demande formulée en langage naturel en une icône SVG conforme à une charte graphique, puis d'évaluer automatiquement sa conformité.

L'architecture sépare volontairement les tâches génératives des tâches déterministes. L'IA est utilisée pour comprendre le besoin et générer le SVG, tandis que les contraintes objectives de la charte sont contrôlées par un validateur programmatique.

1. Flux général

Le flux de traitement est le suivant :
Prompt utilisateur
       │
       ▼
┌──────────────────────┐
│ Analyse du concept   │
│ + compréhension IA   │
└──────────┬───────────┘
           │
           ├──────────────► Prompt structuré
           │
           ▼
┌──────────────────────┐
│ Charte graphique     │
│ Markdown             │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────┐
│ Extracteur de spécification│
└────────────┬───────────────┘
             │
             ▼
      specification.json
             │
             ▼
┌────────────────────────────┐
│ Générateur IA de SVG       │
└────────────┬───────────────┘
             │
             ▼
        fichier SVG
             │
             ▼
┌────────────────────────────┐
│ Validateur déterministe    │
└────────────┬───────────────┘
             │
       ┌─────┴─────┐
       │           │
    Invalide      Valide
       │           │
       │           ▼
       │    ┌──────────────┐
       │    │ Évaluateur   │
       │    └──────┬───────┘
       │           │
       │           ▼
       │      Score final
       │           │
       └─────►─────┴──────► Résultat utilisateur
       2. Composants du système
2.1. Prompt utilisateur

L'utilisateur fournit une demande en langage naturel, par exemple :

« Crée une icône représentant un dossier médical pour une application de clinique. »

Le prompt contient principalement :

le concept à représenter ;
le type d'icône souhaité ;
éventuellement des contraintes particulières.

Il constitue l'entrée du système.

2.2. Analyse du concept

Cette étape utilise un modèle d'IA pour interpréter le prompt utilisateur.

Elle permet notamment d'identifier :

le sujet de l'icône ;
les objets à représenter ;
les éléments importants du concept ;
les éléments à éviter ;
les caractéristiques graphiques pertinentes.

L'objectif n'est pas encore de produire le SVG, mais de transformer une demande vague en description exploitable par les étapes suivantes.

Le système produit alors un prompt structuré.

Exemple :

{
  "concept": "dossier médical",
  "elements": [
    "dossier",
    "symbole médical"
  ],
  "style": "icône simple",
  "niveau_detail": "faible"
}
3. Charte graphique

La charte graphique constitue la source de vérité du système.

Elle décrit les règles que doivent respecter les icônes générées.

Elle peut être stockée sous forme Markdown et contenir différentes catégories :

Catégorie	Exemple de contrainte
Couleurs	couleurs autorisées
Géométrie	grille, proportions, viewBox
Traits	largeur, terminaisons, jonctions
Éléments	primitives autorisées/interdites
Composition	densité, nombre de formes
Style	vocabulaire graphique
Effets	ombres, gradients interdits, etc.

Il est important de distinguer cette charte des informations extraites du prompt.

Le prompt décrit ce que l'utilisateur veut.

La charte décrit comment cela doit être représenté.

4. Extracteur de spécification

L'extracteur transforme les règles de la charte Markdown en une représentation structurée et exploitable par le programme.

La sortie est specification.json.

Par exemple :

{
  "viewBox": "0 0 24 24",
  "couleurs_autorisees": [
    "#FFD21E",
    "#000000"
  ],
  "stroke": {
    "width": 2,
    "linecap": "round",
    "linejoin": "round"
  },
  "interdictions": [
    "gradient",
    "filter",
    "shadow"
  ]
}

Cette représentation intermédiaire est importante car les composants suivants n'ont pas besoin d'interpréter directement le Markdown.

On obtient donc :

Charte Markdown
       │
       ▼
Extracteur
       │
       ▼
specification.json
       │
       ├── règles de couleurs
       ├── règles géométriques
       ├── règles de traits
       ├── règles de composition
       └── éléments interdits
5. Générateur IA de SVG

Le générateur reçoit deux informations principales :

le concept demandé par l'utilisateur ;
la spécification graphique extraite de la charte.

Il produit ensuite le fichier SVG.

Schématiquement :

Prompt structuré
       +
Specification.json
       │
       ▼
   Modèle IA
       │
       ▼
    SVG

Le modèle IA est donc responsable de la génération, mais il ne doit pas être considéré comme le mécanisme de validation.

C'est une distinction importante :

L'IA propose une solution ; le validateur détermine si cette solution respecte les règles.

6. Validateur déterministe

Le SVG généré est ensuite analysé par un validateur programmatique.

Cette étape est déterministe : à entrée identique et règles identiques, elle doit produire le même résultat.

Le validateur vérifie par exemple :

la présence et la valeur du viewBox ;
les couleurs utilisées ;
les fill et stroke ;
la largeur des traits ;
les terminaisons (stroke-linecap) ;
les jonctions (stroke-linejoin) ;
les éléments SVG interdits ;
les gradients ;
les filtres ;
certaines contraintes géométriques.

Exemple :

SVG généré
    │
    ▼
Validateur
    │
    ├── viewBox ────────► OK / ERREUR
    ├── couleurs ───────► OK / ERREUR
    ├── stroke ─────────► OK / ERREUR
    ├── éléments ───────► OK / ERREUR
    └── effets ─────────► OK / ERREUR

Le résultat peut être :

{
  "valide": false,
  "erreurs": [
    "viewBox incorrect",
    "Couleur interdite",
    "Gradient interdit"
  ]
}
7. Évaluateur

Si le SVG passe les contrôles obligatoires, il est transmis à l'évaluateur.

L'évaluateur mesure la qualité et la conformité du SVG selon plusieurs critères.

Par exemple :

             SVG valide
                 │
                 ▼
        ┌─────────────────┐
        │    Évaluateur   │
        └────────┬────────┘
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    Style    Géométrie  Composition
       │         │         │
       └─────────┼─────────┘
                 ▼
             Score final

Le score peut être composé de plusieurs sous-scores :

Score final =
    conformité graphique
    + cohérence géométrique
    + respect du style
    + qualité de composition

La pondération exacte dépend des critères définis dans le sujet.

8. Boucle d'amélioration

La boucle d'amélioration permet éventuellement de corriger un SVG qui ne respecte pas les contraintes.

Le principe est :

Génération
    │
    ▼
Validation
    │
    ├── Conforme ──► Évaluation ──► Résultat
    │
    └── Non conforme
             │
             ▼
       Erreurs détectées
             │
             ▼
      Nouvelle génération
             │
             ▼
         Validation

Par exemple :

Génération 1
     │
     ▼
❌ couleur interdite
     │
     ▼
Correction du prompt
     │
     ▼
Génération 2
     │
     ▼
❌ mauvais viewBox
     │
     ▼
Correction
     │
     ▼
Génération 3
     │
     ▼
✅ conforme

Cette boucle peut être limitée à un nombre maximal d'itérations afin d'éviter une génération infinie.

9. Représentations intermédiaires

L'architecture utilise plusieurs représentations successives :

Langage naturel
      ↓
Prompt structuré
      ↓
Charte Markdown
      ↓
Specification JSON
      ↓
SVG
      ↓
Résultat de validation
      ↓
Score final

Chaque représentation possède un rôle différent.

Représentation	Rôle
Prompt naturel	Expression du besoin utilisateur
Prompt structuré	Concept interprété et organisé
Charte Markdown	Règles graphiques lisibles par l'humain
specification.json	Règles exploitables automatiquement
SVG	Icône générée
Rapport de validation	Conformité objective
Score	Évaluation globale




# Formalisation de la charte graphique

Le programme extraire_specification.py transforme à chaque exécution le contenu de la charte graphique Markdown et les rapports techniques des SVG de référence en une structure specification.json.

L'objectif est de ne pas coder en dur les valeurs de la charte graphique. Les valeurs comme le viewBox, les couleurs, les dimensions de la zone utile ou l'épaisseur des traits sont lues depuis le fichier Markdown fourni à l'exécution.

Le processus est donc :

brand-guidelines.md
        +
SVG de référence
        │
        ▼
extraire_specification.py
        │
        ├── Extraction charte
        ├── Extraction observations SVG
        ├── Détection d'anomalies
        └── Fusion
        │
        ▼
specification.json
1. Palette

La palette est extraite directement de la section ## Palette de la charte.

Le programme recherche les codes hexadécimaux avec une expression régulière :

re.findall(r"#[0-9A-Fa-f]{3,6}", ligne)

Chaque couleur est ensuite représentée avec :

son nom ;
son code HEX ;
son rôle ;
son statut.

Par exemple :

{
  "palette": {
    "couleurs_prescrites": [
      {
        "nom": "Jaune principal",
        "hex": "#FFD21E",
        "role": "couleur principale",
        "statut": "officielle"
      }
    ]
  }
}

Les couleurs réellement utilisées dans les SVG de référence sont également récupérées depuis les pré-rapports :

rapports_couleurs = sorted({
    c
    for r in rapports_svg
    for c in r.get("couleurs_utilisees", [])
})

On obtient donc une distinction entre :

couleurs prescrites par la charte
              ≠
couleurs observées dans les références

Cette distinction permet notamment de détecter les incohérences.

2. Géométrie et zone utile

La géométrie technique est extraite de la section Format SVG.

Le viewBox est recherché directement dans le texte :

viewbox_match = re.search(
    r'viewBox\s*=\s*["`]([^"`]+)',
    format_technique,
    re.IGNORECASE
)

Le résultat est ensuite stocké dans :

{
  "format_technique": {
    "viewBox": "0 0 24 24"
  }
}

La zone utile est également extraite de la charte à partir des coordonnées x et y.

Elle est représentée sous forme structurée :

{
  "zone_utile": {
    "x_min": 2,
    "x_max": 22,
    "y_min": 2,
    "y_max": 22
  }
}

Parallèlement, les SVG de référence fournissent leur bounding box réelle dans les pré-rapports.

Le système peut donc conserver :

Charte
  │
  ├── viewBox prescrit
  └── zone utile prescrite

Références
  │
  └── bbox réellement observée

Cela permet au validateur ultérieur de comparer une icône générée aux contraintes géométriques.

3. Traits et arrondis

Les caractéristiques des traits sont regroupées dans la section :

"trait"

Ton programme extrait notamment :

l'épaisseur prescrite ;
les épaisseurs observées dans les références ;
stroke-linecap ;
stroke-linejoin.

Par exemple :

{
  "trait": {
    "epaisseur_prescrite": 2,
    "epaisseur_observee_dans_references": [
      2
    ],
    "linecap_prescrit": "round",
    "linejoin_prescrit": "round"
  }
}

Les arrondis sont donc représentés par les propriétés SVG :

stroke-linecap = round
stroke-linejoin = round

Le programme ne suppose pas que l'épaisseur vaut nécessairement 2 : il la recherche dans le texte de la section Langage graphique.

4. Densité et complexité

C'est ici qu'il faut être particulièrement prudent dans votre présentation.

Dans la version actuelle de ton code, la densité et la complexité ne sont pas réellement extraites sous forme de mesures numériques.

Le code conserve certaines observations provenant des SVG :

"observations_references": {
    r["fichier"]: {
        "couleurs": r.get("couleurs_utilisees", []),
        "bbox": r.get("bbox_reelle_contenu")
    }
}

Mais il ne calcule pas actuellement des indicateurs comme :

nombre de formes ;
nombre de chemins ;
nombre de nœuds ;
ratio de remplissage ;
densité visuelle ;
niveau de complexité géométrique.

Il faut donc éviter d'affirmer dans le rapport que ton programme mesure automatiquement la complexité si ce n'est pas le cas.

Tu peux plutôt écrire :

La version actuelle conserve les informations nécessaires à l'analyse qualitative du niveau de détail et de la composition, notamment les observations issues des SVG de référence. La densité et la complexité ne sont cependant pas encore représentées par un indicateur numérique déterministe.

C'est plus honnête techniquement.

5. Contraintes hard

Les contraintes hard sont les règles qui doivent obligatoirement être respectées.

Dans ton architecture, elles sont principalement représentées dans :

{
  "format_technique": {},
  "palette": {},
  "trait": {},
  "interdits_stylistiques": []
}

Elles comprennent notamment :

viewBox ;
zone utile ;
nombre maximal de couleurs ;
couleurs prescrites ;
épaisseur de trait ;
linecap ;
linejoin ;
éléments SVG interdits ;
effets stylistiques interdits.

Elles seront ensuite utilisées par le validateur déterministe.

Exemple :

specification.json
       │
       ▼
Validateur
       │
       ├── viewBox correct ?
       ├── couleur autorisée ?
       ├── stroke correct ?
       ├── élément interdit ?
       └── zone utile respectée ?

L'intérêt de cette séparation est important :

Une IA peut générer une icône différente à chaque exécution, mais les règles hard restent contrôlées de manière déterministe.

6. Contraintes soft

Les contraintes soft correspondent aux caractéristiques qualitatives qui décrivent le style sans nécessairement constituer une condition binaire d'invalidité.

Elles sont notamment stockées dans :

{
  "style_qualitatif": {
    "criteres_charte": [],
    "observations_references": {}
  },
  "coherence_collection": {
    "criteres": []
  },
  "grille_construction": {
    "note": "..."
  }
}

Le programme récupère par exemple les listes de critères présentes dans la charte :

[line.strip(" -*")
 for line in trait_texte.splitlines()
 if line.strip().startswith("-")]

Ces informations peuvent ensuite être utilisées par l'évaluateur pour apprécier :

le niveau de détail ;
le vocabulaire graphique ;
la simplicité ;
la cohérence avec la collection ;
l'ambiance visuelle ;
la composition.

La différence fondamentale est donc :

HARD
→ vérification déterministe
→ OK / ERREUR

SOFT
→ évaluation qualitative
→ score / appréciation
7. Comment les valeurs de la charte ne sont pas figées

C'est un point central de votre architecture.

Le programme ne contient pas directement des valeurs telles que :

viewBox = "0 0 24 24"
couleur = "#FFD21E"
stroke = 2

comme règles générales.

À chaque exécution, il lit :

brand-guidelines.md

puis extrait les valeurs.

Ainsi, si la charte change :

Ancienne charte
viewBox = 0 0 24 24
couleur = #FFD21E

        ↓

Nouvelle charte
viewBox = 0 0 32 32
couleur = #FF0000

la génération de specification.json utilise automatiquement les nouvelles valeurs.

Le fichier de sortie devient donc dépendant de la charte réellement fournie :

Charte A ──► specification A
Charte B ──► specification B
Charte C ──► specification C

Le programme ajoute également un hash SHA-256 de la charte :

spec["meta"]["hash_charte"] = hashlib.sha256(
    charte_texte.encode("utf-8")
).hexdigest()

Cela permet d'identifier précisément la version du document ayant servi à produire la spécification.

8. Les prompts ne contiennent pas les valeurs graphiques

Ton architecture va également dans le bon sens concernant le prompt IA.

Le system prompt indique au modèle :

« N'invente aucune valeur absente de la charte »

et précise que les faits numériques doivent provenir prioritairement de la charte.

Le modèle reçoit donc :

[CHARTE_TEXTE]
contenu réel de brand-guidelines.md
[/CHARTE_TEXTE]

plutôt qu'un prompt contenant par exemple :

Utilise toujours #FFD21E
Utilise toujours viewBox 0 0 24 24
Utilise toujours stroke 2

Cela évite de transformer les valeurs d'une charte particulière en constantes globales du système.

# Stratégie de génération

Un concept exprimé en langage naturel est d’abord analysé par le module NLP, qui identifie le subject et les keywords. Ces informations sont ensuite transformées en une représentation intermédiaire symbolique des éléments visuels à produire, puis le générateur assemble ces éléments en SVG en appliquant les paramètres de la charte graphique : les choix de formes et de structure sont symboliques et déterministes, tandis que le choix/interprétation du concept peut être génératif ; les dimensions, positions, couleurs et épaisseurs sont paramétriques.

# Évaluation et boucle d’amélioration

## Contraintes déterministes

Présentez les validateurs utilisés et les erreurs qu’ils détectent.

## Contraintes qualitatives

Présentez les critères de fidélité sémantique, de lisibilité, de simplicité et de style.

## Cohérence de collection

Définissez votre fonction ou votre protocole d’évaluation du set complet :

\[
Consistency(S)=f(palette,\ trait,\ densité,\ géométrie,\ complexité,\ style)
\]

## Boucle Generate - Evaluate - Refine

Décrivez la boucle, ses conditions d’arrêt et les résultats mesurés avant/après.

# Résultats et expériences

Présentez au minimum :

- les résultats sur les concepts publics ;
- les taux de conformité technique ;
- les scores ou observations qualitatives ;
- un test sur des concepts de contrôle hors domaine ;
- un test avec une charte variante et d’autres SVG de référence, sans modification du code ;
- la dégradation observée séparément lors du changement de concepts et du changement de charte ;
- un échec instructif ;
- les limites actuelles.

# Structure du dépôt

```text
# À compléter
```

# Manifeste de remise

Le fichier `manifest.json` doit respecter `submission-template/manifest.schema.json` et utiliser les clés imposées par le sujet :

```json
{
  "equipe": ["Nom Prénom", "..."],
  "methode": "...",
  "modeles": [{"nom": "...", "version": "...", "local": true}],
  "bibliotheques": ["..."],
  "services_distants": [],
  "repli_gratuit": "..."
}
```

# Vidéo de présentation

- lien vers la vidéo de 3 à 5 minutes : **À compléter**
- durée : **À compléter**

# Transparence sur les outils IA utilisés dans le développement et dans la documentation

Toute utilisation d’un outil d’IA doit être déclarée, y compris lorsqu’il a uniquement servi à reformuler la documentation. Ajoutez ou supprimez des lignes selon vos besoins.

## Outils IA utilisés dans le développement

| Outil ou modèle | Version | Mode d’accès | Utilisation précise | Parties produites ou modifiées | Vérification humaine |
|---|---|---|---|---|---|
| ChatGPT |  | gratuit | code | svg generator, validator, extraction charte | contrôle effectué |
| Gemini |  | gratuit | code | codes | contrôle effectué |
| Lovable |  | gratuit | interface | tout interface | contrôle effectué |

Pour chaque outil, précisez également :

- les prompts ou familles de prompts importants ;
- les modifications humaines apportées aux sorties ;
- les erreurs ou hallucinations détectées ;
- les éventuelles limites de reproductibilité ;
- la solution gratuite ou locale de repli si un service distant a été utilisé.

## Outils IA utilisés dans la documentation

| Outil ou modèle | Version | Document concerné | Nature de l’assistance | Vérification et corrections humaines |
|---|---|---|---|---|
| ChatGPT | | documentation sur le sujet, Readme  | compréhension du sujet, rédaction, reformulation| À compléter |

## Déclaration de transparence

> Nous déclarons avoir listé de manière fidèle les outils d’intelligence artificielle utilisés pour le développement et pour la documentation. Nous assumons la responsabilité finale du code, des SVG, des résultats, des analyses et des textes remis.

# Modèles, bibliothèques, données et services

| Ressource | Version ou commit | Licence | Usage | Lien |
|---|---|---|---|---|
| ntlk | |  | Concept NLP |  |
| spacy | |  | Concept NLP |  |
| wordnet | |  | Concept NLP |  |
| omw | 2.0 |  | Concept NLP |  |
| fr_core_news_sm | |  | Concept NLP |  |
| openai | |  | SVG Generator |  |
| x,l.etree.ElementTree | |  | SVG Generator |  |

# Contributions individuelles

Décrivez précisément les contributions de chaque membre. Les rôles généraux ne remplacent pas la description des tâches effectivement réalisées.
Rah-Maesch : Création du code SVG Generator
Loïc : Conception du modèle NLP pour le concept à dessiner
Carlos : Implémentation du SVG analyseur et SVG validator
Anand : Conception de tout interface
Jimmy : Extraction des spec et assemblement du projet

# Limites et améliorations possibles

Présentez les limites connues, les risques techniques, les biais de l’évaluation et ce que vous amélioreriez avec une journée supplémentaire.

# Licence et propriété

Indiquez la licence du dépôt et vérifiez que toutes les ressources externes sont compatibles avec cette licence.
