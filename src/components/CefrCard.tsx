import type { CefrEstimate } from "@/lib/cefr";
import { GraduationCap } from "lucide-react";

export function CefrCard({ est }: { est: CefrEstimate }) {
  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-muted-foreground inline-flex items-center gap-1">
            <GraduationCap className="h-4 w-4" /> Twój szacowany poziom CEFR
          </p>
          <p className="text-4xl font-bold mt-1" style={{ color: "#000" }}>
            {est.level}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Wynik ogólny: {est.score}/100 · do {est.nextLevel}
          </p>
        </div>
      </div>
      <div className="mt-4 h-2 rounded-full bg-secondary overflow-hidden">
        <div
          className="h-full bg-primary transition-all"
          style={{ width: `${est.score}%` }}
        />
      </div>
      <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <Metric label="Quizy" value={`${est.quizAvg}%`} />
        <Metric label="Pokrycie" value={`${est.coverage}%`} />
        <Metric label="Znajomość" value={`${est.knownRatio}%`} />
        <Metric label="Jakość SRS" value={`${est.srsQuality}%`} />
      </div>
      <p className="mt-3 text-xs text-muted-foreground">
        <strong>Wskazówka:</strong> {est.suggestion}
      </p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-secondary/50 px-2 py-2 text-center">
      <p className="text-muted-foreground">{label}</p>
      <p className="font-bold mt-0.5" style={{ color: "#000" }}>
        {value}
      </p>
    </div>
  );
}
