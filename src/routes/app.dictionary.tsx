import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { useActiveProfile, useProfileData, type Word } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Flashcard } from "@/components/Flashcard";
import { SpeakButton } from "@/components/SpeakButton";
import { Printer, Repeat2, Table, Layers, ArrowLeftRight } from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/dictionary")({
  component: Dictionary,
});

function Dictionary() {
  const profile = useActiveProfile();
  const [data] = useProfileData(profile);
  const [view, setView] = useState<"table" | "cards">("table");
  const [mode, setMode] = useState<"en-pl" | "pl-en">("en-pl");
  const [cardIdx, setCardIdx] = useState(0);

  const srsLearning = useMemo(() => Object.values(data.srs), [data.srs]);

  const cardItems = useMemo<Word[]>(() => {
    const shuffled = [...data.words];
    // deterministic-ish shuffle by id
    shuffled.sort((a, b) => a.id.localeCompare(b.id));
    return shuffled;
  }, [data.words]);

  const next = () => setCardIdx((i) => (cardItems.length === 0 ? 0 : (i + 1) % cardItems.length));

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p className="text-sm text-muted-foreground">Twoja baza</p>
          <h1 className="text-3xl mt-1">Mój Słowniczek</h1>
        </div>
        <div className="flex gap-2 no-print">
          <div className="inline-flex rounded-lg border bg-card p-1">
            <button
              onClick={() => setView("table")}
              className={cn(
                "inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                view === "table" ? "bg-secondary text-foreground" : "text-muted-foreground",
              )}
            >
              <Table className="h-3 w-3" /> Tabela
            </button>
            <button
              onClick={() => setView("cards")}
              className={cn(
                "inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                view === "cards" ? "bg-secondary text-foreground" : "text-muted-foreground",
              )}
            >
              <Layers className="h-3 w-3" /> Fiszki
            </button>
          </div>
          <Button variant="outline" onClick={() => window.print()}>
            <Printer className="h-4 w-4" /> Drukuj
          </Button>
        </div>
      </div>

      {srsLearning.length > 0 && (
        <section className="rounded-xl border border-amber-500/40 bg-amber-500/5 p-4 no-print">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div>
              <h2 className="text-base font-semibold flex items-center gap-2">
                <Repeat2 className="h-4 w-4" /> Do powtórki ({srsLearning.length})
              </h2>
              <p className="text-sm text-muted-foreground mt-0.5">
                Słówka, które oznaczyłeś jako „Nie znam" — w kolejce algorytmu SRS.
              </p>
            </div>
            <Link
              to="/app/srs"
              className="inline-flex items-center gap-1 rounded-lg bg-foreground text-background px-3 py-1.5 text-sm font-medium"
            >
              Rozpocznij powtórkę →
            </Link>
          </div>
          <ul className="mt-3 grid sm:grid-cols-2 gap-1 text-sm">
            {srsLearning.slice(0, 10).map((s) => (
              <li key={s.key} className="flex items-center gap-2">
                <SpeakButton text={s.en} />
                <span className="font-medium" style={{ color: "#000" }}>
                  {s.en}
                </span>
                <span className="text-muted-foreground">— {s.pl}</span>
              </li>
            ))}
            {srsLearning.length > 10 && (
              <li className="text-xs text-muted-foreground">…i {srsLearning.length - 10} więcej</li>
            )}
          </ul>
        </section>
      )}

      {view === "cards" ? (
        <section className="no-print">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xl">Fiszki ({cardItems.length})</h2>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setMode((m) => (m === "en-pl" ? "pl-en" : "en-pl"))}
            >
              <ArrowLeftRight className="h-4 w-4" /> {mode === "en-pl" ? "EN → PL" : "PL → EN"}
            </Button>
          </div>
          {cardItems.length === 0 ? (
            <p className="text-muted-foreground">Brak słówek. Zapisz coś z lekcji.</p>
          ) : (
            (() => {
              const w = cardItems[cardIdx % cardItems.length];
              return (
                <Flashcard
                  item={{ en: w.word, ipa: w.ipa, pl: w.meaning, example: w.example }}
                  mode={mode}
                  onKnown={next}
                  onLearning={next}
                  onNext={next}
                />
              );
            })()
          )}
        </section>
      ) : (
        <section>
          <h2 className="text-xl mb-3">Słówka ({data.words.length})</h2>
          {data.words.length === 0 ? (
            <p className="text-muted-foreground">Brak zapisanych słówek.</p>
          ) : (
            <div className="rounded-lg border overflow-hidden bg-card">
              <table className="w-full text-sm">
                <thead className="bg-secondary">
                  <tr>
                    <th className="text-left px-4 py-2 font-semibold">Słówko</th>
                    <th className="text-left px-4 py-2 font-semibold">Wymowa IPA</th>
                    <th className="text-left px-4 py-2 font-semibold">Wymowa PL</th>
                    <th className="text-left px-4 py-2 font-semibold">Znaczenie</th>
                  </tr>
                </thead>
                <tbody>
                  {data.words.map((w) => (
                    <tr key={w.id} className="border-t">
                      <td className="px-4 py-2 font-bold" style={{ color: "#000" }}>
                        <span className="inline-flex items-center gap-1">
                          <span className="no-print">
                            <SpeakButton text={w.word} />
                          </span>
                          {w.word}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-muted-foreground font-mono">{w.ipa}</td>
                      <td className="px-4 py-2 text-muted-foreground">{w.pronouncePl}</td>
                      <td className="px-4 py-2">{w.meaning}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      <section>
        <h2 className="text-xl mb-3">Idiomy ({data.idioms.length})</h2>
        {data.idioms.length === 0 ? (
          <p className="text-muted-foreground">Brak zapisanych idiomów.</p>
        ) : (
          <div className="rounded-lg border overflow-hidden bg-card">
            <table className="w-full text-sm">
              <thead className="bg-secondary">
                <tr>
                  <th className="text-left px-4 py-2 font-semibold">Idiom</th>
                  <th className="text-left px-4 py-2 font-semibold">Znaczenie</th>
                  <th className="text-left px-4 py-2 font-semibold">Przykład</th>
                </tr>
              </thead>
              <tbody>
                {data.idioms.map((i) => (
                  <tr key={i.id} className="border-t">
                    <td className="px-4 py-2 font-bold" style={{ color: "#000" }}>
                      {i.idiom}
                    </td>
                    <td className="px-4 py-2">{i.meaning}</td>
                    <td className="px-4 py-2 text-muted-foreground italic">{i.example}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
