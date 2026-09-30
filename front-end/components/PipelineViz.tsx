import { ChevronDown, ChevronRight } from "lucide-react";

import { pipelineEtapes } from "@/lib/mock-data";

export function PipelineViz({ etapeActive = -1 }: { etapeActive?: number }) {
  return (
    <section className="rounded-2xl border border-border bg-card p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-sm font-semibold text-foreground">Pipeline IA</h2>
        <p className="text-xs text-muted-foreground">
          Concept → Brand Reader → SVG Analyzer → Prompt Builder → LLM → SVG → Validation → Score
        </p>
      </div>

      <ol className="mt-4 flex flex-col gap-3 lg:flex-row lg:items-stretch lg:overflow-x-auto lg:pb-2">
        {pipelineEtapes.map((etape, i) => {
          const fait = etapeActive >= i && etapeActive >= 0;
          const courant = etapeActive === i;
          return (
            <li
              key={etape.nom}
              className="flex min-w-0 flex-1 flex-col items-stretch gap-2 lg:flex-row lg:items-center lg:min-w-[11rem]"
            >
              <div
                className={[
                  "min-w-0 rounded-xl border p-3 transition-colors",
                  courant
                    ? "border-primary bg-primary/10"
                    : fait
                      ? "border-primary/40 bg-primary/5"
                      : "border-border bg-background",
                ].join(" ")}
              >
                <p className="flex items-center gap-2 text-xs font-semibold text-foreground">
                  <span
                    className={[
                      "grid h-5 w-5 shrink-0 place-items-center rounded-full text-[10px]",
                      fait
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground",
                    ].join(" ")}
                  >
                    {i + 1}
                  </span>
                  <span className="break-words">{etape.nom}</span>
                </p>
                <p className="mt-1 break-words text-[11px] text-muted-foreground">{etape.detail}</p>
              </div>
              {i < pipelineEtapes.length - 1 && (
                <>
                  <ChevronDown
                    aria-hidden="true"
                    className="mx-auto h-4 w-4 shrink-0 text-muted-foreground lg:hidden"
                  />
                  <ChevronRight
                    aria-hidden="true"
                    className="hidden h-4 w-4 shrink-0 text-muted-foreground lg:block"
                  />
                </>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
