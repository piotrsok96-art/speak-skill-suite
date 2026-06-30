import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData, uid } from "@/lib/store";
import { BUILTIN_LESSONS, type BuiltinVocab } from "@/content/lessons";
import { QuizCard, type QuizQuestion } from "@/components/QuizCard";
import { Button } from "@/components/ui/button";
import { Printer, RefreshCw } from "lucide-react";

export const Route = createFileRoute("/app/vocab-review")({
  component: VocabReview,
});

function shuffle<T>(arr: T[]): T[] {
  return [...arr].sort(() => Math.random() - 0.5);
}

// Unique vocab from all 50 built-in lessons (en is the key).
function allBuiltinVocab(): (BuiltinVocab & { lessonTopic: string })[] {
  const map = new Map<string, BuiltinVocab & { lessonTopic: string }>();
  for (const l of BUILTIN_LESSONS) {
    for (const v of [...l.vocab, ...l.extraVocab]) {
      const k = v.en.toLowerCase();
      if (!map.has(k)) map.set(k, { ...v, lessonTopic: l.topic });
    }
  }
  return Array.from(map.values());
}

function openPrintWindow(title: string, bodyHtml: string) {
  const w = window.open("", "_blank", "width=900,height=900");
  if (!w) return;
  w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${title}</title>
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding:24px;color:#111}
      h1{font-size:22px;margin:0 0 16px}
      table{width:100%;border-collapse:collapse;font-size:12px}
      th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}
      th{background:#f5f5f5}
      tr:nth-child(even){background:#fafafa}
      @media print { button{display:none} }
    </style></head><body>
    <button onclick="window.print()" style="margin-bottom:12px;padding:6px 12px">Drukuj</button>
    <h1>${title}</h1>${bodyHtml}</body></html>`);
  w.document.close();
}

function VocabReview() {
  const profile = useActiveProfile();
  const [, update] = useProfileData(profile);

  const pool = useMemo(() => allBuiltinVocab(), []);
  const [seed, setSeed] = useState(0);

  const questions = useMemo<QuizQuestion[]>(() => {
    void seed;
    if (pool.length < 4) return [];
    const picked = shuffle(pool).slice(0, 10);
    return picked.map((w) => {
      const wrongs = shuffle(pool.filter((x) => x.en !== w.en))
        .slice(0, 3)
        .map((x) => x.pl);
      const opts = shuffle([w.pl, ...wrongs]);
      return {
        question: `Co oznacza: "${w.en}"?`,
        options: opts,
        correctIndex: opts.indexOf(w.pl),
        explanation: `${w.en} — ${w.pl}${w.example ? ` · ${w.example}` : ""} (${w.lessonTopic})`,
      };
    });
  }, [pool, seed]);

  const [i, setI] = useState(0);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  const printAll = () => {
    const rows = pool
      .map(
        (v) =>
          `<tr><td><strong>${v.en}</strong></td><td>${v.ipa ?? ""}</td><td>${v.pl}</td><td><em>${v.example ?? ""}</em></td><td style="color:#666">${v.lessonTopic}</td></tr>`,
      )
      .join("");
    openPrintWindow(
      `Słówka (${pool.length}) — EnglishLab`,
      `<table><thead><tr><th>EN</th><th>IPA</th><th>PL</th><th>Przykład</th><th>Lekcja</th></tr></thead><tbody>${rows}</tbody></table>`,
    );
  };

  const restart = () => {
    setI(0);
    setScore(0);
    setDone(false);
    setSeed((s) => s + 1);
  };

  if (done) {
    return (
      <div className="space-y-4 text-center py-12">
        <h1 className="text-3xl">Powtórka zakończona</h1>
        <p className="text-xl">
          Wynik:{" "}
          <span className="font-bold" style={{ color: "#000" }}>
            {score} / {questions.length}
          </span>
        </p>
        <Button onClick={restart}>
          <RefreshCw className="h-4 w-4" /> Powtórz z innymi słówkami
        </Button>
      </div>
    );
  }

  const finish = (finalScore: number) => {
    update((d) => ({
      ...d,
      results: [
        ...d.results,
        { id: uid(), type: "vocab", score: finalScore, total: questions.length, at: Date.now() },
      ],
    }));
    setDone(true);
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm text-muted-foreground">
            Pula: {pool.length} słówek z 50 lekcji
          </p>
          <h1 className="text-3xl mt-1">Powtórka Słówek</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={printAll}>
            <Printer className="h-4 w-4" /> Drukuj listę
          </Button>
          <Button variant="outline" size="sm" onClick={restart}>
            <RefreshCw className="h-4 w-4" /> Nowy zestaw
          </Button>
        </div>
      </header>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {i + 1} / {questions.length}
        </span>
        <span>Wynik: {score}</span>
      </div>

      <QuizCard
        key={`${seed}-${i}`}
        q={questions[i]}
        onAnswer={(c) => c && setScore((s) => s + 1)}
        onNext={() => {
          if (i + 1 >= questions.length) finish(score + (questions[i] ? 0 : 0));
          else setI(i + 1);
        }}
        isLast={i + 1 >= questions.length}
      />
    </div>
  );
}
