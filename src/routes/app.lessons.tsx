import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData } from "@/lib/store";
import { BUILTIN_LESSONS } from "@/content/lessons";
import { BookOpen, CheckCircle2, Circle, PlayCircle, Search } from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/lessons")({
  component: LessonsList,
});

function LessonsList() {
  const profile = useActiveProfile();
  const [data] = useProfileData(profile);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState<"all" | "B1" | "B2">("all");
  const [status, setStatus] = useState<"all" | "new" | "in-progress" | "done">("all");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return BUILTIN_LESSONS.filter((l) => {
      if (level !== "all" && l.level !== level) return false;
      const p = data.lessonProgress[l.id];
      const lessonStatus = p?.completedAt ? "done" : p?.startedAt ? "in-progress" : "new";
      if (status !== "all" && lessonStatus !== status) return false;
      if (q && !l.topic.toLowerCase().includes(q) && !l.summary.toLowerCase().includes(q))
        return false;
      return true;
    });
  }, [data.lessonProgress, query, level, status]);

  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm text-muted-foreground">Biblioteka</p>
        <h1 className="text-3xl md:text-4xl mt-1">50 lekcji B1 / B2</h1>
        <p className="text-sm text-muted-foreground mt-2">
          Życie codzienne i praca. Każda lekcja: 25 słówek, 5 idiomów, 2 dialogi, gramatyka, quiz.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Szukaj tematu…"
            className="w-full pl-9 pr-3 py-2 rounded-lg border bg-card text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value as "all" | "B1" | "B2")}
          className="rounded-lg border bg-card px-3 py-2 text-sm"
        >
          <option value="all">Wszystkie poziomy</option>
          <option value="B1">B1</option>
          <option value="B2">B2</option>
        </select>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as "all" | "new" | "in-progress" | "done")}
          className="rounded-lg border bg-card px-3 py-2 text-sm"
        >
          <option value="all">Wszystkie statusy</option>
          <option value="new">Nowa</option>
          <option value="in-progress">W toku</option>
          <option value="done">Ukończona</option>
        </select>
      </div>

      <div className="grid sm:grid-cols-2 gap-3">
        {filtered.map((l) => {
          const p = data.lessonProgress[l.id];
          const done = !!p?.completedAt;
          const started = !!p?.startedAt;
          return (
            <Link
              key={l.id}
              to="/app/lessons/$id"
              params={{ id: l.id }}
              className={cn(
                "block rounded-xl border bg-card p-4 hover:border-foreground/40 transition-colors",
                done && "border-green-500/40",
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span className="rounded bg-secondary px-1.5 py-0.5 font-mono">{l.level}</span>
                    <span>Lekcja {l.number}/50</span>
                  </div>
                  <h3 className="text-base font-semibold mt-1.5" style={{ color: "#000" }}>
                    {l.topic}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{l.summary}</p>
                </div>
                {done ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600 shrink-0" />
                ) : started ? (
                  <PlayCircle className="h-5 w-5 text-amber-500 shrink-0" />
                ) : (
                  <Circle className="h-5 w-5 text-muted-foreground shrink-0" />
                )}
              </div>
              {p?.quizScore != null && (
                <p className="text-xs text-muted-foreground mt-2">
                  Quiz: {p.quizScore}/{p.quizTotal}
                </p>
              )}
            </Link>
          );
        })}
        {filtered.length === 0 && (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            <BookOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Brak lekcji pasujących do filtrów.
          </div>
        )}
      </div>
    </div>
  );
}
