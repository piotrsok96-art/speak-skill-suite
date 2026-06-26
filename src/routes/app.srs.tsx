import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData, type SrsItem } from "@/lib/store";
import { SpeakButton } from "@/components/SpeakButton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { dueToday, reviewItem } from "@/lib/srs";
import { withStreakBump } from "@/lib/streak";
import { cn } from "@/lib/utils";
import { Check, CheckCircle2, Eye, EyeOff, Repeat2, Trophy, X } from "lucide-react";

export const Route = createFileRoute("/app/srs")({
  component: SrsPage,
});

const GRADES = [
  { label: "Nie pamiętam", grade: 0 as const, className: "bg-red-500 hover:bg-red-600 text-white" },
  { label: "Trudne", grade: 1 as const, className: "bg-amber-500 hover:bg-amber-600 text-white" },
  { label: "OK", grade: 2 as const, className: "bg-blue-600 hover:bg-blue-700 text-white" },
  { label: "Łatwe", grade: 3 as const, className: "bg-green-600 hover:bg-green-700 text-white" },
];

type Mode = "flash" | "choice" | "type";

function modeFor(key: string, count: number): Mode {
  // Deterministic per-card mode based on session count + key hash.
  let h = 0;
  for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) | 0;
  const v = (Math.abs(h) + count) % 3;
  return v === 0 ? "flash" : v === 1 ? "choice" : "type";
}

function normalize(s: string) {
  return s.trim().toLowerCase().replace(/[.,!?]/g, "");
}

function makeChoices(current: SrsItem, pool: SrsItem[]): string[] {
  const set = new Set<string>([current.pl]);
  // shuffle-ish via hashed sort
  const others = pool
    .filter((p) => p.key !== current.key && p.pl && p.pl !== current.pl)
    .sort((a, b) => (a.key < b.key ? -1 : 1));
  for (const o of others) {
    if (set.size >= 4) break;
    set.add(o.pl);
  }
  while (set.size < 4) set.add("—");
  const arr = Array.from(set);
  // deterministic shuffle
  let h = 0;
  for (let i = 0; i < current.key.length; i++) h = (h * 31 + current.key.charCodeAt(i)) | 0;
  for (let i = arr.length - 1; i > 0; i--) {
    h = (h * 9301 + 49297) | 0;
    const j = Math.abs(h) % (i + 1);
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function SrsPage() {
  const profile = useActiveProfile();
  const [data, update] = useProfileData(profile);
  const [reveal, setReveal] = useState(false);
  const [done, setDone] = useState(0);
  const [typed, setTyped] = useState("");
  const [picked, setPicked] = useState<number | null>(null);
  const [typeChecked, setTypeChecked] = useState(false);

  const queue = useMemo(() => dueToday(data.srs), [data.srs]);
  const pool = useMemo(() => Object.values(data.srs), [data.srs]);
  const current = queue[0];
  const mode: Mode = current ? modeFor(current.key, done) : "flash";
  const choices = useMemo(
    () => (current && mode === "choice" ? makeChoices(current, pool) : []),
    [current, mode, pool],
  );

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

  const resetCard = () => {
    setReveal(false); setTyped(""); setPicked(null); setTypeChecked(false);
  };

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
    resetCard();
    setDone((n) => n + 1);
  };

  const modeBadge =
    mode === "flash" ? "Fiszka" : mode === "choice" ? "Wybierz znaczenie" : "Wpisz PL";

  return (
    <div className="space-y-5">
      <header>
        <p className="text-sm text-muted-foreground">Powtórki SRS · tryb mieszany</p>
        <h1 className="text-3xl md:text-4xl mt-1">Powtórka dnia</h1>
        <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2 flex-wrap">
          <span className="inline-flex items-center gap-1">
            <Repeat2 className="h-4 w-4" /> Pozostało: {queue.length}
          </span>
          {done > 0 && (
            <span className="inline-flex items-center gap-1 text-green-600">
              <CheckCircle2 className="h-4 w-4" /> Powtórzone: {done}
            </span>
          )}
          <span className="px-2 py-0.5 rounded-full bg-secondary text-xs font-medium">
            {modeBadge}
          </span>
        </div>
      </header>

      <div className="rounded-xl border-2 bg-card p-6 md:p-8 min-h-[300px] flex flex-col">
        {/* HEAD: always EN word */}
        <div className="text-center">
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
        </div>

        {/* BODY: mode-specific */}
        <div className="mt-6 flex-1 flex flex-col justify-center">
          {mode === "flash" && (
            reveal ? (
              <div className="text-center space-y-2 animate-in fade-in">
                <p className="text-xl font-semibold" style={{ color: "#000" }}>{current.pl}</p>
                {current.plPron && <p className="text-sm text-muted-foreground">({current.plPron})</p>}
                {current.example && (
                  <p className="text-sm italic text-muted-foreground mt-2">{current.example}</p>
                )}
              </div>
            ) : (
              <Button variant="outline" className="mx-auto" onClick={() => setReveal(true)}>
                <Eye className="h-4 w-4" /> Pokaż tłumaczenie
              </Button>
            )
          )}

          {mode === "choice" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {choices.map((opt, i) => {
                const isPicked = picked === i;
                const correctIdx = choices.indexOf(current.pl);
                const showCorrect = picked != null && i === correctIdx;
                const showWrong = isPicked && i !== correctIdx;
                return (
                  <button
                    key={i}
                    disabled={picked != null}
                    onClick={() => { setPicked(i); setReveal(true); }}
                    className={cn(
                      "rounded-lg border px-3 py-3 text-left text-sm transition-colors",
                      picked == null && "hover:bg-secondary",
                      showCorrect && "border-green-500 bg-green-500/10 text-green-700",
                      showWrong && "border-red-500 bg-red-500/10 text-red-700",
                      picked != null && !showCorrect && !showWrong && "opacity-60",
                    )}
                  >
                    <span className="inline-flex items-center gap-2">
                      {showCorrect && <Check className="h-4 w-4" />}
                      {showWrong && <X className="h-4 w-4" />}
                      {opt}
                    </span>
                  </button>
                );
              })}
              {reveal && current.example && (
                <p className="sm:col-span-2 text-xs italic text-muted-foreground mt-2 text-center">
                  {current.example}
                </p>
              )}
            </div>
          )}

          {mode === "type" && (
            <div className="space-y-3 max-w-md mx-auto w-full">
              <p className="text-xs uppercase tracking-wide text-muted-foreground text-center">
                Wpisz polskie tłumaczenie:
              </p>
              <Input
                value={typed}
                onChange={(e) => setTyped(e.target.value)}
                disabled={typeChecked}
                placeholder="np. spotkanie"
                onKeyDown={(e) => { if (e.key === "Enter" && !typeChecked) { setTypeChecked(true); setReveal(true); } }}
              />
              {!typeChecked ? (
                <Button
                  className="w-full"
                  onClick={() => { setTypeChecked(true); setReveal(true); }}
                  disabled={!typed.trim()}
                >
                  <Check className="h-4 w-4" /> Sprawdź
                </Button>
              ) : (
                <div className={cn(
                  "rounded-md p-3 text-sm text-center",
                  normalize(typed) === normalize(current.pl)
                    ? "bg-green-500/10 text-green-700"
                    : "bg-red-500/10 text-red-700",
                )}>
                  <p className="font-semibold">
                    {normalize(typed) === normalize(current.pl) ? "Dobrze!" : `Poprawnie: ${current.pl}`}
                  </p>
                  {current.example && (
                    <p className="italic text-muted-foreground mt-1">{current.example}</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
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

      {!reveal && mode === "flash" && (
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
