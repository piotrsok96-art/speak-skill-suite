import { Check, X } from "lucide-react";
import { SpeakButton } from "./SpeakButton";
import { cn } from "@/lib/utils";
import type { WordStatus } from "@/lib/store";

export interface VocabRowItem {
  key: string;
  en: string;
  ipa: string;
  plPron: string;
  pl: string;
  example: string;
}

export function VocabRow({
  item,
  status,
  onMark,
}: {
  item: VocabRowItem;
  status?: WordStatus;
  onMark: (status: WordStatus) => void;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border p-3 transition-colors",
        status === "known" && "border-green-500/40 bg-green-500/5",
        status === "learning" && "border-amber-500/40 bg-amber-500/5",
        !status && "bg-card",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
            <SpeakButton text={item.en} />
            <span className="text-lg font-bold" style={{ color: "#000" }}>
              {item.en}
            </span>
            {item.ipa && (
              <span className="text-xs text-muted-foreground font-mono">[{item.ipa}]</span>
            )}
            {item.plPron && (
              <span className="text-xs text-muted-foreground">({item.plPron})</span>
            )}
            <span className="text-sm">— {item.pl}</span>
          </div>
          {item.example && (
            <p className="text-sm text-muted-foreground italic mt-1">{item.example}</p>
          )}
        </div>
        <div className="flex flex-col gap-1 shrink-0">
          <button
            onClick={() => onMark("known")}
            className={cn(
              "inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium transition-colors",
              status === "known"
                ? "bg-green-600 text-white border-green-600"
                : "hover:bg-green-500/10 hover:border-green-500/40 text-muted-foreground",
            )}
            aria-label="Znam"
            title="Znam"
          >
            <Check className="h-3 w-3" /> Znam
          </button>
          <button
            onClick={() => onMark("learning")}
            className={cn(
              "inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium transition-colors",
              status === "learning"
                ? "bg-amber-500 text-white border-amber-500"
                : "hover:bg-amber-500/10 hover:border-amber-500/40 text-muted-foreground",
            )}
            aria-label="Nie znam"
            title="Nie znam (do powtórki)"
          >
            <X className="h-3 w-3" /> Nie znam
          </button>
        </div>
      </div>
    </div>
  );
}
