import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  useActiveProfile,
  useProfileData,
  uid,
  type Word,
  type Idiom,
} from "@/lib/store";
import {
  parseLesson,
  SAMPLE_LESSON,
  makeGrammarQuestionsFromLesson,
  type ParsedLesson,
} from "@/lib/lesson-parser";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Check, Eye, EyeOff, Plus, Sparkles } from "lucide-react";

export const Route = createFileRoute("/app/lesson")({
  component: LessonPage,
});

function LessonPage() {
  const profile = useActiveProfile();
  const [, update] = useProfileData(profile);
  const [raw, setRaw] = useState(SAMPLE_LESSON);
  const [parsed, setParsed] = useState<ParsedLesson | null>(() => parseLesson(SAMPLE_LESSON));

  const reparse = () => {
    try {
      setParsed(parseLesson(raw));
      toast.success("Lekcja sparsowana");
    } catch {
      toast.error("Nie udało się sparsować lekcji");
    }
  };

  const saveWords = () => {
    if (!parsed) return;
    const now = Date.now();
    update((d) => {
      const existing = new Set(d.words.map((w) => w.word.toLowerCase()));
      const newWords: Word[] = parsed.words
        .filter((w) => !existing.has(w.word.toLowerCase()))
        .map((w) => ({
          ...w,
          id: uid(),
          addedAt: now,
          box: 1,
          nextReview: now,
        }));
      return { ...d, words: [...d.words, ...newWords] };
    });
    toast.success(`Zapisano ${parsed.words.length} słówek`);
  };

  const saveIdiom = () => {
    if (!parsed?.idiom) return;
    const idiom: Idiom = { ...parsed.idiom, id: uid(), addedAt: Date.now() };
    update((d) => ({ ...d, idioms: [...d.idioms, idiom] }));
    toast.success("Zapisano idiom");
  };

  const completeLesson = () => {
    if (!parsed) return;
    update((d) => {
      const newQs = makeGrammarQuestionsFromLesson(parsed).map((q) => ({ ...q, id: uid() }));
      return {
        ...d,
        lessons: [
          ...d.lessons,
          { id: uid(), topic: parsed.topic, level: parsed.level, completedAt: Date.now() },
        ],
        grammarRules: [...d.grammarRules, ...newQs],
      };
    });
    toast.success("Lekcja ukończona");
  };

  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm text-muted-foreground">Moduł lekcji</p>
        <h1 className="text-3xl md:text-4xl mt-1">Nowa Lekcja</h1>
      </header>

      <section className="rounded-xl border bg-card p-5">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="h-4 w-4" />
          <h2 className="text-base">Wklej tekst lekcji</h2>
        </div>
        <p className="text-sm text-muted-foreground mb-3">
          Wklej surowy tekst lekcji wygenerowany przez LLM. Wymagane sekcje: <code># Gramatyka</code>,
          <code> # Błędy</code>, <code># Słówka</code>, <code># Dialog</code>,{" "}
          <code># Tłumaczenie</code>, <code># Idiom</code>.
        </p>
        <Textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          className="font-mono text-sm h-48"
        />
        <div className="mt-3 flex gap-2">
          <Button onClick={reparse}>Parsuj lekcję</Button>
          <Button variant="outline" onClick={() => setRaw(SAMPLE_LESSON)}>
            Załaduj przykład
          </Button>
        </div>
      </section>

      {parsed && <LessonView parsed={parsed} onSaveWords={saveWords} onSaveIdiom={saveIdiom} />}

      {parsed && (
        <div className="flex justify-end">
          <Button onClick={completeLesson} size="lg">
            <Check className="h-4 w-4" /> Oznacz lekcję jako ukończoną
          </Button>
        </div>
      )}
    </div>
  );
}

