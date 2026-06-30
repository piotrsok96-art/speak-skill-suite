import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import {
  useActiveProfile,
  useProfileData,
  uid,
  type Word,
  type Idiom,
  type WordStatus,
  type LessonProgress,
} from "@/lib/store";
import { BUILTIN_LESSONS, type BuiltinLesson, type BuiltinVocab, type BuiltinDialog } from "@/content/lessons";
import { VocabRow } from "@/components/VocabRow";
import { SpeakButton } from "@/components/SpeakButton";
import { FillBlank } from "@/components/FillBlank";
import { TranslateBox } from "@/components/TranslateBox";
import { GrammarBlock } from "@/components/GrammarBlock";
import { Scorecard } from "@/components/Scorecard";
import { PreTest } from "@/components/PreTest";
import { Button } from "@/components/ui/button";
import { scheduleNew } from "@/lib/srs";
import { withStreakBump } from "@/lib/streak";
import { toast } from "sonner";
import {
  ArrowLeft,
  Check,
  ChevronRight,
  Plus,
  RotateCcw,
  Sparkles,
  X,
  CheckCircle2,
  Pencil,
  Languages,
  Target,
} from "lucide-react";
import { cn } from "@/lib/utils";


export const Route = createFileRoute("/app/lessons/$id")({
  component: LessonDetail,
});

