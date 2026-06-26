import { Trophy, Target, Pencil, Languages, Sparkles } from "lucide-react";
import type { LessonProgress } from "@/lib/store";

interface Props {
  progress: LessonProgress | undefined;
}

function Row({
  icon: Icon,
  label,
  score,
  total,
}: {
  icon: typeof Trophy;
  label: string;
  score?: number;
  total?: number;
}) {
  const has = score != null && total != null && total > 0;
  const pct = has ? Math.round((score / total) * 100) : 0;
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-b-0">
      <Icon className="h-4 w-4 text-muted-foreground shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-sm">{label}</span>
          <span className="text-sm font-semibold" style={{ color: has ? "#000" : undefined }}>
            {has ? `${score}/${total}` : "—"}
          </span>
        </div>
        {has && (
          <div className="mt-1 h-1.5 rounded-full bg-secondary overflow-hidden">
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${pct}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export function Scorecard({ progress }: Props) {
  return (
    <div className="rounded-xl border bg-card p-5 space-y-2">
      <div className="flex items-center gap-2 mb-2">
        <Trophy className="h-5 w-5 text-amber-500" />
        <h2 className="text-lg font-semibold" style={{ color: "#000" }}>
          Twój wynik z lekcji
        </h2>
      </div>
      <Row icon={Target} label="Pre-test (test wejściowy)"
           score={progress?.pretestScore} total={progress?.pretestTotal} />
      <Row icon={Pencil} label="Uzupełnianie luk"
           score={progress?.fillCorrect} total={progress?.fillTotal} />
      <Row icon={Languages} label="Tłumaczenia PL→EN"
           score={progress?.transCorrect} total={progress?.transTotal} />
      <Row icon={Sparkles} label="Quiz końcowy (post-test)"
           score={progress?.quizScore} total={progress?.quizTotal} />
      {!progress?.startedAt && (
        <p className="text-xs text-muted-foreground pt-2">
          Wynik zacznie się pojawiać, gdy wykonasz ćwiczenia powyżej.
        </p>
      )}
    </div>
  );
}
