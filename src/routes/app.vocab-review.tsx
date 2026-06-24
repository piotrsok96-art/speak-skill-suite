import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData, uid } from "@/lib/store";
import { QuizCard, type QuizQuestion } from "@/components/QuizCard";
import { Button } from "@/components/ui/button";
import { Link } from "@tanstack/react-router";

export const Route = createFileRoute("/app/vocab-review")({
  component: VocabReview,
});

function shuffle<T>(arr: T[]): T[] {
  return [...arr].sort(() => Math.random() - 0.5);
}

function VocabReview() {
  const profile = useActiveProfile();
  const [data, update] = useProfileData(profile);

  const questions = useMemo<QuizQuestion[]>(() => {
    if (data.words.length < 4) return [];
    const pool = shuffle(data.words).slice(0, 10);
    return pool.map((w) => {
      const wrongs = shuffle(data.words.filter((x) => x.id !== w.id))
        .slice(0, 3)
        .map((x) => x.meaning);
      const opts = shuffle([w.meaning, ...wrongs]);
      return {
        question: `Co oznacza: "${w.word}"?`,
        options: opts,
        correctIndex: opts.indexOf(w.meaning),
        explanation: `${w.word} — ${w.meaning}${w.example ? ` · ${w.example}` : ""}`,
      };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data.words.length]);

  const [i, setI] = useState(0);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  if (data.words.length < 4) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl">Powtórka Słówek</h1>
        <p className="text-muted-foreground">
          Dodaj co najmniej 4 słówka do bazy, aby rozpocząć powtórkę.
        </p>
        <Button asChild>
          <Link to="/app/lesson">Przejdź do lekcji</Link>
        </Button>
      </div>
    );
  }

  if (done) {
    return (
      <div className="space-y-4 text-center py-12">
        <h1 className="text-3xl">Powtórka zakończona</h1>
        <p className="text-xl">
          Wynik: <span className="font-bold" style={{ color: "#000" }}>{score} / {questions.length}</span>
        </p>
        <Button onClick={() => window.location.reload()}>Powtórz</Button>
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
      <div className="flex items-center justify-between">
        <h1 className="text-3xl">Powtórka Słówek</h1>
        <span className="text-sm text-muted-foreground">
          {i + 1} / {questions.length}
        </span>
      </div>
      <QuizCard
        key={i}
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