function LessonDetail() {
  const { id } = Route.useParams();
  const profile = useActiveProfile();
  const [data, update] = useProfileData(profile);
  const navigate = useNavigate();

  const lesson = useMemo<BuiltinLesson | undefined>(
    () => BUILTIN_LESSONS.find((l) => l.id === id),
    [id],
  );

  const [extraVocabShown, setExtraVocabShown] = useState(false);
  const [extraDialogShown, setExtraDialogShown] = useState(false);
  const [extraIdiomsShown, setExtraIdiomsShown] = useState(false);
  const [quizOpen, setQuizOpen] = useState(false);
  const [pretestOpen, setPretestOpen] = useState(false);


  if (!lesson) {
    return (
      <div className="space-y-4">
        <Link to="/app/lessons" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4 mr-1" /> Wróć do listy
        </Link>
        <p>Nie znaleziono lekcji.</p>
      </div>
    );
  }

  const progress = data.lessonProgress[lesson.id];

  // Ensure "started" once the user opens the lesson
  const startedAt = data.lessonProgress[lesson.id]?.startedAt;
  useEffect(() => {
    if (startedAt) return;
    const t = setTimeout(() => {
      update((d) => {
        if (d.lessonProgress[lesson.id]?.startedAt) return d;
        return {
          ...d,
          lessonProgress: {
            ...d.lessonProgress,
            [lesson.id]: { ...d.lessonProgress[lesson.id], startedAt: Date.now() },
          },
        };
      });
    }, 200);
    return () => clearTimeout(t);
  }, [startedAt, lesson.id, update]);

  const markWord = (v: BuiltinVocab, status: WordStatus) => {
    update((d) => {
      const key = wordKey(lesson.id, v.en);
      const wordStatus = { ...d.wordStatus, [key]: status };
      let srs = d.srs;
      if (status === "learning") {
        if (!srs[key]) {
          srs = {
            ...srs,
            [key]: scheduleNew({
              key,
              en: v.en,
              ipa: v.ipa,
              plPron: v.plPron,
              pl: v.pl,
              example: v.example,
              source: lesson.id,
            }),
          };
        }
      } else if (status === "known") {
        if (srs[key]) {
          const next = { ...srs };
          delete next[key];
          srs = next;
        }
      }
      const updated = withStreakBump({ ...d, wordStatus, srs }, 1);
      if (status === "learning") {
        const dueCount = Object.values(updated.srs).filter((s) => s.dueAt <= Date.now() + 86_400_000).length;
        toast.success(`„${v.en}" dodane do powtórek (kolejka: ${dueCount})`, {
          action: { label: "Powtórka", onClick: () => navigate({ to: "/app/srs" }) },
        });
      }
      return updated;
    });
  };

  const markIdiom = (i: { en: string; pl: string; example: string }, status: WordStatus) => {
    update((d) => {
      const key = idiomKey(lesson.id, i.en);
      const wordStatus = { ...d.wordStatus, [key]: status };
      let srs = d.srs;
      if (status === "learning") {
        if (!srs[key]) {
          srs = {
            ...srs,
            [key]: scheduleNew({
              key,
              en: i.en,
              ipa: "",
              plPron: "",
              pl: i.pl,
              example: i.example,
              source: lesson.id,
            }),
          };
        }
      } else if (status === "known" && srs[key]) {
        const next = { ...srs };
        delete next[key];
        srs = next;
      }
      const updated = withStreakBump({ ...d, wordStatus, srs }, 1);
      if (status === "learning") {
        const dueCount = Object.values(updated.srs).filter((s) => s.dueAt <= Date.now() + 86_400_000).length;
        toast.success(`Idiom „${i.en}" dodany do powtórek (kolejka: ${dueCount})`, {
          action: { label: "Powtórka", onClick: () => navigate({ to: "/app/srs" }) },
        });
      }
      return updated;
    });
  };


  const saveAllVocab = () => {
    const vocab = [...lesson.vocab, ...(extraVocabShown ? lesson.extraVocab : [])];
    update((d) => {
      const existing = new Set(d.words.map((w) => w.word.toLowerCase()));
      const newWords: Word[] = vocab
        .filter((v) => !existing.has(v.en.toLowerCase()))
        .map((v) => ({
          id: uid(),
          word: v.en,
          ipa: v.ipa,
          pronouncePl: v.plPron,
          meaning: v.pl,
          example: v.example,
          addedAt: Date.now(),
          box: 1,
          nextReview: Date.now(),
        }));
      return {
        ...d,
        words: [...d.words, ...newWords],
        lessonProgress: {
          ...d.lessonProgress,
          [lesson.id]: { ...d.lessonProgress[lesson.id], savedVocab: true },
        },
      };
    });
    toast.success(`Zapisano ${vocab.length} słówek do bazy`);
  };

  const saveAllIdioms = () => {
    const idioms = [...lesson.idioms, ...(extraIdiomsShown ? lesson.extraIdioms : [])];
    update((d) => {
      const existing = new Set(d.idioms.map((i) => i.idiom.toLowerCase()));
      const next: Idiom[] = idioms
        .filter((i) => !existing.has(i.en.toLowerCase()))
        .map((i) => ({
          id: uid(),
          idiom: i.en,
          meaning: i.pl,
          example: i.example,
          addedAt: Date.now(),
        }));
      return {
        ...d,
        idioms: [...d.idioms, ...next],
        lessonProgress: {
          ...d.lessonProgress,
          [lesson.id]: { ...d.lessonProgress[lesson.id], savedIdioms: true },
        },
      };
    });
    toast.success(`Zapisano ${idioms.length} idiomów do bazy`);
  };

  const completeLesson = (score?: { correct: number; total: number }) => {
    update((d) => {
      const prev = d.lessonProgress[lesson.id] ?? {};
      return withStreakBump(
        {
          ...d,
          lessonProgress: {
            ...d.lessonProgress,
            [lesson.id]: {
              ...prev,
              startedAt: prev.startedAt ?? Date.now(),
              completedAt: Date.now(),
              quizScore: score?.correct ?? prev.quizScore,
              quizTotal: score?.total ?? prev.quizTotal,
            },
          },
          lessons: d.lessons.some((l) => l.id === lesson.id)
            ? d.lessons
            : [
                ...d.lessons,
                {
                  id: lesson.id,
                  topic: lesson.topic,
                  level: lesson.level,
                  completedAt: Date.now(),
                },
              ],
          results: score
            ? [
                ...d.results,
                {
                  id: uid(),
                  type: "lesson",
                  score: score.correct,
                  total: score.total,
                  at: Date.now(),
                  lessonId: lesson.id,
                },
              ]
            : d.results,
        },
        2,
      );
    });
    toast.success("Lekcja oznaczona jako ukończona");
  };

  const resetLesson = () => {
    if (typeof window !== "undefined" && !window.confirm("Zresetować całą lekcję? Usuniemy postęp, status słówek z tej lekcji i powtórki z niej dodane.")) return;
    update((d) => {
      const lessonPrefix = `${lesson.id}::`;
      const idiomPrefix = `idiom::${lesson.id}::`;
      const wordStatus = { ...d.wordStatus };
      for (const k of Object.keys(wordStatus)) {
        if (k.startsWith(lessonPrefix) || k.startsWith(idiomPrefix)) delete wordStatus[k];
      }
      const srs = { ...d.srs };
      for (const k of Object.keys(srs)) {
        if (srs[k].source === lesson.id) delete srs[k];
      }
      const lessonProgress = { ...d.lessonProgress };
      delete lessonProgress[lesson.id];
      return {
        ...d,
        wordStatus,
        srs,
        lessonProgress,
        lessons: d.lessons.filter((l) => l.id !== lesson.id),
        results: d.results.filter((r) => r.lessonId !== lesson.id),
      };
    });
    setQuizOpen(false);
    setPretestOpen(false);
    setExtraVocabShown(false);
    setExtraDialogShown(false);
    setExtraIdiomsShown(false);
    toast.success("Lekcja zresetowana — możesz zacząć od nowa.");
  };

  const recordScore = (patch: Partial<LessonProgress>) => {
    update((d) => {
      const prev = d.lessonProgress[lesson.id] ?? {};
      return withStreakBump(
        {
          ...d,
          lessonProgress: {
            ...d.lessonProgress,
            [lesson.id]: { ...prev, startedAt: prev.startedAt ?? Date.now(), ...patch },
          },
        },
        1,
      );
    });
  };

  const allVocab = [...lesson.vocab, ...(extraVocabShown ? lesson.extraVocab : [])];
  const allIdioms = [...lesson.idioms, ...(extraIdiomsShown ? lesson.extraIdioms : [])];

  const pretestQs = useMemo(() => lesson.pretest ?? lesson.quiz.slice(0, 5), [lesson]);

  return (
    <article className="space-y-8">
      <div className="flex items-center justify-between">
        <Link
          to="/app/lessons"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" /> Lista lekcji
        </Link>
        {progress?.completedAt && (
          <span className="inline-flex items-center gap-1 text-sm text-green-600">
            <CheckCircle2 className="h-4 w-4" /> Ukończona
          </span>
        )}
      </div>

      <header className="border-b pb-4">
        <p className="text-sm text-muted-foreground">
          Poziom {lesson.level} · Lekcja {lesson.number}/50
        </p>
        <h1 className="text-3xl md:text-4xl mt-1" style={{ color: "#000" }}>
          {lesson.topic}
        </h1>
        <p className="text-sm text-muted-foreground mt-2">{lesson.summary}</p>
      </header>

      {/* PRE-TEST */}
      <section className="rounded-xl border bg-card p-5">
        <div className="flex items-center justify-between gap-3 flex-wrap mb-3">
          <div>
            <h2 className="text-xl flex items-center gap-2">
              <Target className="h-5 w-5" /> Test wejściowy
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              5 szybkich pytań — sprawdź, czy potrzebujesz tej lekcji.{" "}
              {progress?.pretestScore != null && (
                <span className="text-foreground font-medium">
                  Twój wynik: {progress.pretestScore}/{progress.pretestTotal}
                </span>
              )}
            </p>
          </div>
          {!pretestOpen && (
            <Button variant="outline" onClick={() => setPretestOpen(true)}>
              {progress?.pretestScore != null ? "Powtórz pre-test" : "Rozpocznij"}
            </Button>
          )}
        </div>
        {pretestOpen && (
          <PreTest
            key={`pre-${lesson.id}`}
            questions={pretestQs}
            onFinish={(correct, total) => {
              recordScore({ pretestScore: correct, pretestTotal: total });
              if (correct / total >= 0.8) {
                toast.success("Świetnie! Możesz tylko przejrzeć materiał i przejść do quizu końcowego.");
              }
            }}
          />
        )}
      </section>

      {/* GRAMMAR + MISTAKES */}
      <section>
        <GrammarBlock
          primary={lesson.grammar}
          secondary={lesson.secondaryGrammar}
          mistakes={lesson.commonMistakes}
        />
      </section>

      <section>
        <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
          <h2 className="text-xl">Słówka ({allVocab.length})</h2>
          <Button size="sm" onClick={saveAllVocab}>
            <Plus className="h-4 w-4" /> Zapisz wszystkie do bazy
          </Button>
        </div>
        <div className="space-y-2">
          {allVocab.map((v) => {
            const key = wordKey(lesson.id, v.en);
            return (
              <VocabRow
                key={key}
                item={{
                  key,
                  en: v.en,
                  ipa: v.ipa,
                  plPron: v.plPron,
                  pl: v.pl,
                  example: v.example,
                }}
                status={data.wordStatus[key]}
                onMark={(s) => markWord(v, s)}
              />
            );
          })}
        </div>
        {!extraVocabShown && (
          <Button
            variant="outline"
            className="mt-3 w-full"
            onClick={() => setExtraVocabShown(true)}
          >
            <Plus className="h-4 w-4" /> Załaduj kolejne 10 przykładów
          </Button>
        )}
      </section>

      <section>
        <h2 className="text-xl mb-3">Dialog</h2>
        <DialogView dialog={lesson.dialogs[0]} />
        <details className="mt-3 rounded-lg border bg-card">
          <summary className="cursor-pointer px-4 py-2 text-sm font-medium select-none">
            Drugi dialog (kliknij, by rozwinąć)
          </summary>
          <div className="p-4 pt-0">
            <DialogView dialog={lesson.dialogs[1]} />
          </div>
        </details>
        {!extraDialogShown ? (
          <Button
            variant="outline"
            className="mt-3 w-full"
            onClick={() => setExtraDialogShown(true)}
          >
            <Plus className="h-4 w-4" /> Załaduj dodatkowy dialog
          </Button>
        ) : (
          <div className="mt-3">
            <p className="text-sm text-muted-foreground mb-2">Dodatkowy dialog:</p>
            <DialogView dialog={lesson.extraDialog} />
          </div>
        )}
      </section>

      <section>
        <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
          <h2 className="text-xl">Idiomy ({allIdioms.length})</h2>
          <Button size="sm" variant="outline" onClick={saveAllIdioms}>
            <Plus className="h-4 w-4" /> Zapisz idiomy
          </Button>
        </div>
        <div className="space-y-2">
          {allIdioms.map((i, idx) => {
            const ikey = idiomKey(lesson.id, i.en);
            const status = data.wordStatus[ikey];
            return (
              <div
                key={idx}
                className={cn(
                  "rounded-lg border p-3 transition-colors",
                  status === "known" && "border-green-500/40 bg-green-500/5",
                  status === "learning" && "border-amber-500/40 bg-amber-500/5",
                  !status && "bg-card",
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2 flex-wrap">
                      <SpeakButton text={i.en} />
                      <span className="font-bold" style={{ color: "#000" }}>
                        {i.en}
                      </span>
                      <span className="text-sm">— {i.pl}</span>
                    </div>
                    {i.example && (
                      <p className="text-sm text-muted-foreground italic mt-1">{i.example}</p>
                    )}
                  </div>
                  <div className="flex flex-col gap-1 shrink-0">
                    <button
                      onClick={() => markIdiom(i, "known")}
                      className={cn(
                        "inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium transition-colors",
                        status === "known"
                          ? "bg-green-600 text-white border-green-600"
                          : "hover:bg-green-500/10 hover:border-green-500/40 text-muted-foreground",
                      )}
                    >
                      <Check className="h-3 w-3" /> Znam
                    </button>
                    <button
                      onClick={() => markIdiom(i, "learning")}
                      className={cn(
                        "inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium transition-colors",
                        status === "learning"
                          ? "bg-amber-500 text-white border-amber-500"
                          : "hover:bg-amber-500/10 hover:border-amber-500/40 text-muted-foreground",
                      )}
                    >
                      <X className="h-3 w-3" /> Nie znam
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        {!extraIdiomsShown && (
          <Button
            variant="outline"
            className="mt-3 w-full"
            onClick={() => setExtraIdiomsShown(true)}
          >
            <Plus className="h-4 w-4" /> Załaduj kolejne 2 idiomy
          </Button>
        )}
      </section>

      {/* FILL-IN-THE-BLANK */}
      {lesson.fillBlanks?.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
            <h2 className="text-xl flex items-center gap-2">
              <Pencil className="h-5 w-5" /> Uzupełnij luki
            </h2>
            {progress?.fillCorrect != null && (
              <span className="text-sm text-muted-foreground">
                Ostatnio: {progress.fillCorrect}/{progress.fillTotal}
              </span>
            )}
          </div>
          <FillBlank
            key={`fill-${lesson.id}`}
            items={lesson.fillBlanks}
            onFinish={(correct, total) => recordScore({ fillCorrect: correct, fillTotal: total })}
          />
        </section>
      )}

      {/* TRANSLATIONS PL→EN */}
      {lesson.translations?.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
            <h2 className="text-xl flex items-center gap-2">
              <Languages className="h-5 w-5" /> Tłumaczenia PL→EN
            </h2>
            {progress?.transCorrect != null && (
              <span className="text-sm text-muted-foreground">
                Ostatnio: {progress.transCorrect}/{progress.transTotal}
              </span>
            )}
          </div>
          <TranslateBox
            key={`trans-${lesson.id}`}
            items={lesson.translations}
            onFinish={(correct, total) => recordScore({ transCorrect: correct, transTotal: total })}
          />
        </section>
      )}

      {/* SCORECARD */}
      <Scorecard progress={progress} />

      {/* QUIZ */}
      <section className="rounded-xl border bg-card p-5">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <h2 className="text-xl flex items-center gap-2">
              <Sparkles className="h-5 w-5" /> Quiz końcowy (post-test)
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              10 pytań: słówka, idiomy, gramatyka.{" "}
              {progress?.quizScore != null && (
                <span className="text-foreground font-medium">
                  Poprzedni wynik: {progress.quizScore}/{progress.quizTotal}
                </span>
              )}
            </p>
          </div>
          <Button size="lg" onClick={() => setQuizOpen((v) => !v)}>
            {quizOpen ? "Schowaj quiz" : "Sprawdź się"}
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {quizOpen && (
          <LessonQuiz
            key={lesson.id}
            lesson={lesson}
            onFinish={(score) => {
              completeLesson(score);
              setQuizOpen(false);
              navigate({ to: "/app/lessons" });
            }}
          />
        )}
      </section>

      {!progress?.completedAt && (
        <div className="flex justify-end">
          <Button variant="outline" onClick={() => completeLesson()}>
            <Check className="h-4 w-4" /> Oznacz jako ukończoną bez quizu
          </Button>
        </div>
      )}
    </article>
  );

}

function wordKey(lessonId: string, en: string): string {
  return `${lessonId}::${en.toLowerCase()}`;
}

function idiomKey(lessonId: string, en: string): string {
  return `idiom::${lessonId}::${en.toLowerCase()}`;
}


function DialogView({ dialog }: { dialog: BuiltinDialog }) {
  return (
    <div className="rounded-lg border bg-card divide-y">
      {dialog.lines.map((l, i) => (
        <div key={i} className="p-3 flex gap-3 items-start">
          <span className="font-bold w-20 shrink-0 text-sm" style={{ color: "#000" }}>
            {l.speaker}:
          </span>
          <div className="flex-1 min-w-0 space-y-0.5">
            <div className="flex items-start gap-2">
              <SpeakButton text={l.en} />
              <span className="text-sm">{l.en}</span>
            </div>
            <p className="text-xs text-muted-foreground italic pl-7">{l.pl}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function LessonQuiz({
  lesson,
  onFinish,
}: {
  lesson: BuiltinLesson;
  onFinish: (score: { correct: number; total: number }) => void;
}) {
  const [idx, setIdx] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const q = lesson.quiz[idx];

  if (!q) {
    return (
      <div className="mt-4 text-center py-6">
        <p className="text-2xl font-bold" style={{ color: "#000" }}>
          {correctCount} / {lesson.quiz.length}
        </p>
        <p className="text-sm text-muted-foreground mt-1">Świetnie!</p>
        <Button
          className="mt-4"
          onClick={() => onFinish({ correct: correctCount, total: lesson.quiz.length })}
        >
          Zapisz wynik i zakończ
        </Button>
      </div>
    );
  }

  const isCorrect = picked === q.correct;

  return (
    <div className="mt-5 space-y-3">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Pytanie {idx + 1} z {lesson.quiz.length}
        </span>
        <span>Wynik: {correctCount}</span>
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
                if (i === q.correct) setCorrectCount((c) => c + 1);
              }}
              className={cn(
                "rounded-lg border px-3 py-2 text-left text-sm transition-colors",
                picked == null && "hover:bg-secondary",
                showCorrect && "border-green-500 bg-green-500/10 text-green-700 dark:text-green-400",
                showWrong && "border-red-500 bg-red-500/10 text-red-700 dark:text-red-400",
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
        <div className="rounded-lg bg-secondary p-3 text-sm">
          <p>
            <strong>{isCorrect ? "Dobrze!" : "Spróbuj zapamiętać."}</strong> {q.explain}
          </p>
          <Button
            size="sm"
            className="mt-2"
            onClick={() => {
              setPicked(null);
              setIdx((i) => i + 1);
            }}
          >
            {idx + 1 === lesson.quiz.length ? "Zobacz wynik" : "Dalej"}{" "}
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
