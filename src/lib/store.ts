import { useEffect, useState, useCallback, useRef } from "react";
import { supabase } from "@/integrations/supabase/client";

export type ProfileId = "piotr" | "monika";

export interface Word {
  id: string;
  word: string;
  ipa: string;
  pronouncePl: string;
  meaning: string;
  example: string;
  addedAt: number;
  box: number;
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
  rule: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface QuizResult {
  id: string;
  type: "vocab" | "grammar" | "lesson";
  score: number;
  total: number;
  at: number;
  lessonId?: string;
}

export type WordStatus = "known" | "learning";

export interface SrsItem {
  key: string;
  en: string;
  ipa: string;
  plPron: string;
  pl: string;
  example: string;
  source: string; // lessonId or 'custom'
  dueAt: number;
  intervalDays: number;
  ease: number; // SM-2 ease factor
  reps: number;
  addedAt: number;
}

export interface StreakState {
  current: number;
  longest: number;
  lastActiveDay: string; // YYYY-MM-DD
  dailyGoal: number;
  todayCount: number;
  todayDay: string;
}

export interface LessonProgress {
  startedAt?: number;
  completedAt?: number;
  quizScore?: number;
  quizTotal?: number;
  savedVocab?: boolean;
  savedIdioms?: boolean;
}

export interface ProfileData {
  lessons: Lesson[];
  words: Word[];
  idioms: Idiom[];
  grammarRules: GrammarRule[];
  results: QuizResult[];
  wordStatus: Record<string, WordStatus>;
  srs: Record<string, SrsItem>;
  streak: StreakState;
  lessonProgress: Record<string, LessonProgress>;
  customLessons?: unknown[];
}

const defaultStreak = (): StreakState => ({
  current: 0,
  longest: 0,
  lastActiveDay: "",
  dailyGoal: 20,
  todayCount: 0,
  todayDay: "",
});

const empty = (): ProfileData => ({
  lessons: [],
  words: [],
  idioms: [],
  grammarRules: [],
  results: [],
  wordStatus: {},
  srs: {},
  streak: defaultStreak(),
  lessonProgress: {},
});

function normalize(d: Partial<ProfileData> | null | undefined): ProfileData {
  const base = empty();
  if (!d) return base;
  return {
    ...base,
    ...d,
    wordStatus: { ...base.wordStatus, ...(d.wordStatus ?? {}) },
    srs: { ...base.srs, ...(d.srs ?? {}) },
    streak: { ...base.streak, ...(d.streak ?? {}) },
    lessonProgress: { ...base.lessonProgress, ...(d.lessonProgress ?? {}) },
  };
}

const KEY = (p: ProfileId) => `englishApp:${p}`;
const ACTIVE = "englishApp:active";

function loadLocal(p: ProfileId): ProfileData {
  if (typeof window === "undefined") return empty();
  try {
    const raw = localStorage.getItem(KEY(p));
    if (!raw) return empty();
    return normalize(JSON.parse(raw));
  } catch {
    return empty();
  }
}

function saveLocal(p: ProfileId, data: ProfileData) {
  try {
    localStorage.setItem(KEY(p), JSON.stringify(data));
  } catch {
    // ignore quota
  }
}

async function fetchCloud(p: ProfileId): Promise<ProfileData | null> {
  const { data, error } = await supabase
    .from("profile_data")
    .select("data")
    .eq("profile_id", p)
    .maybeSingle();
  if (error) {
    console.warn("[cloud] fetch failed", error.message);
    return null;
  }
  if (!data) return null;
  return normalize(data.data as Partial<ProfileData>);
}

let saveTimer: ReturnType<typeof setTimeout> | null = null;
async function pushCloud(p: ProfileId, data: ProfileData) {
  const payload = JSON.parse(JSON.stringify(data));
  const { error } = await supabase
    .from("profile_data")
    .upsert(
      { profile_id: p, data: payload, updated_at: new Date().toISOString() },
      { onConflict: "profile_id" },
    );
  if (error) console.warn("[cloud] save failed", error.message);
}

function debouncedPush(p: ProfileId, data: ProfileData) {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(() => pushCloud(p, data), 400);
}

export function saveProfile(p: ProfileId, data: ProfileData) {
  saveLocal(p, data);
  debouncedPush(p, data);
  window.dispatchEvent(new CustomEvent("profile:update", { detail: p }));
}

export function getActiveProfile(): ProfileId | null {
  if (typeof window === "undefined") return null;
  const v = localStorage.getItem(ACTIVE);
  return v === "piotr" || v === "monika" ? v : null;
}

export function setActiveProfile(p: ProfileId | null) {
  if (typeof window === "undefined") return;
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
  const latestRef = useRef<ProfileData>(empty());

  useEffect(() => {
    if (!p) return;
    let cancelled = false;

    const local = loadLocal(p);
    setData(local);
    latestRef.current = local;

    fetchCloud(p).then((cloud) => {
      if (cancelled || !cloud) return;
      saveLocal(p, cloud);
      latestRef.current = cloud;
      setData(cloud);
    });

    const channel = supabase
      .channel(`profile_data:${p}`)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "profile_data",
          filter: `profile_id=eq.${p}`,
        },
        (payload) => {
          const row = payload.new as { data?: Partial<ProfileData> } | null;
          if (!row?.data) return;
          const next = normalize(row.data);
          if (JSON.stringify(next) === JSON.stringify(latestRef.current)) return;
          saveLocal(p, next);
          latestRef.current = next;
          setData(next);
        },
      )
      .subscribe();

    const onLocal = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail && detail !== p) return;
      const fresh = loadLocal(p);
      latestRef.current = fresh;
      setData(fresh);
    };
    window.addEventListener("profile:update", onLocal as EventListener);

    return () => {
      cancelled = true;
      supabase.removeChannel(channel);
      window.removeEventListener("profile:update", onLocal as EventListener);
    };
  }, [p]);

  const update = useCallback(
    (mut: (d: ProfileData) => ProfileData) => {
      if (!p) return;
      const next = mut(latestRef.current);
      latestRef.current = next;
      setData(next);
      saveProfile(p, next);
    },
    [p],
  );

  return [data, update] as const;
}

export const uid = () =>
  typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2) + Date.now().toString(36);
