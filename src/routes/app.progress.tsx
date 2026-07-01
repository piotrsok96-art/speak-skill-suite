import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo } from "react";
import { useActiveProfile, useProfileData } from "@/lib/store";
import { BUILTIN_LESSONS } from "@/content/lessons";
import { estimateCefr } from "@/lib/cefr";
import { CefrCard } from "@/components/CefrCard";
import { StreakCalendar } from "@/components/StreakCalendar";
import { SkillRadar } from "@/components/SkillRadar";
import { QuizProgressChart } from "@/components/QuizProgressChart";
import { VoiceSettings } from "@/components/VoiceSettings";

export const Route = createFileRoute("/app/progress")({
  component: Progress,
});

function Stat({ label, value, sub }: { label: string; value: number | string; sub?: string }) {
  return (
    <div className="rounded-xl border bg-card p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-3xl mt-1 font-bold" style={{ color: "#000" }}>{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  );
}

function Progress() {
  const profile = useActiveProfile();
  const [data] = useProfileData(profile);
  const total = BUILTIN_LESSONS.length;

  const stats = useMemo(() => {
    let completed = 0, started = 0;
    let quizSum = 0, quizCnt = 0;
    let pretestSum = 0, pretestCnt = 0;
    let grammarSum = 0, grammarCnt = 0;
    for (const l of BUILTIN_LESSONS) {
      const p = data.lessonProgress[l.id];
      if (!p) continue;
      if (p.completedAt) completed++;
      else if (p.startedAt) started++;
      if (p.quizScore != null && p.quizTotal) {
        quizSum += p.quizScore / p.quizTotal;
        quizCnt++;
        // approximate grammar contribution: 5 grammar Qs of ~12
        grammarSum += p.quizScore / p.quizTotal;
        grammarCnt++;
      }
      if (p.pretestScore != null && p.pretestTotal) {
        pretestSum += p.pretestScore / p.pretestTotal;
        pretestCnt++;
      }
    }
    let known = 0, learning = 0;
    for (const v of Object.values(data.wordStatus)) {
      if (v === "known") known++;
      else if (v === "learning") learning++;
    }
    return {
      completed, started, known, learning,
      quizAvg: quizCnt ? Math.round((quizSum / quizCnt) * 100) : 0,
      preAvg: pretestCnt ? Math.round((pretestSum / pretestCnt) * 100) : 0,
      grammarAvg: grammarCnt ? Math.round((grammarSum / grammarCnt) * 100) : 0,
    };
  }, [data.lessonProgress, data.wordStatus]);

  const cefr = useMemo(() => estimateCefr(data), [data]);

  // Radar: 6 axes on 0-100 scale.
  const srsItems = Object.values(data.srs);
  const avgEase = srsItems.length
    ? srsItems.reduce((s, i) => s + i.ease, 0) / srsItems.length
    : 2.5;
  const srsQuality = Math.max(0, Math.min(100, ((avgEase - 1.3) / 1.5) * 100));
  const produceRatio = data.produceStats.total
    ? Math.round((data.produceStats.correct / data.produceStats.total) * 100)
    : 0;
  const coverage = Math.round((stats.completed / total) * 100);

  const radar = [
    { axis: "Słownictwo", value: Math.min(100, stats.known + Math.round(stats.learning / 2)) },
    { axis: "Gramatyka", value: stats.grammarAvg },
    { axis: "Quiz", value: stats.quizAvg },
    { axis: "Produkcja PL→EN", value: produceRatio },
    { axis: "Pokrycie lekcji", value: coverage },
    { axis: "Jakość SRS", value: Math.round(srsQuality) },
  ];

  const recent = useMemo(
    () =>
      BUILTIN_LESSONS
        .map((l) => ({ l, p: data.lessonProgress[l.id] }))
        .filter((x) => x.p?.completedAt || x.p?.startedAt)
        .sort((a, b) => (b.p?.completedAt ?? b.p?.startedAt ?? 0) - (a.p?.completedAt ?? a.p?.startedAt ?? 0))
        .slice(0, 10),
    [data.lessonProgress],
  );

  const pct = Math.round((stats.completed / total) * 100);

  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm text-muted-foreground capitalize">Profil: {profile}</p>
        <h1 className="text-3xl mt-1">Postępy</h1>
        <p className="text-sm text-muted-foreground mt-2">
          Bazuje na 50 wbudowanych lekcjach B1/B2.
        </p>
      </header>

      <CefrCard est={cefr} />

      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-baseline justify-between mb-2">
          <span className="text-sm text-muted-foreground">Ukończone lekcje</span>
          <span className="text-sm font-medium">{stats.completed} / {total} ({pct}%)</span>
        </div>
        <div className="h-2 rounded-full bg-secondary overflow-hidden">
          <div className="h-full bg-primary transition-all" style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label="W toku" value={stats.started} />
        <Stat label="Słówka znam" value={stats.known} />
        <Stat label="Uczę się" value={stats.learning} sub="w kolejce SRS" />
        <Stat label="Pre-test śr." value={`${stats.preAvg}%`} />
        <Stat label="Quiz śr." value={`${stats.quizAvg}%`} />
        <Stat label="PL→EN" value={`${produceRatio}%`} sub={`${data.produceStats.correct}/${data.produceStats.total}`} />
        <Stat label="Streak" value={`${data.streak.current} dni`} sub={`Rekord: ${data.streak.longest}`} />
        <Stat label="Dziś" value={`${data.streak.todayCount}/${data.streak.dailyGoal}`} sub="cel dzienny" />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <StreakCalendar streak={data.streak} />
        <SkillRadar data={radar} />
      </div>

      <QuizProgressChart results={data.results ?? []} />

      <VoiceSettings />

      <section>
        <h2 className="text-xl mb-3">Ostatnio otwierane lekcje</h2>
        {recent.length === 0 ? (
          <p className="text-muted-foreground">Nie rozpoczęto żadnej lekcji. <Link to="/app/lessons" className="underline">Otwórz listę →</Link></p>
        ) : (
          <ul className="space-y-2">
            {recent.map(({ l, p }) => (
              <li key={l.id} className="rounded-lg border bg-card p-3 flex justify-between items-center gap-3 text-sm">
                <Link to="/app/lessons/$id" params={{ id: l.id }} className="font-semibold hover:underline truncate">
                  {l.topic}
                </Link>
                <span className="text-muted-foreground shrink-0">
                  {l.level} ·{" "}
                  {p?.completedAt
                    ? `✓ ${new Date(p.completedAt).toLocaleDateString()}`
                    : `w toku`}
                  {p?.quizScore != null && ` · quiz ${p.quizScore}/${p.quizTotal}`}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
