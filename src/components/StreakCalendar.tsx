import { useMemo } from "react";
import type { StreakState } from "@/lib/store";

// GitHub-style contribution grid: last 12 weeks x 7 days.
export function StreakCalendar({ streak }: { streak: StreakState }) {
  const weeks = 12;
  const cells = useMemo(() => {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const days: { key: string; count: number; date: Date }[] = [];
    const total = weeks * 7;
    // Align so the last cell is today.
    for (let i = total - 1; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(now.getDate() - i);
      const key = d.toISOString().slice(0, 10);
      days.push({ key, count: streak.history?.[key] ?? 0, date: d });
    }
    return days;
  }, [streak.history]);

  const cols: typeof cells[] = [];
  for (let w = 0; w < weeks; w++) cols.push(cells.slice(w * 7, w * 7 + 7));

  const level = (n: number) =>
    n === 0
      ? "bg-secondary"
      : n < 5
      ? "bg-green-500/25"
      : n < 15
      ? "bg-green-500/50"
      : n < 30
      ? "bg-green-500/75"
      : "bg-green-600";

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="text-sm font-semibold">Aktywność (12 tygodni)</h3>
        <span className="text-xs text-muted-foreground">
          Streak: {streak.current} · najdłuższy: {streak.longest}
        </span>
      </div>
      <div className="flex gap-1 overflow-x-auto">
        {cols.map((col, i) => (
          <div key={i} className="flex flex-col gap-1">
            {col.map((c) => (
              <div
                key={c.key}
                title={`${c.key}: ${c.count} akcji`}
                className={`h-3 w-3 rounded-sm ${level(c.count)}`}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-2 text-[10px] text-muted-foreground">
        <span>mniej</span>
        <div className="h-2.5 w-2.5 rounded-sm bg-secondary" />
        <div className="h-2.5 w-2.5 rounded-sm bg-green-500/25" />
        <div className="h-2.5 w-2.5 rounded-sm bg-green-500/50" />
        <div className="h-2.5 w-2.5 rounded-sm bg-green-500/75" />
        <div className="h-2.5 w-2.5 rounded-sm bg-green-600" />
        <span>więcej</span>
      </div>
    </div>
  );
}
