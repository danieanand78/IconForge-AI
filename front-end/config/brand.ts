/**
 * Configuration centrale de la marque.
 * Modifier ce fichier suffit pour changer le logo, le nom et la palette.
 * Les couleurs sont définies en oklch dans src/styles.css (tokens sémantiques).
 */
export const brand = {
  name: "IconForge AI",
  organisation: "ISPM",
  baseline: "Génération d'icônes SVG guidée par la charte de marque",
  logoUrl: "/logo_ispm.png",
  /** Palette officielle (référence visuelle, source de vérité : src/styles.css) */
  palette: [
    { nom: "Vert ISPM", hex: "#12B331", usage: "Couleur primaire, accents, CTA" },
    { nom: "Vert profond", hex: "#0A6E20", usage: "Dégradés, états actifs" },
    { nom: "Vert clair", hex: "#7CE88F", usage: "Survols, indicateurs positifs" },
    { nom: "Noir graphite", hex: "#111413", usage: "Texte principal, aplats" },
    { nom: "Gris ardoise", hex: "#5B6660", usage: "Texte secondaire" },
    { nom: "Blanc cassé", hex: "#F7FAF8", usage: "Fonds, surfaces" },
  ],
} as const;

/** Configuration de l'API FastAPI (branchement futur) */
export const apiConfig = {
  baseUrl: import.meta.env["VITE_API_URL"] ?? "http://localhost:8000",
  endpoints: {
    generate: "/api/v1/generate",
    validate: "/api/v1/validate",
    history: "/api/v1/history",
    brand: "/api/v1/brand",
    health: "/api/v1/health",
  },
} as const;
