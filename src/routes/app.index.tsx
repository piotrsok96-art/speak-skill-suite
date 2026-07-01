import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo } from "react";
import { useActiveProfile, useProfileData } from "@/lib/store";
import { BUILTIN_LESSONS } from "@/content/lessons";
import { estimateCefr } from "@/lib/cefr";
import { computeInsights } from "@/lib/insights";
import { dueToday } from "@/lib/srs";
import { CefrCard } from "@/components/CefrCard";
import { InsightsPanel } from "@/components/InsightsPanel";
import { Button } from "@/components/ui/button";
import { ArrowRight, Flame, Repeat2, Target } from "lucide-react";

export const Route = createFileRoute("/app/")({
  component: Dashboard,
});

function Dashboard() {
  const profile = useActiveProfile();
  const [data] = useProfileData(profile);
  const cefr = useMemo(() => estimateCefr(data), [data]);
  const insights = useMemo(() => computeInsights(data), [data]);
  const dueCount = useMemo(() => dueToday(data.srs).length, [data.srs]);

  const nextLesson =
    BUILTIN_LESSONS.find(
      (l) => !data.lessonProgress[l.id]?.completedAt,
    ) ?? BUILTIN_LESSONS[0];

  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm text-muted-foreground capitalize">Cześć, {profile} 👋</p>
        <h1 className="text-3xl md:text-4xl mt-1">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-2">
          Twój przegląd nauki, poziom CEFR i rekomendacje na dziś.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border bg-card p-4 flex items-start gap-3">
          <Flame className="h-5 w-5 text-orange-500 mt-0.5" />
          <div>
            <p className="text-xs text-muted-foreground">Streak</p>
            <p className="text-2xl font-bold" style={{ color: "#000" }}>
              {data.streak.current} dni
            </p>
            <p className="text-xs text-muted-foreground">
              Dziś: {data.streak.todayCount}/{data.streak.dailyGoal}
            </p>
          </div>
        </div>
        <div className="rounded-xl border bg-card p-4 flex items-start gap-3">
          <Repeat2 className="h-5 w-5 text-blue-500 mt-0.5" />
          <div className="flex-1">
            <p className="text-xs text-muted-foreground">Do powtórzenia dziś</p>
            <p className="text-2xl font-bold" style={{ color: "#000" }}>
              {dueCount}
            </p>
            <Link to="/app/srs" className="text-xs text-primary underline">
              Otwórz powtórki →
            </Link>
          </div>
        </div>
        <div className="rounded-xl border bg-card p-4 flex items-start gap-3">
          <Target className="h-5 w-5 text-green-600 mt-0.5" />
          <div className="flex-1">
            <p className="text-xs text-muted-foreground">Kolejna lekcja</p>
            <p className="text-sm font-semibold truncate" style={{ color: "#000" }}>
              {nextLesson.topic}
            </p>
            <Link
              to="/app/lessons/$id"
              params={{ id: nextLesson.id }}
              className="text-xs text-primary underline inline-flex items-center gap-1"
            >
              Start <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        </div>
      </div>

      <CefrCard est={cefr} />

      <InsightsPanel insights={insights} />

      <div className="flex flex-wrap gap-2">
        <Button asChild variant="outline">
          <Link to="/app/progress">Zobacz szczegółowe postępy</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/app/lessons">Wszystkie lekcje</Link>
        </Button>
      </div>
    </div>
  );
}
