import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { setActiveProfile, type ProfileId, getActiveProfile } from "@/lib/store";
import { BookOpen } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "EnglishLab — Twój notatnik do nauki angielskiego" },
      {
        name: "description",
        content:
          "Interaktywny notatnik, system powtórek i quizy do nauki angielskiego. Wybierz profil i zacznij naukę.",
      },
    ],
  }),
  component: ProfilePick,
});

function ProfilePick() {
  const navigate = useNavigate();

  useEffect(() => {
    if (getActiveProfile()) navigate({ to: "/app/lesson" });
  }, [navigate]);

  const choose = (p: ProfileId) => {
    setActiveProfile(p);
    navigate({ to: "/app/lesson" });
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-12 bg-background">
      <div className="flex items-center gap-2 mb-10">
        <BookOpen className="h-7 w-7" />
        <span className="text-xl font-bold tracking-tight" style={{ color: "#000" }}>
          EnglishLab
        </span>
      </div>
      <h1 className="text-4xl md:text-5xl mb-3 text-center">Wybierz profil</h1>
      <p className="text-muted-foreground mb-10 text-center max-w-md">
        Każdy profil ma własną historię lekcji, słowniczek i wyniki quizów.
      </p>
      <div className="grid sm:grid-cols-2 gap-5 w-full max-w-2xl">
        {(["piotr", "monika"] as ProfileId[]).map((p) => (
          <button
            key={p}
            onClick={() => choose(p)}
            className="group rounded-2xl border bg-card p-8 text-left hover:border-foreground/40 hover:shadow-md transition-all"
          >
            <div className="h-16 w-16 rounded-full bg-secondary flex items-center justify-center text-2xl font-bold mb-5">
              {p[0].toUpperCase()}
            </div>
            <h2 className="text-2xl mb-1 capitalize">{p}</h2>
            <p className="text-sm text-muted-foreground">
              Kontynuuj naukę z profilu <span className="capitalize">{p}</span>
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
