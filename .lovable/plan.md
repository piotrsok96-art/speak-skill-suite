## Cel

Odpowiedź na 6 punktów: naturalna mowa, ocena CEFR, losowe quizy z tasowaniem, bogate wykresy postępów, aktywne przypominanie PL→EN, adaptacyjny silnik używający zebranych danych.

---

### 1. Naturalna mowa (ElevenLabs TTS)

- Podłączam konektor **ElevenLabs** (`ELEVENLABS_API_KEY`) — wysokiej jakości głosy neuronowe (Sarah, George, Charlie).
- Nowa trasa `src/routes/api/public/tts.ts` (server route) — proxy do ElevenLabs, zwraca MP3 (streaming). Cache w `sessionStorage` po hashu tekstu, by nie generować dwa razy tego samego.
- `src/lib/tts.ts` — nowa funkcja `speakNatural(text, voice?)`: pobiera MP3 z endpointu i odtwarza przez `Audio`. Fallback do Web Speech API gdy fetch padnie (offline / brak kredytów).
- W ustawieniach profilu (sidebar) przełącznik **Głos: naturalny / systemowy** + wybór głosu (British male / female / American).
- `SpeakButton` używa `speakNatural`. Loader spinner podczas fetch.

### 2. Ocena poziomu CEFR

- Nowy komponent `src/components/CefrEstimator.tsx` — liczy poziom na podstawie:
  - średniej z quizów końcowych (waga 40%)
  - liczby ukończonych lekcji vs pula (25%)
  - % słówek "znam" spośród spotkanych (20%)
  - jakości SRS: średni `ease` i `reps` (15%)
- Progi: <30% = A2, 30-55% = B1, 55-80% = B1+/B2, >80% = B2+/C1.
- Widoczne jako karta "Twój szacowany poziom" na `/app/progress` oraz na dashboardzie `/app/index`.
- Dodatkowo pokazuje "punkty do następnego poziomu" (co należy zrobić).

### 3. Losowe quizy + tasowanie

Refaktor generowania quizów, tak by za każdym otwarciem lekcji były inne:
- `src/lib/quiz-gen.ts` — nowy helper `buildLessonQuiz(lesson, seed)`:
  - Losowe 12 pytań z pełnej puli: 6 słówek (spośród 25 głównych + extra), 5 gramatycznych (spośród 6 pytań GRAMMAR_QUIZ_POOL na temat), 1 idiom.
  - Każde pytanie: tasowanie opcji (`shuffle`) i losowe generowanie dystraktorów słówkowych z całej lekcji.
  - Seed = `Date.now()` przy starcie quizu → `Powtórz z innym zestawem`.
- Analogicznie `buildPreTest(lesson)` — 6 innych pytań, non-overlap kontrolowany przez seed.
- `src/routes/app.lessons.$id.tsx` — użyj `useMemo` z `quizSeed` z `useState`; przycisk "Losuj nowy" ponownie tasuje.

### 4. Wykresy postępu

Instaluję `recharts` (już jest w shadcn `chart.tsx`) — używam istniejącej integracji.
Rozbudowa `src/routes/app.progress.tsx`:
- **Kalendarz streak** (`StreakCalendar.tsx`) — grid 12 tygodni × 7 dni w stylu GitHub contributions, kolor zależny od `todayCount` z historii (nowe pole `streakHistory: Record<'YYYY-MM-DD', number>` w `StreakState`).
- **Wykres liniowy** — punkty z ostatnich 30 wyników quizów (`data.results`).
- **Radar umiejętności** (`SkillRadar.tsx`) — 5 osi: Słownictwo, Gramatyka, Rozumienie, Idiomy, Powtórki (SRS ease). Wartości 0-100 wyliczane z danych.
- **Bar chart** — pokrycie 20 zagadnień gramatycznych (średni wynik quizów per topic).

### 5. PL→EN (produktywne)

- W SRS: nowy tryb `mode: 'produce'` — wyświetla PL, użytkownik pisze EN (fuzzy match: normalizacja, tolerancja literówek Levenshtein ≤ 2).
- `src/routes/app.srs.tsx` — mieszanka trybów: 40% flash, 20% choice, 20% type EN, 20% **type PL→EN (produce)**.
- Nowy komponent `ProduceCard.tsx` — pokazuje polskie tłumaczenie + wskazówki (pierwsza litera, liczba liter), pole tekstowe, sprawdzenie z podświetleniem różnic.
- W lekcji: w sekcji Słówka drugi tryb fiszek "PL→EN" (przycisk toggle).
- Statystyki oddzielne dla trybu produce → wpływa na radar (skala "Aktywne użycie").

### 6. Silnik adaptacyjny

- `src/lib/insights.ts` — nowy moduł: `computeInsights(data)` zwraca:
  - **Słabe zagadnienia gramatyczne** (topic z najniższą średnią quizową).
  - **Trudne słówka** (te z niskim `ease` w SRS lub wielokrotnie oblane produce).
  - **Rekomendowana lekcja** — nieskończona lekcja pokrywająca najsłabszy topic.
  - **"Tryb słabych punktów"** — sesja SRS ograniczona do items z ease < 2.0.
- Nowa sekcja na dashboardzie `/app/index`: karty "Twoja słaba strona: Present Perfect →", "5 słówek do dopracowania →", "Polecane: Lekcja 23 →".
- W SRS: przycisk **"Trenuj słabe punkty (12 items)"**.
- W lekcji: jeśli pretestScore ≥ 80%, banner "Znasz to — pomiń do quizu?".

---

### Kolejność implementacji

1. TTS ElevenLabs (konektor + endpoint + integracja) — pkt 1
2. Losowe quizy + PL→EN produce (nowe komponenty) — pkt 3, 5
3. Insights + adaptive suggestions — pkt 6
4. CefrEstimator + rozbudowa progress z wykresami/kalendarzem/radarem — pkt 2, 4

### Uwagi techniczne

- `streakHistory` wymaga migracji danych w `normalize()` (backward compat — pusty domyślny obiekt).
- `recharts` już jest w projekcie (shadcn chart).
- Fuzzy match dla PL→EN: prosta implementacja Levenshteina w `src/lib/fuzzy.ts`.
- ElevenLabs — cache MP3 blobs w IndexedDB (kluczem hash SHA1 tekstu+voice), by nie palić kredytów.
- Wszystko po stronie klienta korzysta z `useProfileData`, więc auto-sync do chmury działa bez zmian.

Czy zatwierdzasz? Mogę też okroić zakres, jeśli wolisz zacząć od 2-3 najważniejszych punktów.