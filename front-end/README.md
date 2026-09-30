# Icon Forge AI Studio

Je souhaite créer une application web Frontend nommée **IconForge AI**.

Le projet est réalisé dans le cadre d'un Hackathon d'AI Engineering.

Important :

- Génère un projet complet exportable et modifiable en local.

- Utilise React + TypeScript + Vite + Tailwind CSS.

- Le projet doit fonctionner avec `npm install` puis `npm run dev`.

- Le code doit être propre, organisé et facilement maintenable.

- Toute l'interface doit être en **français**.

- Le backend sera développé plus tard avec FastAPI, donc utilise uniquement des données fictives (mock).

J'ai déjà :

- un logo (logo_ispm.png)

- une palette de couleurs officielle (en reference avec le logo_ispm.png)

Prévois une structure permettant de modifier facilement le logo et les couleurs.

Le design doit être moderne, élégant, minimaliste, professionnel et responsive, avec une expérience utilisateur digne d'une plateforme d'IA.

L'application doit contenir :

• Une barre latérale avec :

- Tableau de bord

- Générer une icône

- Spécification de la marque

- Validation

- Historique

- Paramètres

Le tableau de bord doit afficher :

- l'état du système

- le nombre d'icônes générées

- les dernières générations

La page "Générer une icône" doit contenir :

- un champ pour saisir un concept

- un bouton "Générer"

- un aperçu SVG

- les boutons Télécharger, Copier et Ouvrir

- un score de génération

La page "Spécification de la marque" doit afficher :

- Palette

- Géométrie

- Traits

- Style

- Éléments interdits

- Références

La page "Validation" doit afficher les vérifications :

- SVG valide

- XML valide

- ViewBox

- Palette

- Stroke

- Nombre de couleurs

- Score global

La page "Historique" doit afficher les générations précédentes.

La page "Paramètres" doit permettre de sélectionner le modèle IA, de changer le thème et de configurer l'API. 

Ajoute également une visualisation du pipeline IA :

Concept → Brand Reader → SVG Analyzer → Prompt Builder → LLM → Génération SVG → Validation → Score.

Je veux une interface très professionnelle, moderne et facilement connectable à une API FastAPI.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/d126fe5f-7cc8-4f46-a19f-5b67e8ec0d5c).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
