// Simplified SM-2 spaced repetition.
// Grades: 0 = forgot, 1 = hard, 2 = ok, 3 = easy.
import type { SrsItem } from "./store";

const DAY_MS = 86_400_000;

export function startOfDay(ts = Date.now()): number {
  const d = new Date(ts);
  d.setHours(0, 0, 0, 0);
  return d.getTime();
}

export function todayKey(ts = Date.now()): string {
  return new Date(ts).toISOString().slice(0, 10);
}

export function scheduleNew(
  partial: Omit<SrsItem, "dueAt" | "intervalDays" | "ease" | "reps" | "addedAt">,
): SrsItem {
  return {
    ...partial,
    addedAt: Date.now(),
    reps: 0,
    ease: 2.5,
    intervalDays: 0,
    // due immediately so the user can start practicing today
    dueAt: Date.now(),
  };
}

export function reviewItem(item: SrsItem, grade: 0 | 1 | 2 | 3): SrsItem {
  let { ease, intervalDays, reps } = item;
  if (grade === 0) {
    reps = 0;
    intervalDays = 1;
    ease = Math.max(1.3, ease - 0.2);
  } else {
    reps += 1;
    if (reps === 1) intervalDays = 1;
    else if (reps === 2) intervalDays = 3;
    else intervalDays = Math.round(intervalDays * ease);
    const bump = grade === 1 ? -0.15 : grade === 2 ? 0 : 0.15;
    ease = Math.min(2.8, Math.max(1.3, ease + bump));
  }
  return {
    ...item,
    ease,
    intervalDays,
    reps,
    dueAt: Date.now() + intervalDays * DAY_MS,
  };
}

export function dueToday(srs: Record<string, SrsItem>): SrsItem[] {
  const cutoff = startOfDay() + DAY_MS - 1; // anything due today or earlier
  return Object.values(srs)
    .filter((i) => i.dueAt <= cutoff)
    .sort((a, b) => a.dueAt - b.dueAt);
}

export function countDue(srs: Record<string, SrsItem>): number {
  return dueToday(srs).length;
}
