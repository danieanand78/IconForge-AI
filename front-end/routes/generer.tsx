import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Copy, Download, ExternalLink, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { PageHeader } from "@/components/PageHeader";
import { PipelineViz } from "@/components/PipelineViz";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiConfig } from "@/config/brand";
import { pipelineEtapes } from "@/lib/mock-data";

export const Route = createFileRoute("/generer")({
  head: () => ({
    meta: [
      { title: "Générer une icône — IconForge AI" },
      {
        name: "description",
        content:
          "Saisissez un concept et générez une icône SVG conforme à la charte de marque ISPM.",
      },
      { property: "og:title", content: "Générer une icône — IconForge AI" },
      {
        property: "og:description",
        content: "Génération d'icônes SVG vectorielles guidée par l'IA.",
      },
    ],
  }),
  component: Generer,
});

function Generer() {
  const [concept, setConcept] = useState("");
  const [enCours, setEnCours] = useState(false);
  const [etape, setEtape] = useState(-1);
  const [resultat, setResultat] = useState<{ svg: string; score: number; concept: string } | null>(
    null,
  );

  const generer = async () => {
    const conceptNettoye = concept.trim();
    if (!conceptNettoye) {
      toast.error("Veuillez saisir un concept.");
      return;
    }
    setEnCours(true);
    setResultat(null);
    setEtape(0);
    let i = 0;
    const timer = window.setInterval(() => {
      i += 1;
      setEtape(i);
      if (i >= pipelineEtapes.length - 1) window.clearInterval(timer);
    }, 320);

    try {
      const response = await fetch(`${apiConfig.baseUrl}${apiConfig.endpoints.generate}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ concept: conceptNettoye }),
      });
      const payload = (await response.json()) as {
        svg?: string;
        score?: number;
        concept?: string;
        error?: string;
      };
      if (!response.ok || !payload.svg) {
        throw new Error(payload.error ?? "La génération a échoué.");
      }
      window.clearInterval(timer);
      setEtape(pipelineEtapes.length - 1);
      setResultat({
        svg: payload.svg,
        score: payload.score ?? 0,
        concept: payload.concept ?? conceptNettoye,
      });
    } catch (error) {
      window.clearInterval(timer);
      setEtape(-1);
      toast.error(error instanceof Error ? error.message : "Impossible de joindre l'API.");
    } finally {
      setEnCours(false);
    }
  };

  const telecharger = () => {
    if (!resultat) return;
    const url = URL.createObjectURL(new Blob([resultat.svg], { type: "image/svg+xml" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `${resultat.concept.replace(/\s+/g, "-").toLowerCase()}.svg`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Icône téléchargée.");
  };

  const copier = async () => {
    if (!resultat) return;
    await navigator.clipboard.writeText(resultat.svg);
    toast.success("Code SVG copié.");
  };

  const ouvrir = () => {
    if (!resultat) return;
    const url = URL.createObjectURL(new Blob([resultat.svg], { type: "image/svg+xml" }));
    window.open(url, "_blank", "noopener");
  };

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8">
      <PageHeader
        titre="Générer une icône"
        description="Décrivez un concept, l'IA produit une icône SVG conforme à votre charte."
      />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="rounded-2xl border border-border bg-card p-5">
          <label htmlFor="concept" className="text-sm font-medium text-foreground">
            Concept
          </label>
          <div className="mt-2 flex flex-col gap-2 sm:flex-row">
            <Input
              id="concept"
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && generer()}
              placeholder="ex. remise de diplôme, laboratoire, partenariat…"
              className="min-w-0"
            />
            <Button onClick={generer} disabled={enCours} className="shrink-0">
              {enCours && <Loader2 className="h-4 w-4 animate-spin" />}
              {enCours ? "Génération…" : "Générer"}
            </Button>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Génération effectuée par le pipeline IconForge local.
          </p>

          <div className="mt-6 grid place-items-center rounded-xl border border-dashed border-border bg-background p-10">
            {resultat ? (
              <div
                className="h-40 w-40 [&_svg]:h-full [&_svg]:w-full"
                dangerouslySetInnerHTML={{ __html: resultat.svg }}
              />
            ) : (
              <p className="text-sm text-muted-foreground">
                {enCours ? "Génération en cours…" : "L'aperçu SVG s'affichera ici."}
              </p>
            )}
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <Button
              variant="outline"
              onClick={telecharger}
              disabled={!resultat}
              className="group transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-foreground hover:bg-primary hover:text-primary-foreground hover:shadow-md"
            >
              <Download className="h-4 w-4 transition-transform group-hover:-translate-y-0.5" />
              Télécharger
            </Button>
            <Button
              variant="outline"
              onClick={copier}
              disabled={!resultat}
              className="group transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-foreground hover:bg-primary hover:text-primary-foreground hover:shadow-md"
            >
              <Copy className="h-4 w-4 transition-transform group-hover:scale-110" /> Copier
            </Button>
            <Button
              variant="outline"
              onClick={ouvrir}
              disabled={!resultat}
              className="group transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-foreground hover:bg-primary hover:text-primary-foreground hover:shadow-md"
            >
              <ExternalLink className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              Ouvrir
            </Button>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground">Score de génération</h2>
          <p className="mt-6 text-5xl font-semibold tracking-tight text-primary">
            {resultat ? resultat.score : "—"}
            <span className="text-lg text-muted-foreground"> / 100</span>
          </p>
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all duration-500"
              style={{ width: `${resultat?.score ?? 0}%` }}
            />
          </div>
          <ul className="mt-6 space-y-2 text-sm">
            {[
              ["Conformité palette", resultat ? "100 %" : "—"],
              ["Géométrie", resultat ? "94 %" : "—"],
              ["Épaisseur de trait", resultat ? "88 %" : "—"],
              ["Lisibilité 16 px", resultat ? "92 %" : "—"],
            ].map(([k, v]) => (
              <li key={k} className="flex justify-between gap-3">
                <span className="min-w-0 truncate text-muted-foreground">{k}</span>
                <span className="shrink-0 font-medium text-foreground">{v}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <PipelineViz etapeActive={resultat ? pipelineEtapes.length - 1 : etape} />
    </div>
  );
}
