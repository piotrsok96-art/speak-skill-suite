import type { Word, Idiom, GrammarRule } from "./store";
import { uid } from "./store";

export interface ParsedLesson {
  topic: string;
  level: string;
  grammar: { rules: string; mistakes: string };
  words: Omit<Word, "id" | "addedAt" | "box" | "nextReview">[];
  dialogue: { speaker: string; line: string }[];
  translations: { pl: string; en: string }[];
  idiom: Omit<Idiom, "id" | "addedAt"> | null;
  grammarQuestion: Omit<GrammarRule, "id"> | null;
}

const section = (text: string, name: string): string => {
  const re = new RegExp(`(?:^|\\n)\\s*#+\\s*${name}[^\\n]*\\n([\\s\\S]*?)(?=\\n\\s*#+\\s|$)`, "i");
  const m = text.match(re);
  return m ? m[1].trim() : "";
};

export function parseLesson(raw: string): ParsedLesson {
  const topicMatch = raw.match(/(?:Temat|Topic)\s*:\s*([^\n]+)/i);
  const levelMatch = raw.match(/(?:Poziom|Level)\s*:\s*([^\n]+)/i);

  const grammarBlock = section(raw, "Gramatyka") || section(raw, "Grammar");
  const mistakesBlock = section(raw, "Błędy") || section(raw, "Mistakes");
  const wordsBlock = section(raw, "Słówka") || section(raw, "Vocabulary") || section(raw, "Words");
  const dialogueBlock = section(raw, "Dialog") || section(raw, "Dialogue");
  const translateBlock = section(raw, "Tłumaczenie") || section(raw, "Translation");
  const idiomBlock = section(raw, "Idiom");

  // Words: "word [ipa] (wymowa pl) - meaning. Example: ..."
  const words: ParsedLesson["words"] = [];
  for (const line of wordsBlock.split("\n")) {
    const t = line.replace(/^[-*•\d.\s]+/, "").trim();
    if (!t) continue;
    const m = t.match(
      /^(.+?)\s*(?:\[([^\]]+)\])?\s*(?:\(([^)]+)\))?\s*[-–—:]\s*([^.;]+)(?:[.;]\s*(?:Example|Przykład)\s*:\s*(.+))?$/i,
    );
    if (m) {
      words.push({
        word: m[1].trim(),
        ipa: m[2]?.trim() || "",
        pronouncePl: m[3]?.trim() || "",
        meaning: m[4]?.trim() || "",
        example: m[5]?.trim() || "",
      });
    }
  }

  const dialogue: ParsedLesson["dialogue"] = [];
  for (const line of dialogueBlock.split("\n")) {
    const m = line.match(/^\s*([AB][^:]*?)\s*:\s*(.+)$/);
    if (m) dialogue.push({ speaker: m[1].trim(), line: m[2].trim() });
  }

  const translations: ParsedLesson["translations"] = [];
  const tLines = translateBlock.split("\n").filter((l) => l.trim());
  for (const line of tLines) {
    const t = line.replace(/^[-*•\d.\s]+/, "").trim();
    const m = t.match(/^(.+?)\s*[=→\-]+>?\s*(.+)$/);
    if (m) translations.push({ pl: m[1].trim(), en: m[2].trim() });
  }

  let idiom: ParsedLesson["idiom"] = null;
  if (idiomBlock) {
    const lines = idiomBlock.split("\n").filter((l) => l.trim());
    if (lines.length) {
      const first = lines[0].replace(/^[-*•]\s*/, "");
      const m = first.match(/^(.+?)\s*[-–—:]\s*(.+)$/);
      idiom = {
        idiom: m ? m[1].trim() : first.trim(),
        meaning: m ? m[2].trim() : "",
        example: lines.slice(1).join(" ").replace(/^Example\s*:\s*/i, "").trim(),
      };
    }
  }

  return {
    topic: topicMatch?.[1].trim() || "Lekcja",
    level: levelMatch?.[1].trim() || "B1",
    grammar: { rules: grammarBlock, mistakes: mistakesBlock },
    words,
    dialogue,
    translations,
    idiom,
    grammarQuestion: null,
  };
}

export const SAMPLE_LESSON = `Temat: Daily routines
Poziom: A2

# Gramatyka
Present Simple używamy do opisywania rutyny i nawyków.
Twierdzenie: I/You/We/They + verb. He/She/It + verb+s.
Pytanie: Do/Does + podmiot + verb.

# Błędy Polaków
- "He don't like coffee" — poprawnie: "He doesn't like coffee"
- "I am go to work" — poprawnie: "I go to work"

# Słówka
- commute [kəˈmjuːt] (komjut) - dojeżdżać do pracy. Example: I commute by train every day.
- chore [tʃɔːr] (czor) - obowiązek domowy. Example: Washing dishes is my least favorite chore.
- errand [ˈerənd] (erand) - sprawa do załatwienia. Example: I need to run a few errands today.
- nap [næp] (nap) - drzemka. Example: I take a short nap after lunch.

# Dialog
A: What time do you usually wake up?
B: I get up at seven and have a quick breakfast.
A: Do you commute to work?
B: Yes, it takes me about thirty minutes.

# Tłumaczenie
Codziennie jeżdżę do pracy autobusem. = I commute to work by bus every day.
On nie lubi porannych obowiązków. = He doesn't like morning chores.
Czy ucinasz sobie drzemkę po obiedzie? = Do you take a nap after lunch?
Muszę załatwić kilka spraw. = I need to run a few errands.

# Idiom
hit the hay - iść spać
Example: I'm exhausted, I'm going to hit the hay.`;

export function makeGrammarQuestionsFromLesson(p: ParsedLesson): Omit<GrammarRule, "id">[] {
  // generate from translations
  return p.translations.slice(0, 4).map((t, i) => {
    const others = p.translations.filter((_, j) => j !== i).map((x) => x.en);
    const shuffled = [t.en, ...others.slice(0, 3)].sort(() => Math.random() - 0.5);
    return {
      topic: p.topic,
      rule: p.grammar.rules.slice(0, 200),
      question: `Przetłumacz: "${t.pl}"`,
      options: shuffled,
      correctIndex: shuffled.indexOf(t.en),
      explanation: `Poprawnie: ${t.en}`,
    };
  });
}
