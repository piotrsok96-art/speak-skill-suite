import type { ProfileData, StreakState } from "./store";
import { todayKey } from "./srs";

function yesterdayOf(day: string): string {
  const d = new Date(day + "T00:00:00");
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

/** Call when the user performs a learning action. Returns new streak state. */
export function bumpStreak(prev: StreakState, increment = 1): StreakState {
  const today = todayKey();
  const s: StreakState = { ...prev, history: { ...(prev.history ?? {}) } };

  // Reset daily counter if new day
  if (s.todayDay !== today) {
    s.todayDay = today;
    s.todayCount = 0;
  }

  s.todayCount += increment;
  s.history[today] = (s.history[today] ?? 0) + increment;

  // Update streak only the first time today
  if (s.lastActiveDay !== today) {
    if (s.lastActiveDay === yesterdayOf(today)) {
      s.current = (s.current || 0) + 1;
    } else {
      s.current = 1;
    }
    s.lastActiveDay = today;
    if (s.current > (s.longest || 0)) s.longest = s.current;
  }

  return s;
}

export function withStreakBump(d: ProfileData, n = 1): ProfileData {
  return { ...d, streak: bumpStreak(d.streak, n) };
}

export function ensureToday(s: StreakState): StreakState {
  const today = todayKey();
  if (s.todayDay !== today) return { ...s, todayDay: today, todayCount: 0 };
  return s;
}
