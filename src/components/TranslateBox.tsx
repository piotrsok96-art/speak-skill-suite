import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { SpeakButton } from "@/components/SpeakButton";
import { Check, Eye, ChevronRight, Sparkles, ThumbsUp, ThumbsDown } from "lucide-react";
import { cn } from "@/lib/utils";
import type { BuiltinTranslation } from "@/content/lessons";

interface Props {
  items: BuiltinTranslation[];
  onFinish?: (correct: number, total: number) => void;
}

function score(input: string, target: string): number {
  // Token-overlap proportion (very rough).
  const tokenize = (s: string) =>
    s.toLowerCase().replace(/[.,!?;:"]/g, "").split(/\s+/).filter(Boolean);
  const a = new Set(tokenize(input));
  const b = tokenize(target);
  if (!b.length) return 0;
  const hit = b.filter((w) => a.has(w)).length;
  return hit / b.length;
}

export function TranslateBox({ items, onFinish }: Props) {
  const [idx, setIdx] = useState(0);
  const [value, setValue] = useState("");
  const [revealed, setRevealed] = useState(false);
  const [self, setSelf] = useState<null | boolean>(null);
  const [correct, setCorrect] = useState(0);
  const [done, setDone] = useState(false);

  if (!items.length) return null;

  if (done) {
    return (
      <div className="rounded-lg border bg-card p-6 text-center space-y-2">
        <p className="text-2xl font-bold" style={{ color: "#000" }}>
          {correct} / {items.length}
        </p>
        <p className="text-sm text-muted-foreground">Brawo!</p>
        <Button
          variant="outline"
          size="sm"
          className="mt-2"
          onClick={() => { setIdx(0); setValue(""); setRevealed(false); setSelf(null); setCorrect(0); setDone(false); }}
        >
          Spróbuj ponownie
        </Button>
      </div>
    );
  }

  const item = items[idx];
  const auto = score(value, item.en);

  const next = () => {
    if (idx + 1 >= items.length) {
      setDone(true);
      onFinish?.(correct, items.length);
      return;
    }
    setIdx((i) => i + 1); setValue(""); setRevealed(false); setSelf(null);
  };

  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Zdanie {idx + 1} z {items.length}</span>
        <span>Poprawne: {correct}</span>
      </div>
      <p className="text-xs uppercase tracking-wide text-muted-foreground">Przetłumacz na angielski:</p>
      <p className="text-base font-medium" style={{ color: "#000" }}>{item.pl}</p>
      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Twoje tłumaczenie po angielsku…"
        rows={2}
        disabled={revealed}
      />
      {!revealed ? (
        <div className="flex gap-2 flex-wrap">
          <Button onClick={() => setRevealed(true)} disabled={!value.trim()}>
            <Check className="h-4 w-4" /> Sprawdź
          </Button>
          <Button variant="outline" onClick={() => { setValue(""); setRevealed(true); }}>
            <Eye className="h-4 w-4" /> Pokaż odpowiedź
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="rounded-md bg-secondary p-3 space-y-1">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Wzorcowa odpowiedź</p>
            <div className="flex items-start gap-2">
              <SpeakButton text={item.en} />
              <p className="font-medium" style={{ color: "#000" }}>{item.en}</p>
            </div>
            <p className="text-xs text-muted-foreground">
              Trafność słów: {Math.round(auto * 100)}%
            </p>
          </div>
          {self == null ? (
            <div className="flex gap-2 flex-wrap">
              <p className="text-sm self-center">Jak Ci poszło?</p>
              <Button
                size="sm"
                className="bg-green-600 hover:bg-green-700 text-white"
                onClick={() => { setSelf(true); setCorrect((c) => c + 1); }}
              >
                <ThumbsUp className="h-4 w-4" /> Dobrze
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setSelf(false)}
              >
                <ThumbsDown className="h-4 w-4" /> Jeszcze nie
              </Button>
            </div>
          ) : (
            <Button onClick={next} className={cn(self && "bg-green-600 hover:bg-green-700 text-white")}>
              {idx + 1 === items.length ? <><Sparkles className="h-4 w-4" /> Zakończ</> : <>Dalej <ChevronRight className="h-4 w-4" /></>}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
