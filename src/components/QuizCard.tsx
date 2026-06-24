import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ArrowRight } from "lucide-react";

export interface QuizQuestion {
  question: string;
  options: string[];
  correctIndex: number;
  explanation?: string;
}

export function QuizCard({
  q,
  onAnswer,
  onNext,
  isLast,
}: {
  q: QuizQuestion;
  onAnswer: (correct: boolean) => void;
  onNext: () => void;
  isLast: boolean;
}) {
  const [picked, setPicked] = useState<number | null>(null);
  const answered = picked !== null;
  const correct = picked === q.correctIndex;

  const pick = (i: number) => {
    if (answered) return;
    setPicked(i);
    onAnswer(i === q.correctIndex);
  };

  const next = () => {
    setPicked(null);
    onNext();
  };

  return (
    <div className="rounded-xl border bg-card p-6 space-y-5">
      <h2 className="text-xl leading-snug">{q.question}</h2>
      <div className="grid gap-3">
        {q.options.map((opt, i) => {
          const isPicked = picked === i;
          const isRight = answered && i === q.correctIndex;
          const isWrong = answered && isPicked && i !== q.correctIndex;
          return (
            <button
              key={i}
              onClick={() => pick(i)}
              disabled={answered}
              style={
                isRight
                  ? {
                      backgroundColor: "var(--quiz-correct-bg)",
                      borderColor: "var(--quiz-correct-border)",
                      color: "var(--quiz-correct-fg)",
                    }
                  : isWrong
                  ? {
                      backgroundColor: "var(--quiz-wrong-bg)",
                      borderColor: "var(--quiz-wrong-border)",
                      color: "var(--quiz-wrong-fg)",
                    }
                  : undefined
              }
              className={cn(
                "w-full text-left rounded-lg border-2 px-4 py-3 text-sm font-semibold transition-colors",
                !answered &&
                  "bg-secondary border-transparent text-foreground hover:border-foreground/30",
                answered && !isRight && !isWrong && "opacity-60 bg-secondary border-transparent",
              )}
            >
              {opt}
            </button>
          );
        })}
      </div>

      {answered && (
        <div
          className="rounded-lg border-2 p-4 text-sm"
          style={
            correct
              ? {
                  backgroundColor: "var(--quiz-correct-bg)",
                  borderColor: "var(--quiz-correct-border)",
                  color: "var(--quiz-correct-fg)",
                }
              : {
                  backgroundColor: "var(--quiz-wrong-bg)",
                  borderColor: "var(--quiz-wrong-border)",
                  color: "var(--quiz-wrong-fg)",
                }
          }
        >
          <div className="font-bold mb-1">{correct ? "Świetnie!" : "Dlaczego źle?"}</div>
          {q.explanation && <div>{q.explanation}</div>}
        </div>
      )}

      {answered && (
        <div className="flex justify-end">
          <Button onClick={next}>
            {isLast ? "Zakończ" : "Dalej"} <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
