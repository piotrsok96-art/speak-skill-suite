import {
  createFileRoute,
  Link,
  Outlet,
  useNavigate,
  useRouterState,
} from "@tanstack/react-router";
import { useEffect, useMemo } from "react";
import { useActiveProfile, setActiveProfile, useProfileData } from "@/lib/store";
import { countDue } from "@/lib/srs";
import { ensureToday } from "@/lib/streak";
import {
  BookOpen,
  Repeat,
  Sparkles,
  Library,
  BarChart3,
  LogOut,
  GraduationCap,
  Repeat2,
  HelpCircle,
  Flame,
  FilePlus2,
} from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app")({
  component: AppLayout,
});

function AppLayout() {
  const profile = useActiveProfile();
  const [data] = useProfileData(profile);
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  useEffect(() => {
    if (profile === null) {
      const t = setTimeout(() => {
        if (!localStorage.getItem("englishApp:active")) navigate({ to: "/" });
      }, 50);
      return () => clearTimeout(t);
    }
  }, [profile, navigate]);

  const dueCount = useMemo(() => countDue(data.srs), [data.srs]);
  const streak = useMemo(() => ensureToday(data.streak), [data.streak]);

  const nav = [
    { to: "/app/lessons", label: "Lekcje (50)", icon: GraduationCap, badge: null as number | null },
    { to: "/app/srs", label: "Powtórka dnia", icon: Repeat2, badge: dueCount || null },
    { to: "/app/vocab-review", label: "Powtórka słówek", icon: Repeat, badge: null },
    { to: "/app/grammar-quiz", label: "Quiz gramatyczny", icon: Sparkles, badge: null },
    { to: "/app/dictionary", label: "Mój słowniczek", icon: Library, badge: null },
    { to: "/app/progress", label: "Postępy", icon: BarChart3, badge: null },
    { to: "/app/help", label: "Jak używać", icon: HelpCircle, badge: null },
    { to: "/app/lesson", label: "Wklej lekcję", icon: FilePlus2, badge: null },
  ] as const;

  const switchProfile = (p: "piotr" | "monika") => {
    if (p !== profile) {
      setActiveProfile(p);
      navigate({ to: "/app/lessons" });
    }
  };

  const logout = () => {
    setActiveProfile(null);
    navigate({ to: "/" });
  };

  return (
    <div className="min-h-screen flex bg-background">
      <aside className="no-print w-64 shrink-0 border-r bg-card flex flex-col">
        <div className="px-5 py-5 border-b">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            <span className="text-lg font-bold" style={{ color: "#000" }}>
              EnglishLab
            </span>
          </div>
          {profile && (
            <div className="mt-3 flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-sm font-bold">
                {profile[0].toUpperCase()}
              </div>
              <div className="text-sm capitalize font-semibold">{profile}</div>
            </div>
          )}
          {profile && (
            <div className="mt-3 rounded-lg bg-secondary/60 px-3 py-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center gap-1 font-medium">
                  <Flame className="h-3 w-3 text-orange-500" /> {streak.current} dni
                </span>
                <span className="text-muted-foreground">
                  {streak.todayCount}/{streak.dailyGoal} dziś
                </span>
              </div>
              <div className="mt-1.5 h-1.5 rounded-full bg-background overflow-hidden">
                <div
                  className="h-full bg-orange-500 transition-all"
                  style={{
                    width: `${Math.min(100, (streak.todayCount / Math.max(1, streak.dailyGoal)) * 100)}%`,
                  }}
                />
              </div>
            </div>
          )}
        </div>
        <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
          {nav.map((item) => {
            const active = pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-secondary text-foreground"
                    : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground",
                )}
              >
                <item.icon className="h-4 w-4" />
                <span className="flex-1">{item.label}</span>
                {item.badge != null && item.badge > 0 && (
                  <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 rounded-full bg-orange-500 text-white text-[10px] font-bold">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
        <button
          onClick={logout}
          className="no-print m-3 flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Zmień profil
        </button>
      </aside>
      <main className="flex-1 min-w-0 overflow-x-hidden">
        <div className="max-w-4xl mx-auto px-6 md:px-10 py-8 md:py-12">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
