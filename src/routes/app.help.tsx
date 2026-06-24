import { createFileRoute, Link } from "@tanstack/react-router";
import {
  BookOpen,
  Volume2,
  Check,
  Repeat2,
  Library,
  Printer,
  Flame,
} from "lucide-react";

export const Route = createFileRoute("/app/help")({
  component: HelpPage,
});

const STEPS = [
  {
    icon: BookOpen,
    title: "1. Wybierz lekcję",
    body: "W zakładce Lekcje masz 50 gotowych lekcji B1/B2 (życie codzienne i praca). Każda zawiera 25 słówek, 5 idiomów, 2 dialogi, gramatykę i 10-pytaniowy quiz.",
  },
  {
    icon: Check,
    title: "2. Oznacz słówka „Znam / Nie znam\"",
    body: "Przy każdym słówku masz dwa przyciski. „Nie znam\" wrzuca słowo do kolejki Powtórki Dnia (SRS). „Znam\" usuwa je z kolejki.",
  },
  {
    icon: Volume2,
    title: "3. Posłuchaj wymowy",
    body: "Ikonka głośnika przy słówkach, idiomach i linijkach dialogu czyta tekst na głos (Web Speech API — bez internetu, bez kosztów).",
  },
  {
    icon: Check,
    title: "4. Sprawdź się quizem",
    body: "Na końcu każdej lekcji kliknij „Sprawdź się\" — 10 pytań mixujących słówka, idiomy i gramatykę. Wynik zapisuje się do statystyk.",
  },
  {
    icon: Repeat2,
    title: "5. Powtórka dnia (SRS)",
    body: "W zakładce Powtórka system pokazuje słówka zaplanowane na dziś według algorytmu SM-2. Oceń: Nie pamiętam / Trudne / OK / Łatwe — kolejna data sama się ustawi.",
  },
  {
    icon: Flame,
    title: "6. Streak i cel dzienny",
    body: "Każde zaznaczenie znam/nie znam i każda powtórka zwiększają licznik dnia. Trzymaj streak żeby budować nawyk!",
  },
  {
    icon: Library,
    title: "7. Mój słowniczek + fiszki",
    body: "Cała zapisana baza słówek i idiomów jest w Słowniczku. Możesz przełączyć widok na tryb fiszek (flip card) lub wydrukować przyciskiem Drukuj.",
  },
  {
    icon: Printer,
    title: "8. Druk",
    body: "Przy drukowaniu nawigacja jest ukryta — drukujesz czystą tabelę słownika.",
  },
];

function HelpPage() {
  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm text-muted-foreground">Przewodnik</p>
        <h1 className="text-3xl md:text-4xl mt-1">Jak używać EnglishLab</h1>
        <p className="text-sm text-muted-foreground mt-2">
          8 kroków, dzięki którym wyciśniesz z aplikacji maksimum.
        </p>
      </header>

      <div className="grid sm:grid-cols-2 gap-3">
        {STEPS.map(({ icon: Icon, title, body }, i) => (
          <div key={i} className="rounded-xl border bg-card p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
                <Icon className="h-4 w-4" />
              </span>
              <h3 className="font-semibold" style={{ color: "#000" }}>
                {title}
              </h3>
            </div>
            <p className="text-sm text-muted-foreground">{body}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border bg-card p-5">
        <h2 className="text-lg font-semibold mb-2" style={{ color: "#000" }}>
          Pro tip
        </h2>
        <p className="text-sm text-muted-foreground">
          Codziennie: 1 nowa lekcja (15–20 min) + powtórka dnia (5–10 min). Po dwóch tygodniach
          masz solidny grunt z 200+ słówek aktywnie powtarzanych.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Link
          to="/app/lessons"
          className="inline-flex items-center gap-2 rounded-lg bg-foreground text-background px-4 py-2 text-sm font-medium"
        >
          Przejdź do lekcji →
        </Link>
        <Link
          to="/app/srs"
          className="inline-flex items-center gap-2 rounded-lg border bg-card px-4 py-2 text-sm font-medium"
        >
          Powtórka dnia
        </Link>
      </div>
    </div>
  );
}
