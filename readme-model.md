# [Institut Supérieur Polytechnique de Madagascar - ISPM](http://www.ispm-edu.com/)

## Examen de fin d’études - Master 2 AI Engineering

# Thème du Hackathon

## IconForge AI - Génération d’une famille cohérente d’icônes SVG

> Remplacez ce paragraphe par une présentation concise de votre système, de son objectif et de votre approche principale.

# Liste des contributeurs

| Nom | Prénom(s) | Classe | Numéro | Rôle |
|---|---|---|---|---|
| À compléter | À compléter | À compléter | À compléter | À compléter |
| À compléter | À compléter | À compléter | À compléter | À compléter |
| À compléter | À compléter | À compléter | À compléter | À compléter |
| À compléter | À compléter | À compléter | À compléter | À compléter |
| À compléter | À compléter | À compléter | À compléter | À compléter |
| À compléter | À compléter | À compléter | À compléter | À compléter |
| À compléter | À compléter | À compléter | À compléter | À compléter |

# Résumé du travail

## Problématique

Expliquez en 2 à 3 phrases le problème traité et pourquoi la cohérence d’une collection d’icônes est plus difficile que la simple génération de SVG indépendants.

## Approche adoptée

Résumez votre chaîne : lecture à l’exécution de la charte et des références, extraction du langage visuel, représentation intermédiaire éventuelle, génération, validation, évaluation et raffinement.

## Résultats obtenus

Présentez vos principaux résultats sur les concepts publics et une découverte importante issue de vos expériences.

## Mots-clés

`SVG`, `AI Engineering`, `évaluation`, `cohérence visuelle`, `génération`, ...

# Installation

## Prérequis

- système d’exploitation testé : ...
- version de Python, Node.js ou autre runtime : ...
- ressources matérielles nécessaires : ...
- variables d’environnement : ...

## Commandes d’installation

```bash
# À compléter
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

Décrivez les composants, les flux de données, les modèles, les représentations intermédiaires, les validateurs et la boucle d’amélioration. Ajoutez un schéma si nécessaire.

# Formalisation de la charte graphique

Expliquez comment votre programme extrait et représente, à chaque exécution :

- la palette ;
- la géométrie et la zone utile ;
- les traits et arrondis ;
- la densité et la complexité ;
- les contraintes hard ;
- les contraintes soft.

Précisez comment vous empêchez les valeurs de la charte publique (`viewBox`, palette, largeur de trait, marges ou style) d’être figées dans le code ou dans les prompts.

# Stratégie de génération

Décrivez comment un concept en langage naturel devient un SVG. Précisez ce qui est génératif, paramétrique, symbolique ou déterministe.

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
| À compléter | À compléter | local, gratuit ou payant | code, SVG, prompts, tests, architecture... | fichiers ou composants concernés | contrôle effectué |

Pour chaque outil, précisez également :

- les prompts ou familles de prompts importants ;
- les modifications humaines apportées aux sorties ;
- les erreurs ou hallucinations détectées ;
- les éventuelles limites de reproductibilité ;
- la solution gratuite ou locale de repli si un service distant a été utilisé.

## Outils IA utilisés dans la documentation

| Outil ou modèle | Version | Document concerné | Nature de l’assistance | Vérification et corrections humaines |
|---|---|---|---|---|
| À compléter | À compléter | README, rapport, schéma, vidéo... | rédaction, reformulation, traduction, synthèse... | À compléter |

## Déclaration de transparence

> Nous déclarons avoir listé de manière fidèle les outils d’intelligence artificielle utilisés pour le développement et pour la documentation. Nous assumons la responsabilité finale du code, des SVG, des résultats, des analyses et des textes remis.

# Modèles, bibliothèques, données et services

| Ressource | Version ou commit | Licence | Usage | Lien |
|---|---|---|---|---|
| À compléter | À compléter | À compléter | À compléter | À compléter |

# Contributions individuelles

Décrivez précisément les contributions de chaque membre. Les rôles généraux ne remplacent pas la description des tâches effectivement réalisées.

# Limites et améliorations possibles

Présentez les limites connues, les risques techniques, les biais de l’évaluation et ce que vous amélioreriez avec une journée supplémentaire.

# Licence et propriété

Indiquez la licence du dépôt et vérifiez que toutes les ressources externes sont compatibles avec cette licence.