function LessonView({
  parsed,
  onSaveWords,
  onSaveIdiom,
}: {
  parsed: ParsedLesson;
  onSaveWords: () => void;
  onSaveIdiom: () => void;
}) {
  return (
    <article className="space-y-8">
      <header className="border-b pb-4">
        <p className="text-sm text-muted-foreground">Poziom {parsed.level}</p>
        <h2 className="text-3xl mt-1">{parsed.topic}</h2>
      </header>

      <section>
        <h3 className="text-xl mb-3">Gramatyka</h3>
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-secondary">
              <tr>
                <th className="text-left px-4 py-2 font-semibold">Zasada</th>
              </tr>
            </thead>
            <tbody>
              {parsed.grammar.rules.split("\n").filter(Boolean).map((row, i) => (
                <tr key={i} className="border-t">
                  <td className="px-4 py-2 whitespace-pre-wrap">{row}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {parsed.grammar.mistakes && (
          <div className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
            <h4 className="text-sm mb-2">⚠️ Błędy Polaków</h4>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {parsed.grammar.mistakes
                .split("\n")
                .map((l) => l.replace(/^[-*•]\s*/, "").trim())
                .filter(Boolean)
                .map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
            </ul>
          </div>
        )}
      </section>

      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xl">Słówka</h3>
          <Button size="sm" onClick={onSaveWords}>
            <Plus className="h-4 w-4" /> Zapisz do bazy
          </Button>
        </div>
        <ul className="space-y-2">
          {parsed.words.map((w, i) => (
            <li key={i} className="rounded-lg border bg-card p-4">
              <div className="flex flex-wrap items-baseline gap-x-3">
                <span className="text-lg font-bold" style={{ color: "#000" }}>
                  {w.word}
                </span>
                {w.ipa && (
                  <span className="text-sm text-muted-foreground font-mono">[{w.ipa}]</span>
                )}
                {w.pronouncePl && <span className="text-sm text-muted-foreground">({w.pronouncePl})</span>}
                <span className="text-sm">— {w.meaning}</span>
              </div>
              {w.example && <p className="text-sm text-muted-foreground mt-1 italic">{w.example}</p>}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="text-xl mb-3">Dialog</h3>
        <div className="rounded-lg border bg-card divide-y">
          {parsed.dialogue.map((d, i) => (
            <div key={i} className="p-4 flex gap-3">
              <span className="font-bold w-8 shrink-0" style={{ color: "#000" }}>
                {d.speaker}:
              </span>
              <span>{d.line}</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3 className="text-xl mb-3">Tłumaczenie</h3>
        <div className="space-y-2">
          {parsed.translations.map((t, i) => (
            <TranslationItem key={i} pl={t.pl} en={t.en} />
          ))}
        </div>
      </section>

      {parsed.idiom && (
        <section>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xl">Idiom</h3>
            <Button size="sm" variant="outline" onClick={onSaveIdiom}>
              <Plus className="h-4 w-4" /> Zapisz idiom
            </Button>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-baseline gap-3">
              <span className="text-lg font-bold" style={{ color: "#000" }}>
                {parsed.idiom.idiom}
              </span>
              <span>— {parsed.idiom.meaning}</span>
            </div>
            {parsed.idiom.example && (
              <p className="text-sm text-muted-foreground mt-2 italic">{parsed.idiom.example}</p>
            )}
          </div>
        </section>
      )}
    </article>
  );
}

function TranslationItem({ pl, en }: { pl: string; en: string }) {
  const [show, setShow] = useState(false);
  return (
    <div className="rounded-lg border bg-card p-4">
      <p>{pl}</p>
      {show ? (
        <div className="mt-2 flex items-center justify-between gap-3">
          <p className="font-semibold" style={{ color: "#000" }}>
            {en}
          </p>
          <button
            onClick={() => setShow(false)}
            className="text-xs text-muted-foreground inline-flex items-center gap-1"
          >
            <EyeOff className="h-3 w-3" /> ukryj
          </button>
        </div>
      ) : (
        <Button size="sm" variant="outline" className="mt-2" onClick={() => setShow(true)}>
          <Eye className="h-4 w-4" /> Pokaż rozwiązanie
        </Button>
      )}
    </div>
  );
}
