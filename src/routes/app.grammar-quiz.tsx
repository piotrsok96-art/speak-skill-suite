import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData, uid } from "@/lib/store";
import { QuizCard, type QuizQuestion } from "@/components/QuizCard";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/app/grammar-quiz")({
  component: GrammarQuiz,
});

function GrammarQuiz() {
  const profile = useActiveProfile();
  const [data, update] = useProfileData(profile);

  const questions = useMemo<QuizQuestion[]>(() => {
    return [...data.grammarRules]
      .sort(() => Math.random() - 0.5)
      .slice(0, 10)
      .map((r) => ({
        question: r.question,
        options: r.options,
        correctIndex: r.correctIndex,
        explanation: r.explanation,
      }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data.grammarRules.length]);

  const [i, setI] = useState(0);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);

  if (questions.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl">Quiz Gramatyczny</h1>
        <p className="text-muted-foreground">
          Brak pytań gramatycznych. Ukończ przynajmniej jedną lekcję, aby wygenerować quiz.
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
        <h1 className="text-3xl">Quiz zakończony</h1>
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
        { id: uid(), type: "grammar", score: finalScore, total: questions.length, at: Date.now() },
      ],
    }));
    setDone(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl">Quiz Gramatyczny</h1>
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
