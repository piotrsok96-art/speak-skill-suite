
## Co buduję

50 rozbudowanych lekcji B1/B2 (życie codzienne + praca) wbudowanych w aplikację, plus warstwa nauki (SRS, TTS, streak, fiszki) i instrukcja użytkowania.

## Zawartość każdej z 50 lekcji

- 25 słówek (EN + IPA + wymowa fonetyczna PL + tłumaczenie + przykładowe zdanie)
- 5 idiomów (EN + znaczenie PL + przykład)
- 2 dialogi (5–8 wymian, z tłumaczeniem PL)
- 1 sekcja gramatyki (2 zagadnienia, krótkie wyjaśnienie + przykłady)
- Quiz: 10 pytań (mix: tłumaczenie, uzupełnij lukę, wybierz idiom, gramatyka)
- 2–3 dodatkowe paczki ("Załaduj więcej") — extra słówka i extra dialog

Tematy (przykład): Small talk, Job interview, Emails at work, Meetings, Doctor's visit, Travel & airports, Hotel, Renting a flat, Banking, Shopping & returns, Restaurant, Negotiations, Project management, Remote work, Public transport, Family life, Hobbies, Health & gym, Weather & seasons, Tech & gadgets, Social media, Asking for help, Giving feedback, Conflict at work, Career change… (50 w sumie).

## Nowe funkcje nauki

**1. "Znam / Nie znam" przy każdym słówku** — w lekcji i w słowniczku. Trzy stany: `unseen` / `known` / `learning`. "Nie znam" → ląduje w Słowniczku w sekcji "Do powtórki" + w kolejce SRS.

**2. Spaced Repetition (SM-2 light)** — dla słówek `learning`. Nowy widok `/app/srs` "Powtórka dnia": pokazuje słówka zaplanowane na dziś. Po odpowiedzi: Łatwe (×2.5), OK (×2.0), Trudne (×1.3), Nie pamiętam (reset). Następna data = `today + interval days`. Licznik "do powtórki dziś: N" na dashboardzie.

**3. Text-to-Speech (Web Speech API, offline)** — ikonka 🔊 przy słówkach, idiomach i linijkach dialogu. `speechSynthesis.speak(new SpeechSynthesisUtterance(text))` z `lang="en-GB"`. Zero kosztów, zero backendu.

**4. Tryb fiszek** w Słowniczku — przełącznik Tabela / Fiszki. Karta z animacją flip (Tailwind transform), tryb EN→PL i PL→EN, auto-tasowanie, swipe znam/nie znam.

**5. Streak + cel dzienny** — w storze pole `streak: { current, longest, lastActive, dailyGoal:20, todayCount }`. Pasek postępu na dashboardzie ("12/20 słówek dziś • 🔥 5 dni z rzędu"). Codzienne zwiększenie `todayCount` przy każdej akcji nauki; reset o północy lokalnie.

**6. Quiz w każdej lekcji** — przycisk "Sprawdź się" na końcu lekcji uruchamia 10 pytań tej lekcji (osobny od globalnego Quizu Gramatycznego). Wynik zapisany w `lessonProgress[lessonId]`.

**7. "Załaduj więcej przykładów"** — przyciski w sekcjach Słówka / Dialogi / Idiomy. Każda lekcja ma w danych pola `extraVocabPacks[]`, `extraDialogs[]`, `extraIdioms[]` (2–3 paczki). Klik dokleja paczkę do widoku i do bazy użytkownika (jeśli zaznaczy "Zapisz").

**8. Ekran "Jak używać"** — nowa trasa `/app/help` (link w nawigacji + auto-otwarcie po pierwszym wyborze profilu). Krótki przewodnik z 6 kafelków: Wybierz lekcję → Słówka (znam/nie znam) → Posłuchaj wymowy → Quiz → Powtórka SRS → Słowniczek/druk.

## Architektura danych

```
content/lessons/         ← 50 plików .ts z gotowymi lekcjami (statyczny import)
  lesson-01-small-talk.ts
  ...
  lesson-50-...ts
content/index.ts         ← agreguje wszystkie lekcje
src/lib/srs.ts           ← algorytm SM-2 + planowanie powtórek
src/lib/tts.ts           ← wrapper na Web Speech API + fallback
src/lib/streak.ts        ← liczenie dni i celu dziennego
src/components/
  VocabRow.tsx           ← słówko + znam/nie znam + 🔊
  Flashcard.tsx          ← flip card
  SrsReviewCard.tsx
src/routes/
  app.lessons.tsx        ← lista 50 lekcji (filtr poziom/temat, status: nowa/w toku/ukończona)
  app.lessons.$id.tsx    ← widok pojedynczej lekcji
  app.srs.tsx            ← powtórka dnia
  app.help.tsx           ← jak używać
```

Store rozszerzam o: `wordStatus: Record<wordId, 'known'|'learning'>`, `srsQueue: Record<wordId, { dueAt, interval, ease, reps }>`, `streak`, `lessonProgress`. Wszystko leci do Supabase (`profile_data.data` jsonb) tak jak dziś.

## Synchronizacja Supabase

Bez zmian schematu — wszystko mieści się w istniejącym `profile_data.data jsonb`. Lekcje wbudowane (50 plików) NIE lecą do Supabase; tam zapisuję tylko stan użytkownika (`wordStatus`, `srsQueue`, `streak`, `lessonProgress`, custom lekcje wklejone przez użytkownika).

## Treść lekcji — jak zrobię 50 sztuk

Piszę generator buildowy w Node (`scripts/build-lessons.ts`) z szablonami tematycznymi i ręcznie dopracowanymi danymi dla każdego tematu (25 słówek, 5 idiomów, 2 dialogi, gramatyka, quiz). Wynik: 50 plików `.ts` w `content/lessons/`. Treść po angielsku + polskie tłumaczenia i IPA. To NIE jest AI w runtime — wszystko statyczne, sprawdzone, offline.

## Czego NIE robię w tej iteracji

- AI na żywo do generowania nowych przykładów (wybrałeś warianty offline).
- Logowanie / ochrona profili (publiczny dostęp pozostaje).
- Nowe migracje DB.

## Plik z instrukcją

Krótki tekst "Jak używać EnglishLab" w odpowiedzi po zakończeniu + ten sam tekst w `/app/help`.
