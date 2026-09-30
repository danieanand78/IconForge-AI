import { Link } from "@tanstack/react-router";
import { Sparkles } from "lucide-react";

import { brand } from "@/config/brand";

const items = [{ to: "/generer", label: "Générer une icône", icon: Sparkles }] as const;

export function AppSidebar() {
  return (
    <aside className="flex w-full shrink-0 flex-col gap-6 border-b border-border bg-sidebar px-4 py-5 lg:h-screen lg:w-72 lg:border-r lg:border-b-0 lg:sticky lg:top-0">
      <div className="flex min-w-0 items-center gap-3">
        <img
          src={brand.logoUrl}
          alt={`Logo ${brand.organisation}`}
          className="h-11 w-11 shrink-0 rounded-xl bg-background object-contain p-1"
        />
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold tracking-tight text-sidebar-foreground">
            {brand.name}
          </p>
          <p className="truncate text-xs text-muted-foreground">{brand.organisation}</p>
        </div>
      </div>

      <nav className="flex flex-wrap gap-1 lg:flex-col lg:flex-nowrap">
        {items.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className="group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground data-[status=active]:bg-primary/10 data-[status=active]:text-primary"
          >
            <item.icon className="h-4 w-4 shrink-0" />
            <span className="truncate">{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="mt-auto hidden rounded-xl border border-border bg-background p-4 lg:block">
        <p className="text-xs font-medium text-foreground">Backend FastAPI</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Données fictives actives. Branchement prévu via <code>apiConfig</code>.
        </p>
      </div>
    </aside>
  );
}
