import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData, uid } from "@/lib/store";
import { BUILTIN_LESSONS, type BuiltinQuizQ } from "@/content/lessons";
import { QuizCard, type QuizQuestion } from "@/components/QuizCard";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

export const Route = createFileRoute("/app/grammar-quiz")({
  component: GrammarQuiz,
});

function shuffle<T>(arr: T[]): T[] {
  return [...arr].sort(() => Math.random() - 0.5);
}

// Pull all grammar questions from BUILTIN_LESSONS (prefix "Gramatyka").
function allGrammarQs(): BuiltinQuizQ[] {
  const out: BuiltinQuizQ[] = [];
  const seen = new Set<string>();
  for (const l of BUILTIN_LESSONS) {
    for (const q of [...l.quiz, ...l.pretest]) {
      if (!q.q.startsWith("Gramatyka")) continue;
      const key = q.q + "|" + q.options.join("|");
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(q);
    }
  }
  return out;
}

function GrammarQuiz() {
  const profile = useActiveProfile();
  const [, update] = useProfileData(profile);

  const pool = useMemo(() => allGrammarQs(), []);
  const [seed, setSeed] = useState(0);

  const questions = useMemo<QuizQuestion[]>(() => {
    void seed;
    return shuffle(pool)
      .slice(0, 12)
      .map((q) => ({
        question: q.q,
        options: q.options,
        correctIndex: q.correct,
        explanation: q.explain,
      }));
  }, [pool, seed]);

  const [i, setI] = useState(0);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  const restart = () => { setI(0); setScore(0); setDone(false); setSeed((s) => s + 1); };

  if (questions.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl">Quiz Gramatyczny</h1>
        <p className="text-muted-foreground">Brak pytań gramatycznych.</p>
      </div>
    );
  }

  if (done) {
    return (
      <div className="space-y-4 text-center py-12">
        <h1 className="text-3xl">Quiz zakończony</h1>
        <p className="text-xl">
          Wynik:{" "}
          <span className="font-bold" style={{ color: "#000" }}>
            {score} / {questions.length}
          </span>
        </p>
        <Button onClick={restart}>
          <RefreshCw className="h-4 w-4" /> Powtórz z nowym zestawem
        </Button>
      </div>
    );
  }

  const finish = (finalScore: number) => {
    update((d) => ({
      ...d,
      results: [
        ...d.results,
        { id: uid(), type: "grammar", score: finalScore, total: questions.length, at: Date.now() },
      ],
    }));
    setDone(true);
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <p className="text-sm text-muted-foreground">
            Pula: {pool.length} pytań gramatycznych z 50 lekcji
          </p>
          <h1 className="text-3xl mt-1">Quiz Gramatyczny</h1>
        </div>
        <Button variant="outline" size="sm" onClick={restart}>
          <RefreshCw className="h-4 w-4" /> Nowy zestaw
        </Button>
      </header>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>{i + 1} / {questions.length}</span>
        <span>Wynik: {score}</span>
      </div>

      <QuizCard
        key={`${seed}-${i}`}
        q={questions[i]}
        onAnswer={(c) => c && setScore((s) => s + 1)}
        onNext={() => {
          if (i + 1 >= questions.length) finish(score);
          else setI(i + 1);
        }}
        isLast={i + 1 >= questions.length}
      />
    </div>
  );
}
