## Co dodaję (funkcje 1, 2, 5, 12, 14)

Numeracja z poprzedniej listy:

1. **Fill-in-the-blank** — 5 zdań/lekcję z lukami, walidacja, podpowiedź (pierwsza litera).
2. **PL → EN translation** — 5 zdań/lekcję, akceptujemy ≥1 poprawny wariant, normalizacja (case/spacja/interpunkcja), pokaż wzorzec po sprawdzeniu.
5. **Extended Grammar + Common Mistakes** — każda lekcja: 2 zagadnienia gramatyczne z tabelką (forma, użycie, przykłady) + sekcja „Częste błędy Polaków" (3-5 par ❌/✅ z wyjaśnieniem).
12. **Mixed daily review (SRS)** — powtórka dnia miesza typy kart: tłumaczenie EN↔PL, cloze (luka w przykładzie), wybór z 4 opcji. SM-2 nadal steruje harmonogramem.
14. **Pre-test / Post-test** — na wejściu do lekcji krótki test (5 pytań). Wynik ≥80% → propozycja „Pomiń lekcję, oznacz jako opanowaną". Po lekcji post-test + scorecard (poprawa pre vs post).

## Plan implementacji

### Treść (`src/content/lessons.ts` + generator)
- Rozszerzenie typu `Lesson`: `fillBlanks`, `translations`, `grammar[] { topic, explanation, table, examples }`, `commonMistakes[] { wrong, right, note }`, `pretest` (5 pytań — losowane z `quiz`).
- `scripts/gen_lessons.py`: dogeneruj nowe pola dla wszystkich 50 lekcji (paczki szablonowe per topic), regeneruj `lessons.ts`.

### Komponenty (`src/components/`)
- `FillBlank.tsx` — input + walidacja + „pokaż podpowiedź".
- `TranslateBox.tsx` — textarea, akceptuje listę wariantów, normalizacja stringa.
- `GrammarBlock.tsx` — render tabeli + przykładów + sekcji „Częste błędy".
- `Scorecard.tsx` — podsumowanie: % słówek opanowanych, quiz, fill-blank, translation, delta pre→post, czas.
- `MixedReviewCard.tsx` — uniwersalna karta dla SRS (typ: translate / cloze / choice).

### Logika (`src/lib/`)
- `normalize.ts` — `normalizeAnswer(s)` (lower, trim, strip końcowej interpunkcji, podwójne spacje).
- `srs.ts` — `pickReviewMode(item)` (losowanie typu karty na bazie pola, na które user jest słabszy).
- `store.ts` — `LessonProgress` dostaje pola: `pretestScore`, `posttestScore`, `fillBlankResults`, `translationResults`.

### Routes
- `src/routes/app.lessons.$id.tsx` — przebudowa na sekcje: **Pre-test → Słówka → Idiomy → Dialogi → Gramatyka + Częste błędy → Fill-in-the-blank → Tłumaczenie PL→EN → Post-test → Scorecard**. Nawigacja przyciskami „Dalej", progress bar u góry.
- `src/routes/app.srs.tsx` — użycie `MixedReviewCard` zamiast tylko fiszki.

### Bez zmian
- Streak, TTS, słowniczek, store sync.

## Szczegóły techniczne

- **Normalizacja tłumaczeń**: `s.toLowerCase().trim().replace(/[.!?,;:]$/,'').replace(/\s+/g,' ')`. Każde zdanie ma 2-3 warianty docelowe.
- **Pre-test threshold**: 4/5 = pomiń (z confirm dialogiem).
- **Scorecard formuła**: `mastery = 0.4*quiz + 0.3*fillBlank + 0.2*translation + 0.1*vocabKnown`.
- **Mixed SRS**: dla każdego `SrsItem` losujemy 1 z {translate EN→PL, translate PL→EN, cloze z `example`, multiple choice 4 opcji z dystraktorów z innych słów lekcji}. Wynik aktualizuje SM-2 (poprawne = quality 4, błędne = 2).
- **Generator**: szablon zdań per topic (np. „I usually ___ to work" + answer „commute") — 5 fill-blanków i 5 par PL→EN per lekcja, deterministycznie z listy słówek lekcji.

## Zakres
~8-10 nowych plików, edycja 3 routes + store + generator + regeneracja `lessons.ts` (duży plik). Po akceptacji robię wszystko w jednej iteracji.