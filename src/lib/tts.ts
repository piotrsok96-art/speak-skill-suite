// Natural TTS via Lovable AI Gateway with graceful fallback to Web Speech API.

let cached: SpeechSynthesisVoice[] = [];
function pickVoice(): SpeechSynthesisVoice | undefined {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return undefined;
  if (cached.length === 0) cached = window.speechSynthesis.getVoices();
  if (cached.length === 0) return undefined;
  return (
    cached.find((v) => /en[-_]GB/i.test(v.lang)) ??
    cached.find((v) => /en[-_]US/i.test(v.lang)) ??
    cached.find((v) => v.lang.toLowerCase().startsWith("en")) ??
    cached[0]
  );
}
if (typeof window !== "undefined" && "speechSynthesis" in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    cached = window.speechSynthesis.getVoices();
  };
}

export function speakSystem(text: string, opts: { lang?: string; rate?: number } = {}) {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  try {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = opts.lang ?? "en-GB";
    u.rate = opts.rate ?? 0.95;
    const v = pickVoice();
    if (v) u.voice = v;
    window.speechSynthesis.speak(u);
  } catch {
    /* noop */
  }
}

const VOICE_KEY = "englishApp:tts:voice";
const NATURAL_KEY = "englishApp:tts:natural";

export type NaturalVoice = "alloy" | "verse" | "shimmer" | "sage" | "ash";
export const VOICE_OPTIONS: { id: NaturalVoice; label: string }[] = [
  { id: "alloy", label: "Alloy (neutral)" },
  { id: "verse", label: "Verse (męski)" },
  { id: "shimmer", label: "Shimmer (żeński)" },
  { id: "sage", label: "Sage (ciepły)" },
  { id: "ash", label: "Ash (głęboki)" },
];

export function getVoicePref(): NaturalVoice {
  if (typeof window === "undefined") return "alloy";
  const v = localStorage.getItem(VOICE_KEY);
  return (VOICE_OPTIONS.find((o) => o.id === v)?.id ?? "alloy") as NaturalVoice;
}
export function setVoicePref(v: NaturalVoice) {
  if (typeof window === "undefined") return;
  localStorage.setItem(VOICE_KEY, v);
  audioCache.clear();
}
export function isNaturalEnabled(): boolean {
  if (typeof window === "undefined") return true;
  return localStorage.getItem(NATURAL_KEY) !== "0";
}
export function setNaturalEnabled(on: boolean) {
  if (typeof window === "undefined") return;
  localStorage.setItem(NATURAL_KEY, on ? "1" : "0");
}

// In-memory MP3 cache keyed by voice+text.
const audioCache = new Map<string, string>(); // key -> blob URL
let currentAudio: HTMLAudioElement | null = null;

async function fetchNatural(text: string, voice: NaturalVoice): Promise<string | null> {
  const key = `${voice}::${text}`;
  const hit = audioCache.get(key);
  if (hit) return hit;
  try {
    const res = await fetch("/api/public/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice }),
    });
    if (!res.ok) return null;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    audioCache.set(key, url);
    return url;
  } catch {
    return null;
  }
}

export async function speak(
  text: string,
  opts: { natural?: boolean; voice?: NaturalVoice } = {},
): Promise<void> {
  const natural = opts.natural ?? isNaturalEnabled();
  const voice = opts.voice ?? getVoicePref();
  // Stop any in-flight audio
  if (currentAudio) {
    try {
      currentAudio.pause();
    } catch {
      /* noop */
    }
    currentAudio = null;
  }
  if (typeof window !== "undefined" && "speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
  if (natural) {
    const url = await fetchNatural(text, voice);
    if (url) {
      const audio = new Audio(url);
      currentAudio = audio;
      audio.play().catch(() => speakSystem(text));
      return;
    }
  }
  speakSystem(text);
}

export function ttsAvailable(): boolean {
  return typeof window !== "undefined";
}
