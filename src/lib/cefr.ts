import type { ProfileData } from "@/lib/store";
import { BUILTIN_LESSONS } from "@/content/lessons";

export interface CefrEstimate {
  level: string;
  score: number; // 0-100
  quizAvg: number;
  coverage: number;
  knownRatio: number;
  srsQuality: number;
  nextLevel: string;
  suggestion: string;
}

export function estimateCefr(data: ProfileData): CefrEstimate {
  const total = BUILTIN_LESSONS.length || 50;

  // quiz avg
  let qSum = 0, qCnt = 0;
  for (const l of BUILTIN_LESSONS) {
    const p = data.lessonProgress[l.id];
    if (p?.quizScore != null && p.quizTotal) {
      qSum += p.quizScore / p.quizTotal;
      qCnt++;
    }
  }
  const quizAvg = qCnt ? (qSum / qCnt) * 100 : 0;

  // coverage
  const completed = BUILTIN_LESSONS.filter(
    (l) => data.lessonProgress[l.id]?.completedAt,
  ).length;
  const coverage = (completed / total) * 100;

  // known ratio
  let known = 0, seen = 0;
  for (const [, v] of Object.entries(data.wordStatus)) {
    seen++;
    if (v === "known") known++;
  }
  const knownRatio = seen ? (known / seen) * 100 : 0;

  // SRS quality
  const srsItems = Object.values(data.srs);
  const avgEase =
    srsItems.length > 0
      ? srsItems.reduce((s, i) => s + i.ease, 0) / srsItems.length
      : 2.5;
  const srsQuality = Math.max(0, Math.min(100, ((avgEase - 1.3) / 1.5) * 100));

  const score = Math.round(
    quizAvg * 0.4 + coverage * 0.25 + knownRatio * 0.2 + srsQuality * 0.15,
  );

  let level: string, nextLevel: string, suggestion: string;
  if (score < 20) {
    level = "A2";
    nextLevel = "B1";
    suggestion = "Ukończ pierwsze 5 lekcji i przerób pretesty.";
  } else if (score < 45) {
    level = "B1";
    nextLevel = "B1+";
    suggestion = "Więcej lekcji + regularne powtórki SRS (30/dzień).";
  } else if (score < 65) {
    level = "B1+";
    nextLevel = "B2";
    suggestion = "Skup się na gramatyce i tłumaczeniach PL→EN.";
  } else if (score < 85) {
    level = "B2";
    nextLevel = "B2+";
    suggestion = "Poprawiaj słabe zagadnienia gramatyczne i idiomy.";
  } else {
    level = "B2+/C1";
    nextLevel = "C1";
    suggestion = "Utrzymuj poziom — codzienne powtórki i nowe lekcje.";
  }

  return {
    level,
    score,
    quizAvg: Math.round(quizAvg),
    coverage: Math.round(coverage),
    knownRatio: Math.round(knownRatio),
    srsQuality: Math.round(srsQuality),
    nextLevel,
    suggestion,
  };
}
