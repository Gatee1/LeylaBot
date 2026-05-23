import { Settings } from "lucide-react";
import { haptic } from "@/lib/telegram";

export function PageHeader({ title, avatar }: { title: string; avatar?: string }) {
  return (
    <header className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-background/85 px-5 py-3 backdrop-blur-xl">
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-card-elevated ring-1 ring-border">
          {avatar ? (
            <img src={avatar} alt="" className="h-full w-full object-cover" />
          ) : (
            <span className="text-xs">🪐</span>
          )}
        </div>
        <h1 suppressHydrationWarning className="text-[15px] font-semibold tracking-tight">{title}</h1>
      </div>
      <button
        onClick={() => haptic("light")}
        className="flex h-9 w-9 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-card-elevated hover:text-foreground"
        aria-label="Settings"
      >
        <Settings className="h-[18px] w-[18px]" strokeWidth={1.8} />
      </button>
    </header>
  );
}