import { Link, useLocation } from "@tanstack/react-router";
import { LayoutGrid, Lightbulb, BarChart3, User } from "lucide-react";
import { hapticSelect } from "@/lib/telegram";

const items = [
  { to: "/", label: "Студия", icon: LayoutGrid },
  { to: "/ideas", label: "Идеи", icon: Lightbulb },
  { to: "/stats", label: "Статы", icon: BarChart3 },
  { to: "/profile", label: "Профиль", icon: User },
] as const;

export function BottomNav() {
  const { pathname } = useLocation();
  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-border/60 bg-background/70 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-md items-stretch justify-around px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2">
        {items.map(({ to, label, icon: Icon }) => {
          const active = pathname === to;
          return (
            <Link
              key={to}
              to={to}
              onClick={() => hapticSelect()}
              className="group relative flex flex-1 flex-col items-center gap-1 py-1.5"
            >
              {active && (
                <span className="absolute inset-x-4 top-0 h-[2px] rounded-full bg-foreground/80 pop-in" />
              )}
              <Icon
                className={`h-5 w-5 transition-all duration-300 ${active ? "text-foreground scale-110" : "text-muted-foreground group-active:scale-90"}`}
                strokeWidth={active ? 2.2 : 1.8}
              />
              <span
                className={`text-[10px] tracking-wide transition-colors ${active ? "text-foreground font-medium" : "text-muted-foreground"}`}
              >
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}