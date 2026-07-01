import { useState } from "react";
import type { SrsItem } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { matchEn, normalizeEn } from "@/lib/fuzzy";
import { cn } from "@/lib/utils";
import { SpeakButton } from "@/components/SpeakButton";
import { Check, Lightbulb } from "lucide-react";

interface Props {
  item: SrsItem;
  onResult: (result: "exact" | "close" | "wrong", grade: 0 | 1 | 2 | 3) => void;
}

export function ProduceCard({ item, onResult }: Props) {
  const [typed, setTyped] = useState("");
  const [checked, setChecked] = useState(false);
  const [hint, setHint] = useState(false);

  const result = checked ? matchEn(typed, item.en) : null;

  const submit = () => {
    if (!typed.trim() || checked) return;
    setChecked(true);
    const r = matchEn(typed, item.en);
    // Grading: exact = OK (2), close = trudne (1), wrong = nie pamiętam (0).
    const grade = r === "exact" ? 2 : r === "close" ? 1 : 0;
    onResult(r, grade);
  };

  const firstLetter = item.en.charAt(0);
  const letterCount = item.en.replace(/\s/g, "").length;

  return (
    <div className="space-y-3 max-w-md mx-auto w-full">
      <div className="text-center">
        <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">PL → EN</p>
        <p className="text-2xl font-semibold" style={{ color: "#000" }}>
          {item.pl}
        </p>
        {hint && !checked && (
          <p className="text-xs text-muted-foreground mt-2">
            Zaczyna się na <strong>{firstLetter}</strong> · {letterCount} liter
          </p>
        )}
      </div>
      <Input
        autoFocus
        value={typed}
        onChange={(e) => setTyped(e.target.value)}
        disabled={checked}
        placeholder="Wpisz po angielsku…"
        onKeyDown={(e) => {
          if (e.key === "Enter") submit();
        }}
      />
      {!checked ? (
        <div className="flex gap-2">
          <Button className="flex-1" onClick={submit} disabled={!typed.trim()}>
            <Check className="h-4 w-4" /> Sprawdź
          </Button>
          <Button variant="outline" onClick={() => setHint(true)} disabled={hint}>
            <Lightbulb className="h-4 w-4" /> Podpowiedź
          </Button>
        </div>
      ) : (
        <div
          className={cn(
            "rounded-md p-3 text-sm text-center",
            result === "exact" && "bg-green-500/10 text-green-700",
            result === "close" && "bg-amber-500/10 text-amber-700",
            result === "wrong" && "bg-red-500/10 text-red-700",
          )}
        >
          <p className="font-semibold">
            {result === "exact"
              ? "Dokładnie!"
              : result === "close"
              ? `Blisko — poprawnie: ${item.en}`
              : `Poprawnie: ${item.en}`}
          </p>
          {normalizeEn(typed) !== normalizeEn(item.en) && (
            <p className="text-xs mt-1">Twoja odpowiedź: {typed}</p>
          )}
          <div className="mt-2 flex items-center justify-center gap-2">
            <SpeakButton text={item.en} size={16} />
            {item.example && (
              <span className="italic text-muted-foreground text-xs">{item.example}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
