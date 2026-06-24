import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData } from "@/lib/store";
import { SpeakButton } from "@/components/SpeakButton";
import { Button } from "@/components/ui/button";
import { dueToday, reviewItem } from "@/lib/srs";
import { withStreakBump } from "@/lib/streak";
import { cn } from "@/lib/utils";
import { CheckCircle2, Eye, EyeOff, Repeat2, Trophy } from "lucide-react";

export const Route = createFileRoute("/app/srs")({
  component: SrsPage,
});

const GRADES = [
  { label: "Nie pamiętam", grade: 0 as const, className: "bg-red-500 hover:bg-red-600 text-white" },
  { label: "Trudne", grade: 1 as const, className: "bg-amber-500 hover:bg-amber-600 text-white" },
  { label: "OK", grade: 2 as const, className: "bg-blue-600 hover:bg-blue-700 text-white" },
  { label: "Łatwe", grade: 3 as const, className: "bg-green-600 hover:bg-green-700 text-white" },
];

function SrsPage() {
  const profile = useActiveProfile();
  const [data, update] = useProfileData(profile);
  const [reveal, setReveal] = useState(false);
  const [done, setDone] = useState(0);

  const queue = useMemo(() => dueToday(data.srs), [data.srs]);
  const current = queue[0];

  if (!profile) return null;

  if (!current) {
    return (
      <div className="space-y-6">
        <header>
          <p className="text-sm text-muted-foreground">Powtórki</p>
          <h1 className="text-3xl md:text-4xl mt-1">Powtórka dnia</h1>
        </header>
        <div className="rounded-xl border bg-card p-8 text-center space-y-3">
          <Trophy className="h-10 w-10 mx-auto text-amber-500" />
          <p className="text-lg font-medium" style={{ color: "#000" }}>
            Brak słówek do powtórki dziś!
          </p>
          <p className="text-sm text-muted-foreground">
            Zaznacz „Nie znam" przy nowych słówkach w lekcjach, aby trafiły do kolejki SRS.
          </p>
          <Link
            to="/app/lessons"
            className="inline-flex items-center text-sm text-foreground underline mt-2"
          >
            Przejdź do lekcji →
          </Link>
        </div>
        {done > 0 && (
          <p className="text-center text-sm text-muted-foreground">
            Sesja zakończona: {done} powtórek.
          </p>
        )}
      </div>
    );
  }

  const grade = (g: 0 | 1 | 2 | 3) => {
    update((d) => {
      const item = d.srs[current.key];
      if (!item) return d;
      const next = reviewItem(item, g);
      return withStreakBump(
        { ...d, srs: { ...d.srs, [current.key]: next } },
        1,
      );
    });
    setReveal(false);
    setDone((n) => n + 1);
  };

  return (
    <div className="space-y-5">
      <header>
        <p className="text-sm text-muted-foreground">Powtórki SRS</p>
        <h1 className="text-3xl md:text-4xl mt-1">Powtórka dnia</h1>
        <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
          <span className="inline-flex items-center gap-1">
            <Repeat2 className="h-4 w-4" /> Pozostało: {queue.length}
          </span>
          {done > 0 && (
            <span className="inline-flex items-center gap-1 text-green-600">
              <CheckCircle2 className="h-4 w-4" /> Powtórzone: {done}
            </span>
          )}
        </div>
      </header>

      <div className="rounded-xl border-2 bg-card p-6 md:p-8 text-center min-h-[300px] flex flex-col justify-center">
        <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">EN</p>
        <div className="flex items-center justify-center gap-2">
          <SpeakButton text={current.en} size={20} />
          <p className="text-3xl md:text-4xl font-bold" style={{ color: "#000" }}>
            {current.en}
          </p>
        </div>
        {current.ipa && (
          <p className="text-sm text-muted-foreground font-mono mt-1">[{current.ipa}]</p>
        )}

        {reveal ? (
          <div className="mt-6 space-y-2 animate-in fade-in">
            <p className="text-xl font-semibold" style={{ color: "#000" }}>
              {current.pl}
            </p>
            {current.plPron && (
              <p className="text-sm text-muted-foreground">({current.plPron})</p>
            )}
            {current.example && (
              <p className="text-sm italic text-muted-foreground mt-2">{current.example}</p>
            )}
          </div>
        ) : (
          <Button variant="outline" className="mx-auto mt-6" onClick={() => setReveal(true)}>
            <Eye className="h-4 w-4" /> Pokaż tłumaczenie
          </Button>
        )}
      </div>

      {reveal && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {GRADES.map((g) => (
            <Button
              key={g.grade}
              onClick={() => grade(g.grade)}
              className={cn("h-auto py-3", g.className)}
            >
              {g.label}
            </Button>
          ))}
        </div>
      )}

      {!reveal && (
        <button
          onClick={() => setReveal(false)}
          className="w-full text-xs text-muted-foreground inline-flex items-center justify-center gap-1"
        >
          <EyeOff className="h-3 w-3" /> Najpierw spróbuj sobie przypomnieć
        </button>
      )}
    </div>
  );
}
