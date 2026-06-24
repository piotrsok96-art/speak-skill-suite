import { createFileRoute } from "@tanstack/react-router";
import { useActiveProfile, useProfileData } from "@/lib/store";

export const Route = createFileRoute("/app/progress")({
  component: Progress,
});

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-xl border bg-card p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-3xl mt-1 font-bold" style={{ color: "#000" }}>
        {value}
      </p>
    </div>
  );
}

function Progress() {
  const profile = useActiveProfile();
  const [data] = useProfileData(profile);

  const vocabRes = data.results.filter((r) => r.type === "vocab");
  const grammarRes = data.results.filter((r) => r.type === "grammar");
  const avg = (arr: typeof vocabRes) =>
    arr.length ? Math.round((arr.reduce((s, r) => s + r.score / r.total, 0) / arr.length) * 100) : 0;

  return (
    <div className="space-y-8">
      <header>
        <p className="text-sm text-muted-foreground capitalize">Profil: {profile}</p>
        <h1 className="text-3xl mt-1">Postępy</h1>
      </header>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label="Ukończone lekcje" value={data.lessons.length} />
        <Stat label="Słówka w bazie" value={data.words.length} />
        <Stat label="Idiomy" value={data.idioms.length} />
        <Stat label="Quizy ogółem" value={data.results.length} />
        <Stat label="Średni wynik (słówka)" value={`${avg(vocabRes)}%`} />
        <Stat label="Średni wynik (gramatyka)" value={`${avg(grammarRes)}%`} />
      </div>

      <section>
        <h2 className="text-xl mb-3">Ostatnie lekcje</h2>
        {data.lessons.length === 0 ? (
          <p className="text-muted-foreground">Brak ukończonych lekcji.</p>
        ) : (
          <ul className="space-y-2">
            {[...data.lessons].reverse().slice(0, 10).map((l) => (
              <li key={l.id} className="rounded-lg border bg-card p-3 flex justify-between text-sm">
                <span className="font-semibold">{l.topic}</span>
                <span className="text-muted-foreground">
                  {l.level} · {new Date(l.completedAt).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="text-xl mb-3">Ostatnie wyniki</h2>
        {data.results.length === 0 ? (
          <p className="text-muted-foreground">Brak wyników quizów.</p>
        ) : (
          <ul className="space-y-2">
            {[...data.results].reverse().slice(0, 10).map((r) => (
              <li key={r.id} className="rounded-lg border bg-card p-3 flex justify-between text-sm">
                <span className="font-semibold">
                  {r.type === "vocab" ? "Powtórka słówek" : "Quiz gramatyczny"}
                </span>
                <span className="text-muted-foreground">
                  {r.score}/{r.total} · {new Date(r.at).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
