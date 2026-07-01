import type { BuiltinLesson, BuiltinQuizQ, BuiltinVocab, BuiltinIdiom } from "@/content/lessons";

// Simple seeded PRNG (Mulberry32).
function mulberry32(seed: number) {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let x = t;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffle<T>(arr: T[], rnd: () => number): T[] {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function shuffleOptions(q: BuiltinQuizQ, rnd: () => number): BuiltinQuizQ {
  const idx = q.options.map((_, i) => i);
  const shuffledIdx = shuffle(idx, rnd);
  const options = shuffledIdx.map((i) => q.options[i]);
  const correct = shuffledIdx.indexOf(q.correct);
  return { ...q, options, correct };
}

function vocabQ(v: BuiltinVocab, pool: BuiltinVocab[], rnd: () => number): BuiltinQuizQ {
  const distractors = shuffle(
    pool.filter((x) => x.en !== v.en && x.pl !== v.pl),
    rnd,
  )
    .slice(0, 3)
    .map((x) => x.pl);
  const options = shuffle([v.pl, ...distractors], rnd);
  return {
    q: `Co oznacza „${v.en}"?`,
    options,
    correct: options.indexOf(v.pl),
    explain: `„${v.en}" = ${v.pl}${v.example ? ` · ${v.example}` : ""}`,
  };
}

function idiomQ(i: BuiltinIdiom, pool: BuiltinIdiom[], rnd: () => number): BuiltinQuizQ {
  const distractors = shuffle(pool.filter((x) => x.en !== i.en), rnd)
    .slice(0, 3)
    .map((x) => x.pl);
  const options = shuffle([i.pl, ...distractors], rnd);
  return {
    q: `Co znaczy idiom „${i.en}"?`,
    options,
    correct: options.indexOf(i.pl),
    explain: `„${i.en}" = ${i.pl}`,
  };
}

/** 12-question mixed quiz: fresh each seed, shuffled options, no repeated items. */
export function buildLessonQuiz(lesson: BuiltinLesson, seed: number): BuiltinQuizQ[] {
  const rnd = mulberry32(seed);
  const vocabPool = [...lesson.vocab, ...lesson.extraVocab];
  const idiomPool = [...lesson.idioms, ...lesson.extraIdioms];

  const vocabPicks = shuffle(vocabPool, rnd).slice(0, 6).map((v) => vocabQ(v, vocabPool, rnd));
  const idiomPicks = shuffle(idiomPool, rnd).slice(0, 1).map((i) => idiomQ(i, idiomPool, rnd));

  // Grammar: pick 5 unique grammar questions from lesson.quiz (rows tagged "Gramatyka").
  const grammarSource = lesson.quiz.filter((q) => q.q.startsWith("Gramatyka"));
  const grammarPicks = shuffle(grammarSource, rnd)
    .slice(0, 5)
    .map((q) => shuffleOptions(q, rnd));

  return shuffle([...vocabPicks, ...grammarPicks, ...idiomPicks], rnd);
}

/** 6-question pretest — different seed so it doesn't overlap with the post-test. */
export function buildPreTest(lesson: BuiltinLesson, seed: number): BuiltinQuizQ[] {
  const rnd = mulberry32(seed ^ 0x9e3779b1);
  const vocabPool = [...lesson.vocab, ...lesson.extraVocab];
  const idiomPool = [...lesson.idioms, ...lesson.extraIdioms];

  const vocabPicks = shuffle(vocabPool, rnd).slice(0, 2).map((v) => vocabQ(v, vocabPool, rnd));
  const idiomPicks = shuffle(idiomPool, rnd).slice(0, 1).map((i) => idiomQ(i, idiomPool, rnd));
  const grammarSource = lesson.quiz.filter((q) => q.q.startsWith("Gramatyka"));
  const grammarPicks = shuffle(grammarSource, rnd).slice(0, 3).map((q) => shuffleOptions(q, rnd));

  return shuffle([...vocabPicks, ...grammarPicks, ...idiomPicks], rnd);
}
