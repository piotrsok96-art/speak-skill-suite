import { BookOpen, AlertTriangle, Check, X } from "lucide-react";
import { SpeakButton } from "@/components/SpeakButton";
import type { BuiltinGrammar, BuiltinMistake } from "@/content/lessons";

interface Props {
  primary: BuiltinGrammar;
  secondary?: BuiltinGrammar;
  mistakes?: BuiltinMistake[];
}

function GrammarCard({ g, label }: { g: BuiltinGrammar; label?: string }) {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      {label && (
        <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
      )}
      <h3 className="font-semibold text-base" style={{ color: "#000" }}>{g.title}</h3>
      <p className="text-sm whitespace-pre-wrap leading-relaxed">{g.rule}</p>
      {g.forms && g.forms.length > 0 && (
        <div className="rounded-md border bg-secondary/40 overflow-hidden">
          <p className="text-[11px] uppercase tracking-wide text-muted-foreground px-3 pt-2">
            Formy / struktury
          </p>
          <table className="w-full text-xs">
            <tbody>
              {g.forms.map((f, i) => (
                <tr key={i} className="border-t first:border-t-0">
                  <td className="px-3 py-1.5 font-mono font-semibold whitespace-nowrap align-top w-1/3">
                    {f.label}
                  </td>
                  <td className="px-3 py-1.5 align-top">
                    <div>{f.a}</div>
                    {f.b && <div className="text-muted-foreground mt-0.5">{f.b}</div>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="text-[11px] uppercase tracking-wide text-muted-foreground mt-2">Przykłady</p>
      <ul className="space-y-1.5 text-sm">
        {g.examples.map((e, i) => (
          <li key={i} className="flex items-start gap-2">
            <SpeakButton text={e} />
            <span className="font-medium">{e}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}


export function GrammarBlock({ primary, secondary, mistakes }: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl flex items-center gap-2">
        <BookOpen className="h-5 w-5" /> Gramatyka
      </h2>
      <div className="grid gap-3 md:grid-cols-2">
        <GrammarCard g={primary} label="Główne zagadnienie" />
        {secondary && <GrammarCard g={secondary} label="Powtórka pokrewna" />}
      </div>
      {mistakes && mistakes.length > 0 && (
        <div className="rounded-lg border bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900 p-4 space-y-3">
          <h3 className="font-semibold flex items-center gap-2 text-amber-900 dark:text-amber-200">
            <AlertTriangle className="h-4 w-4" /> Częste błędy Polaków
          </h3>
          <ul className="space-y-2.5 text-sm">
            {mistakes.map((m, i) => (
              <li key={i} className="space-y-1">
                <div className="flex items-start gap-2 text-red-700 dark:text-red-400">
                  <X className="h-4 w-4 mt-0.5 shrink-0" />
                  <span className="line-through">{m.wrong}</span>
                </div>
                <div className="flex items-start gap-2 text-green-700 dark:text-green-400">
                  <Check className="h-4 w-4 mt-0.5 shrink-0" />
                  <SpeakButton text={m.right} />
                  <span className="font-medium">{m.right}</span>
                </div>
                <p className="text-xs text-muted-foreground pl-6">{m.note}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
