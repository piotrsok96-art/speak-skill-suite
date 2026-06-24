import { useEffect, useState, useCallback } from "react";

export type ProfileId = "piotr" | "monika";

export interface Word {
  id: string;
  word: string;
  ipa: string;
  pronouncePl: string;
  meaning: string;
  example: string;
  addedAt: number;
  // SRS
  box: number; // 1..5
  nextReview: number;
}

export interface Idiom {
  id: string;
  idiom: string;
  meaning: string;
  example: string;
  addedAt: number;
}

export interface Lesson {
  id: string;
  topic: string;
  level: string;
  completedAt: number;
}

export interface GrammarRule {
  id: string;
  topic: string;
  rule: string; // the gist
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface QuizResult {
  id: string;
  type: "vocab" | "grammar";
  score: number;
  total: number;
  at: number;
}

export interface ProfileData {
  lessons: Lesson[];
  words: Word[];
  idioms: Idiom[];
  grammarRules: GrammarRule[];
  results: QuizResult[];
}

const empty = (): ProfileData => ({
  lessons: [],
  words: [],
  idioms: [],
  grammarRules: [],
  results: [],
});

const KEY = (p: ProfileId) => `englishApp:${p}`;
const ACTIVE = "englishApp:active";

export function loadProfile(p: ProfileId): ProfileData {
  if (typeof window === "undefined") return empty();
  try {
    const raw = localStorage.getItem(KEY(p));
    if (!raw) return empty();
    return { ...empty(), ...JSON.parse(raw) };
  } catch {
    return empty();
  }
}

export function saveProfile(p: ProfileId, data: ProfileData) {
  localStorage.setItem(KEY(p), JSON.stringify(data));
  window.dispatchEvent(new CustomEvent("profile:update", { detail: p }));
}

export function getActiveProfile(): ProfileId | null {
  if (typeof window === "undefined") return null;
  const v = localStorage.getItem(ACTIVE);
  return v === "piotr" || v === "monika" ? v : null;
}

export function setActiveProfile(p: ProfileId | null) {
  if (p) localStorage.setItem(ACTIVE, p);
  else localStorage.removeItem(ACTIVE);
  window.dispatchEvent(new CustomEvent("profile:active"));
}

export function useActiveProfile(): ProfileId | null {
  const [p, setP] = useState<ProfileId | null>(null);
  useEffect(() => {
    setP(getActiveProfile());
    const h = () => setP(getActiveProfile());
    window.addEventListener("profile:active", h);
    window.addEventListener("storage", h);
    return () => {
      window.removeEventListener("profile:active", h);
      window.removeEventListener("storage", h);
    };
  }, []);
  return p;
}

export function useProfileData(p: ProfileId | null) {
  const [data, setData] = useState<ProfileData>(empty());
  useEffect(() => {
    if (!p) return;
    setData(loadProfile(p));
    const h = () => setData(loadProfile(p));
    window.addEventListener("profile:update", h);
    window.addEventListener("storage", h);
    return () => {
      window.removeEventListener("profile:update", h);
      window.removeEventListener("storage", h);
    };
  }, [p]);

  const update = useCallback(
    (mut: (d: ProfileData) => ProfileData) => {
      if (!p) return;
      const next = mut(loadProfile(p));
      saveProfile(p, next);
      setData(next);
    },
    [p],
  );

  return [data, update] as const;
}

export const uid = () =>
  typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2) + Date.now().toString(36);
