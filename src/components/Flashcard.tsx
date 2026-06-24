import { useState } from "react";
import { SpeakButton } from "./SpeakButton";
import { Button } from "./ui/button";
import { ArrowLeftRight, RotateCw } from "lucide-react";

export interface FlashcardItem {
  en: string;
  ipa?: string;
  pl: string;
  example?: string;
}

export function Flashcard({
  item,
  mode,
  onKnown,
  onLearning,
  onNext,
}: {
  item: FlashcardItem;
  mode: "en-pl" | "pl-en";
  onKnown: () => void;
  onLearning: () => void;
  onNext: () => void;
}) {
  const [flipped, setFlipped] = useState(false);
  const front = mode === "en-pl" ? item.en : item.pl;
  const back = mode === "en-pl" ? item.pl : item.en;
  const speakText = mode === "en-pl" ? item.en : item.en;

  return (
    <div className="space-y-3">
      <button
        onClick={() => setFlipped((f) => !f)}
        className="w-full min-h-[260px] rounded-xl border-2 bg-card p-8 flex flex-col items-center justify-center text-center transition-all hover:shadow-md active:scale-[0.99]"
      >
        <p className="text-xs uppercase tracking-wide text-muted-foreground mb-3">
          {flipped ? (mode === "en-pl" ? "PL" : "EN") : mode === "en-pl" ? "EN" : "PL"}
        </p>
        <p className="text-3xl font-bold" style={{ color: "#000" }}>
          {flipped ? back : front}
        </p>
        {!flipped && mode === "en-pl" && item.ipa && (
          <p className="text-sm text-muted-foreground font-mono mt-2">[{item.ipa}]</p>
        )}
        {flipped && item.example && (
          <p className="text-sm text-muted-foreground italic mt-4">{item.example}</p>
        )}
        <p className="text-xs text-muted-foreground mt-6">
          {flipped ? "Kliknij, aby odwrócić" : "Kliknij, aby zobaczyć tłumaczenie"}
        </p>
      </button>

      <div className="flex items-center justify-center gap-2">
        <SpeakButton text={speakText} size={18} />
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setFlipped(false);
            onNext();
          }}
        >
          <RotateCw className="h-4 w-4" /> Następna
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <Button
          variant="outline"
          onClick={() => {
            onLearning();
            setFlipped(false);
          }}
          className="border-amber-500/40 hover:bg-amber-500/10"
        >
          Nie znam
        </Button>
        <Button
          onClick={() => {
            onKnown();
            setFlipped(false);
          }}
          className="bg-green-600 hover:bg-green-700"
        >
          Znam
        </Button>
      </div>

      <p className="text-center text-xs text-muted-foreground">
        Tryb: {mode === "en-pl" ? "EN → PL" : "PL → EN"}{" "}
        <ArrowLeftRight className="inline h-3 w-3 ml-1" />
      </p>
    </div>
  );
}
