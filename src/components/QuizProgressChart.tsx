import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { QuizResult } from "@/lib/store";

export function QuizProgressChart({ results }: { results: QuizResult[] }) {
  const data = results
    .slice()
    .sort((a, b) => a.at - b.at)
    .slice(-30)
    .map((r, i) => ({
      idx: i + 1,
      pct: r.total ? Math.round((r.score / r.total) * 100) : 0,
      date: new Date(r.at).toLocaleDateString(),
    }));
  return (
    <div className="rounded-xl border bg-card p-5">
      <h3 className="text-sm font-semibold mb-2">Wyniki quizów (ostatnie 30)</h3>
      {data.length === 0 ? (
        <p className="text-sm text-muted-foreground py-8 text-center">
          Brak wyników — zrób pierwszy quiz w lekcji.
        </p>
      ) : (
        <div className="w-full h-48">
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="idx" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip
                formatter={(v: number) => `${v}%`}
                labelFormatter={(l, p) =>
                  p?.[0]?.payload?.date ? `Quiz #${l} · ${p[0].payload.date}` : `Quiz #${l}`
                }
              />
              <Line
                type="monotone"
                dataKey="pct"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
