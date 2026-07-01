import type { ProfileData, SrsItem } from "@/lib/store";
import { BUILTIN_LESSONS, type BuiltinLesson } from "@/content/lessons";

export interface WeakGrammar {
  topic: string;
  lesson: BuiltinLesson;
  avg: number; // 0-1
}

export interface Insights {
  weakGrammar: WeakGrammar | null;
  hardWords: SrsItem[];
  recommendedLesson: BuiltinLesson | null;
  weakItemsForSrs: SrsItem[];
}

export function computeInsights(data: ProfileData): Insights {
  // Weak grammar: lesson with lowest quiz score, among completed with quiz.
  let worst: WeakGrammar | null = null;
  for (const l of BUILTIN_LESSONS) {
    const p = data.lessonProgress[l.id];
    if (p?.quizScore == null || !p.quizTotal) continue;
    const avg = p.quizScore / p.quizTotal;
    if (avg >= 0.7) continue;
    if (!worst || avg < worst.avg) worst = { topic: l.grammar.title, lesson: l, avg };
  }

  // Hard words: SRS items with low ease, sorted worst first.
  const items = Object.values(data.srs);
  const hardWords = items
    .filter((i) => i.ease < 2.2)
    .sort((a, b) => a.ease - b.ease)
    .slice(0, 8);

  // Recommended lesson: first non-completed lesson.
  const recommendedLesson =
    BUILTIN_LESSONS.find((l) => !data.lessonProgress[l.id]?.completedAt) ?? null;

  // Weak-items set for a focused SRS session.
  const weakItemsForSrs = items
    .filter((i) => i.ease < 2.4)
    .sort((a, b) => a.ease - b.ease)
    .slice(0, 12);

  return { weakGrammar: worst, hardWords, recommendedLesson, weakItemsForSrs };
}
