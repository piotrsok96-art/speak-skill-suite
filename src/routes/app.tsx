import {
  createFileRoute,
  Link,
  Outlet,
  useNavigate,
  useRouterState,
} from "@tanstack/react-router";
import { useEffect } from "react";
import { useActiveProfile, setActiveProfile } from "@/lib/store";
import {
  BookOpen,
  Repeat,
  Sparkles,
  Library,
  BarChart3,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app")({
  component: AppLayout,
});

const nav = [
  { to: "/app/lesson", label: "Nowa Lekcja", icon: BookOpen },
  { to: "/app/vocab-review", label: "Powtórka Słówek", icon: Repeat },
  { to: "/app/grammar-quiz", label: "Quiz Gramatyczny", icon: Sparkles },
  { to: "/app/dictionary", label: "Mój Słowniczek", icon: Library },
  { to: "/app/progress", label: "Postępy", icon: BarChart3 },
] as const;

function AppLayout() {
  const profile = useActiveProfile();
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  useEffect(() => {
    if (profile === null) {
      // wait for hydration; if still null after mount, redirect
      const t = setTimeout(() => {
        if (!localStorage.getItem("englishApp:active")) navigate({ to: "/" });
      }, 50);
      return () => clearTimeout(t);
    }
  }, [profile, navigate]);

  const logout = () => {
    setActiveProfile(null);
    navigate({ to: "/" });
  };

  return (
    <div className="min-h-screen flex bg-background">
      <aside className="no-print w-60 shrink-0 border-r bg-card flex flex-col">
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
        </div>
        <nav className="flex-1 py-3 px-2 space-y-1">
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
                {item.label}
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
