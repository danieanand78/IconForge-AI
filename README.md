# IconForge AI

## Description

Hackathon d’AI Engineering pour étudiants de niveau M2 disposant pour le Parcours IMTICIA (www.ispm-edu.com).

L’objectif est de construire un système capable de générer une **famille cohérente d’icônes SVG** à partir de concepts exprimés en langage naturel, en respectant une charte graphique imposée et lue à l’exécution.

La charte graphique est une adaptation pédagogique créée pour l’épreuve. Le challenge n’est affilié à aucune marque existante.

## Démarrage rapide

1. Lire `Sujet - Clinique IMTICIA.pdf` et faire lire `brand-guidelines.md` par le programme à l’exécution.
2. Faire analyser la collection du dossier `references/` sans la recopier ni figer ses valeurs dans le code.
3. Développer un système exposant le contrat décrit dans `benchmark/README.md` et résolvant la charte relativement à la racine du dépôt.
4. Générer les concepts de `benchmark/public-concepts.json`.
5. Installer Inkscape puis vérifier les SVG du profil public avec `python tools/validate_svg.py outputs/public/ --requests benchmark/public-concepts.json`.
6. Copier `readme-model.md` sous le nom `README.md` dans le dépôt de remise et le compléter. Le même canevas est également fourni dans `submission-template/README.md`.
7. Avant la remise, tester sans modifier le code une charte variante et un autre dossier de références placés aux mêmes emplacements.

## Génération SVG avec Gemini

L'adaptateur `generate.py` utilise `gemini-3.6-flash` via l'API Gemini lorsque
`GEMINI_API_KEY` est défini. Pour stocker la clé localement, copiez
`.env.example` vers `.env`, puis renseignez `.env` :

```bash
cp .env.example .env
```

```dotenv
GEMINI_API_KEY=votre-vraie-cle
GEMINI_MODEL=gemini-3.6-flash
```

`.env` est ignoré par Git et la clé n'est jamais écrite dans le code :

```bash
python generate.py \
	--input benchmark/public-concepts.json \
	--output outputs/public/
```

Le programme relit `brand-guidelines.md` et `references/` à chaque exécution,
construit le prompt à partir de la spécification extraite, puis valide chaque
SVG avec `tools/validate_svg.py`. Le modèle peut être changé avec
`GEMINI_MODEL` ou `--model`.

Si Gemini retourne un SVG techniquement invalide, les erreurs précises du
validateur sont réinjectées dans le prompt et le fichier est régénéré, avec un
maximum de trois tentatives par concept.

En cas d'indisponibilité temporaire de Gemini (`429`, `500` ou `503`), le
générateur effectue trois nouvelles tentatives avec un délai progressif. Si le
service reste indisponible, il utilise automatiquement le fallback local.

Sans clé API, un fallback local déterministe produit des SVG conformes aux
contraintes techniques afin de permettre l'exécution et les tests hors ligne.
Ce fallback est une solution de secours technique, pas une évaluation de la
fidélité sémantique du concept.

Dépendances Python :

```bash
pip install -r requirements.txt
```

## Lancer l'interface complète

Dans un premier terminal, démarrer l'API Python :

```bash
python3 api_server.py
```

Dans un second terminal, démarrer l'interface :

```bash
cd front-end
npm install
npm run dev
```

L'interface appelle `http://127.0.0.1:8000/api/v1/generate`. La clé Gemini
reste uniquement côté API, dans `.env`. Sans clé ou si Gemini est indisponible,
l'API utilise le fallback local déterministe.
