import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Check, X, Target, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { BuiltinQuizQ } from "@/content/lessons";

interface Props {
  questions: BuiltinQuizQ[]; // typically 5 first quiz items
  onFinish: (correct: number, total: number) => void;
}

export function PreTest({ questions, onFinish }: Props) {
  const [idx, setIdx] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [correct, setCorrect] = useState(0);
  const [done, setDone] = useState(false);

  if (!questions.length) return null;

  if (done) {
    const pct = Math.round((correct / questions.length) * 100);
    const passed = pct >= 80;
    return (
      <div className="rounded-lg border bg-card p-5 text-center space-y-3">
        <Target className={cn("h-8 w-8 mx-auto", passed ? "text-green-600" : "text-amber-500")} />
        <p className="text-2xl font-bold" style={{ color: "#000" }}>
          {correct} / {questions.length}
        </p>
        <p className="text-sm text-muted-foreground">
          {passed
            ? "Świetnie znasz materiał! Możesz przejrzeć szybko i pominąć do quizu końcowego."
            : "Warto przerobić lekcję — odkryjesz nowe słówka i konstrukcje."}
        </p>
      </div>
    );
  }

  const q = questions[idx];
  const isCorrect = picked === q.correct;

  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1"><Target className="h-3 w-3" /> Pre-test</span>
        <span>Pytanie {idx + 1} z {questions.length}</span>
      </div>
      <p className="font-medium">{q.q}</p>
      <div className="grid gap-2">
        {q.options.map((opt, i) => {
          const isPicked = picked === i;
          const showCorrect = picked != null && i === q.correct;
          const showWrong = isPicked && i !== q.correct;
          return (
            <button
              key={i}
              disabled={picked != null}
              onClick={() => {
                setPicked(i);
                if (i === q.correct) setCorrect((c) => c + 1);
              }}
              className={cn(
                "rounded-lg border px-3 py-2 text-left text-sm transition-colors",
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
      </div>
      {picked != null && (
        <Button
          size="sm"
          onClick={() => {
            const finalCorrect = correct; // already updated by setCorrect on click
            if (idx + 1 === questions.length) {
              setDone(true);
              onFinish(finalCorrect, questions.length);
            } else {
              setPicked(null);
              setIdx((i) => i + 1);
            }
          }}
        >
          {idx + 1 === questions.length ? "Zobacz wynik" : "Dalej"} <ChevronRight className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
