// Lightweight wrapper around Web Speech API.
// No backend, no cost, works offline in modern browsers.

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

export function speak(text: string, opts: { lang?: string; rate?: number } = {}) {
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
    // ignore — feature not supported
  }
}

export function ttsAvailable(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}
