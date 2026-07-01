import { Link } from "@tanstack/react-router";
import type { Insights } from "@/lib/insights";
import { AlertTriangle, BookOpen, Target } from "lucide-react";

export function InsightsPanel({ insights }: { insights: Insights }) {
  const { weakGrammar, hardWords, recommendedLesson, weakItemsForSrs } = insights;
  if (!weakGrammar && hardWords.length === 0 && !recommendedLesson) {
    return null;
  }
  return (
    <div className="space-y-3">
      <h2 className="text-xl">Rekomendacje na dziś</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        {weakGrammar && (
          <Link
            to="/app/lessons/$id"
            params={{ id: weakGrammar.lesson.id }}
            className="rounded-xl border bg-card p-4 hover:border-foreground/30 transition-colors block"
          >
            <div className="flex items-center gap-2 text-amber-600 text-xs font-medium">
              <AlertTriangle className="h-4 w-4" /> Słaba strona
            </div>
            <p className="mt-1 font-semibold" style={{ color: "#000" }}>
              {weakGrammar.topic}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Twój wynik: {Math.round(weakGrammar.avg * 100)}%. Powtórz lekcję „{weakGrammar.lesson.topic}".
            </p>
          </Link>
        )}
        {recommendedLesson && (
          <Link
            to="/app/lessons/$id"
            params={{ id: recommendedLesson.id }}
            className="rounded-xl border bg-card p-4 hover:border-foreground/30 transition-colors block"
          >
            <div className="flex items-center gap-2 text-blue-600 text-xs font-medium">
              <BookOpen className="h-4 w-4" /> Polecana lekcja
            </div>
            <p className="mt-1 font-semibold" style={{ color: "#000" }}>
              {recommendedLesson.topic}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Poziom {recommendedLesson.level} · {recommendedLesson.grammar.title}
            </p>
          </Link>
        )}
        {weakItemsForSrs.length >= 4 && (
          <Link
            to="/app/srs"
            search={{ mode: "weak" }}
            className="rounded-xl border bg-card p-4 hover:border-foreground/30 transition-colors block"
          >
            <div className="flex items-center gap-2 text-red-600 text-xs font-medium">
              <Target className="h-4 w-4" /> Tryb słabych punktów
            </div>
            <p className="mt-1 font-semibold" style={{ color: "#000" }}>
              {weakItemsForSrs.length} trudnych słówek
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Sesja SRS ograniczona do najsłabszych fiszek.
            </p>
          </Link>
        )}
      </div>
      {hardWords.length > 0 && (
        <div className="rounded-xl border bg-card p-4">
          <p className="text-xs font-medium text-muted-foreground mb-2">
            Słówka do dopracowania
          </p>
          <div className="flex flex-wrap gap-2">
            {hardWords.map((w) => (
              <span
                key={w.key}
                className="text-xs px-2 py-1 rounded-md bg-secondary"
                title={`ease: ${w.ease.toFixed(2)}`}
              >
                <strong style={{ color: "#000" }}>{w.en}</strong>
                <span className="text-muted-foreground"> — {w.pl}</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
