/**
 * Données fictives (mock).
 * À remplacer par les appels FastAPI — voir src/config/brand.ts (apiConfig).
 */

export type Generation = {
  id: string;
  concept: string;
  date: string;
  score: number;
  modele: string;
  svg: string;
};

export const iconeSvg = (
  concept: string,
) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" stroke="#12B331" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
  <title>${concept}</title>
  <circle cx="32" cy="32" r="22" />
  <path d="M20 36c6-10 18-10 24 0" />
  <path d="M32 14v8M32 42v8" />
</svg>`;

export const generations: Generation[] = [
  {
    id: "gen_0192",
    concept: "Diplôme numérique",
    date: "26/08/2026 08:41",
    score: 96,
    modele: "gpt-5-mini",
    svg: iconeSvg("Diplôme numérique"),
  },
  {
    id: "gen_0191",
    concept: "Partenariat international",
    date: "26/08/2026 08:12",
    score: 92,
    modele: "gpt-5-mini",
    svg: iconeSvg("Partenariat international"),
  },
  {
    id: "gen_0190",
    concept: "Laboratoire de recherche",
    date: "25/08/2026 17:55",
    score: 88,
    modele: "claude-sonnet-4",
    svg: iconeSvg("Laboratoire de recherche"),
  },
  {
    id: "gen_0189",
    concept: "Bibliothèque en ligne",
    date: "25/08/2026 16:03",
    score: 94,
    modele: "gpt-5-mini",
    svg: iconeSvg("Bibliothèque en ligne"),
  },
  {
    id: "gen_0188",
    concept: "Réseau étudiant",
    date: "25/08/2026 11:20",
    score: 81,
    modele: "gemini-2.5-flash",
    svg: iconeSvg("Réseau étudiant"),
  },
  {
    id: "gen_0187",
    concept: "Certification qualité",
    date: "24/08/2026 09:47",
    score: 90,
    modele: "gpt-5-mini",
    svg: iconeSvg("Certification qualité"),
  },
];

export const systemStatus = [
  { label: "API FastAPI", valeur: "Simulée", ok: true },
  { label: "Modèle IA", valeur: "gpt-5-mini", ok: true },
  { label: "Validateur SVG", valeur: "Opérationnel", ok: true },
  { label: "Latence moyenne", valeur: "1,8 s", ok: true },
];

export const pipelineEtapes = [
  { nom: "Concept", detail: "Saisie utilisateur normalisée" },
  { nom: "Brand Reader", detail: "Lecture de la charte ISPM" },
  { nom: "SVG Analyzer", detail: "Analyse des références existantes" },
  { nom: "Prompt Builder", detail: "Construction du prompt contraint" },
  { nom: "LLM", detail: "Inférence du modèle sélectionné" },
  { nom: "Génération SVG", detail: "Sortie vectorielle brute" },
  { nom: "Validation", detail: "Contrôles XML, palette, stroke" },
  { nom: "Score", detail: "Note de conformité globale" },
];

export const specification = {
  geometrie: [
    "Grille 64 × 64 px, marge de sécurité 4 px",
    "Rayon de courbure constant : 2 px",
    "Alignement sur grille entière (pas de demi-pixel)",
    "Formes basées sur cercle, arc et lignes droites",
  ],
  traits: [
    "Épaisseur unique : 3 px",
    "Extrémités et jointures arrondies",
    "Pas de remplissage sauf aplat de marque",
    "Contraste minimum AA sur fond clair et foncé",
  ],
  style: [
    "Minimaliste, géométrique, institutionnel",
    "Maximum 3 couleurs par icône",
    "Métaphores académiques : savoir, échange, excellence",
    "Lisibilité garantie à 16 px",
  ],
  interdits: [
    "Dégradés multicolores hors palette",
    "Ombres portées et effets 3D",
    "Textes ou lettrages dans l'icône",
    "Images bitmap intégrées",
    "Traits d'épaisseurs mixtes",
  ],
  references: [
    { nom: "Logo ISPM", detail: "Globe, toque et poignée de main" },
    { nom: "Charte 2026", detail: "Document de référence interne v3.2" },
    { nom: "Set d'icônes noyau", detail: "24 icônes validées" },
  ],
};

export const validations = [
  { critere: "SVG valide", statut: "réussi", detail: "Balise <svg> conforme" },
  { critere: "XML valide", statut: "réussi", detail: "Arbre bien formé" },
  { critere: "ViewBox", statut: "réussi", detail: "0 0 64 64" },
  { critere: "Palette", statut: "réussi", detail: "Couleurs issues de la charte" },
  { critere: "Stroke", statut: "avertissement", detail: "3 px attendu, 2,8 px détecté" },
  { critere: "Nombre de couleurs", statut: "réussi", detail: "2 / 3 autorisées" },
];

export const modelesIA = [
  { id: "gpt-5-mini", nom: "GPT-5 Mini", detail: "Rapide, bon rapport qualité/coût" },
  { id: "claude-sonnet-4", nom: "Claude Sonnet 4", detail: "Meilleure rigueur géométrique" },
  { id: "gemini-2.5-flash", nom: "Gemini 2.5 Flash", detail: "Latence la plus faible" },
];
