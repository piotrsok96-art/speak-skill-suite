import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SpeakButton } from "@/components/SpeakButton";
import { Check, Eye, X, ChevronRight, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import type { BuiltinFillBlank } from "@/content/lessons";

interface Props {
  items: BuiltinFillBlank[];
  onFinish?: (correct: number, total: number) => void;
}

function normalize(s: string) {
  return s.trim().toLowerCase().replace(/[.,!?]/g, "");
}

export function FillBlank({ items, onFinish }: Props) {
  const [idx, setIdx] = useState(0);
  const [value, setValue] = useState("");
  const [checked, setChecked] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [done, setDone] = useState(false);

  if (!items.length) return null;

  if (done) {
    return (
      <div className="rounded-lg border bg-card p-6 text-center space-y-2">
        <p className="text-2xl font-bold" style={{ color: "#000" }}>
          {correct} / {items.length}
        </p>
        <p className="text-sm text-muted-foreground">Świetna robota!</p>
        <Button
          variant="outline"
          size="sm"
          className="mt-2"
          onClick={() => {
            setIdx(0); setValue(""); setChecked(false); setRevealed(false); setCorrect(0); setDone(false);
          }}
        >
          Spróbuj jeszcze raz
        </Button>
      </div>
    );
  }

  const item = items[idx];
  const isCorrect = normalize(value) === normalize(item.answer);

  const next = () => {
    if (idx + 1 >= items.length) {
      setDone(true);
      onFinish?.(correct + (checked && isCorrect ? 1 : 0), items.length);
      return;
    }
    setIdx((i) => i + 1);
    setValue(""); setChecked(false); setRevealed(false);
  };

  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Zdanie {idx + 1} z {items.length}</span>
        <span>Poprawne: {correct}</span>
      </div>
      <div className="flex items-start gap-2">
        <SpeakButton text={item.full} />
        <p className="text-base leading-relaxed" style={{ color: "#000" }}>
          {item.sentence}
        </p>
      </div>
      <p className="text-xs italic text-muted-foreground">Wskazówka (PL): {item.hint}</p>
      <div className="flex gap-2 flex-wrap">
        <Input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Wpisz brakujące słowo…"
          disabled={checked}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              if (!checked) {
                setChecked(true);
                if (isCorrect) setCorrect((c) => c + 1);
              } else next();
            }
          }}
          className="flex-1 min-w-[160px]"
        />
        {!checked ? (
          <>
            <Button
              onClick={() => {
                setChecked(true);
                if (isCorrect) setCorrect((c) => c + 1);
              }}
              disabled={!value.trim()}
            >
              <Check className="h-4 w-4" /> Sprawdź
            </Button>
            <Button variant="outline" size="icon" onClick={() => setRevealed(true)} title="Podpowiedz">
              <Eye className="h-4 w-4" />
            </Button>
          </>
        ) : (
          <Button onClick={next}>
            {idx + 1 === items.length ? <><Sparkles className="h-4 w-4" /> Zakończ</> : <>Dalej <ChevronRight className="h-4 w-4" /></>}
          </Button>
        )}
      </div>
      {revealed && !checked && (
        <p className="text-xs text-amber-600">Odpowiedź: <span className="font-semibold">{item.answer}</span></p>
      )}
      {checked && (
        <div className={cn(
          "rounded-md p-3 text-sm flex items-start gap-2",
          isCorrect ? "bg-green-500/10 text-green-700" : "bg-red-500/10 text-red-700",
        )}>
          {isCorrect ? <Check className="h-4 w-4 mt-0.5" /> : <X className="h-4 w-4 mt-0.5" />}
          <div>
            <p className="font-semibold">
              {isCorrect ? "Dobrze!" : `Poprawnie: ${item.answer}`}
            </p>
            <p className="italic opacity-90">{item.full}</p>
          </div>
        </div>
      )}
    </div>
  );
}
