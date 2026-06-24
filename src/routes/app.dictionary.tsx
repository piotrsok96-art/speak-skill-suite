import { createFileRoute } from "@tanstack/react-router";
import { useActiveProfile, useProfileData } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Printer } from "lucide-react";

export const Route = createFileRoute("/app/dictionary")({
  component: Dictionary,
});

function Dictionary() {
  const profile = useActiveProfile();
  const [data] = useProfileData(profile);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Twoja baza</p>
          <h1 className="text-3xl mt-1">Mój Słowniczek</h1>
        </div>
        <Button variant="outline" onClick={() => window.print()} className="no-print">
          <Printer className="h-4 w-4" /> Drukuj
        </Button>
      </div>

      <section>
        <h2 className="text-xl mb-3">Słówka ({data.words.length})</h2>
        {data.words.length === 0 ? (
          <p className="text-muted-foreground">Brak zapisanych słówek.</p>
        ) : (
          <div className="rounded-lg border overflow-hidden bg-card">
            <table className="w-full text-sm">
              <thead className="bg-secondary">
                <tr>
                  <th className="text-left px-4 py-2 font-semibold">Słówko</th>
                  <th className="text-left px-4 py-2 font-semibold">Wymowa IPA</th>
                  <th className="text-left px-4 py-2 font-semibold">Wymowa PL</th>
                  <th className="text-left px-4 py-2 font-semibold">Znaczenie</th>
                </tr>
              </thead>
              <tbody>
                {data.words.map((w) => (
                  <tr key={w.id} className="border-t">
                    <td className="px-4 py-2 font-bold" style={{ color: "#000" }}>
                      {w.word}
                    </td>
                    <td className="px-4 py-2 text-muted-foreground font-mono">{w.ipa}</td>
                    <td className="px-4 py-2 text-muted-foreground">{w.pronouncePl}</td>
                    <td className="px-4 py-2">{w.meaning}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-xl mb-3">Idiomy ({data.idioms.length})</h2>
        {data.idioms.length === 0 ? (
          <p className="text-muted-foreground">Brak zapisanych idiomów.</p>
        ) : (
          <div className="rounded-lg border overflow-hidden bg-card">
            <table className="w-full text-sm">
              <thead className="bg-secondary">
                <tr>
                  <th className="text-left px-4 py-2 font-semibold">Idiom</th>
                  <th className="text-left px-4 py-2 font-semibold">Znaczenie</th>
                  <th className="text-left px-4 py-2 font-semibold">Przykład</th>
                </tr>
              </thead>
              <tbody>
                {data.idioms.map((i) => (
                  <tr key={i.id} className="border-t">
                    <td className="px-4 py-2 font-bold" style={{ color: "#000" }}>
                      {i.idiom}
                    </td>
                    <td className="px-4 py-2">{i.meaning}</td>
                    <td className="px-4 py-2 text-muted-foreground italic">{i.example}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
