import { createFileRoute } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import { Flame, Star, Trophy, Gem, UserCog, Lock, Bell, Send, ChevronRight, LogOut, Pencil, X } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { haptic } from "@/lib/telegram";
import { PageHeader } from "@/components/PageHeader";
import { profileQuery } from "@/lib/queries";
import type { Achievement } from "@/lib/types";

export const Route = createFileRoute("/profile")({
  component: ProfilePage,
});

const iconMap = { flame: Flame, star: Star, trophy: Trophy, gem: Gem } as const;

type MenuKey = "account" | "privacy" | "notifications" | "telegram";
const menu: { icon: typeof UserCog; label: string; key: MenuKey; description: string }[] = [
  { icon: UserCog, key: "account", label: "Account Settings", description: "Имя, e-mail, часовой пояс — синхронизируются с твоим Telegram-ботом." },
  { icon: Lock, key: "privacy", label: "Privacy & Security", description: "Подключённые соцсети, доступ к токенам, удаление аккаунта." },
  { icon: Bell, key: "notifications", label: "Notifications", description: "Пуши о публикациях, охватах и напоминания о съёмке." },
  { icon: Send, key: "telegram", label: "Telegram Integration", description: "Свяжи аккаунт с @lelya_studio_bot, чтобы вести идеи прямо из чата." },
];

function ProfilePage() {
  const { data } = useQuery(profileQuery());
  const me = data?.me;
  const name = me?.first_name ?? "...";
  const handle = me?.username ? `@${me.username}` : "";
  const photo = me?.photo_url ?? undefined;
  const achievements: Achievement[] = data?.achievements ?? [];
  const [editOpen, setEditOpen] = useState(false);
  const [editName, setEditName] = useState("");
  const [activeMenu, setActiveMenu] = useState<MenuKey | null>(null);
  const activeMenuItem = menu.find((m) => m.key === activeMenu) ?? null;

  return (
    <div className="page-in">
      <PageHeader title="Creator Studio" avatar={photo} />

      <section className="flex flex-col items-center px-5 pt-8">
        <div className="relative">
          <div className="flex h-24 w-24 items-center justify-center overflow-hidden rounded-full bg-card-elevated ring-1 ring-border-strong">
            {photo ? (
              <img src={photo} alt="" className="h-full w-full object-cover" />
            ) : (
              <span className="text-3xl">🪐</span>
            )}
          </div>
          <button
            onClick={() => {
              haptic("light");
              setEditName(name === "..." ? "" : name);
              setEditOpen(true);
            }}
            className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full bg-card-elevated ring-1 ring-border-strong"
            aria-label="Изменить имя"
          >
            <Pencil className="h-3 w-3 text-foreground" />
          </button>
        </div>
        <h2 className="mt-4 text-2xl font-semibold tracking-tight">{name}</h2>
        <p className="mt-0.5 text-sm text-muted-foreground">{handle}</p>

        {me ? (
          <div className="mt-6 flex items-center gap-4 rounded-full border border-border bg-card px-5 py-2.5">
            <span className="flex items-center gap-1.5 text-[13px]">🔥 {me.streak_days} дней</span>
            <span className="h-3 w-px bg-border" />
            <span className="text-[13px] tabular-nums text-muted-foreground">{me.total_reels} роликов</span>
          </div>
        ) : null}
      </section>

      <section className="mt-8 px-5">
        <div className="mb-3 flex items-center gap-2">
          <div className="h-3 w-px bg-foreground" />
          <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Achievements</p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {achievements.map((a) => {
            const Icon = iconMap[a.icon];
            return (
              <div key={a.key} className="rounded-2xl border border-border bg-card p-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-card-elevated">
                  <Icon className="h-4 w-4 text-foreground" strokeWidth={1.8} />
                </div>
                <p className="mt-3 text-[15px] font-semibold">{a.label}</p>
                <p className="text-[12px] text-muted-foreground">{a.earned_at_label}</p>
              </div>
            );
          })}
          {!data &&
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-[120px] animate-pulse rounded-2xl bg-card" />
            ))}
        </div>
      </section>

      <section className="mt-8 px-5">
        <div className="mb-3 flex items-center gap-2">
          <div className="h-3 w-px bg-foreground" />
          <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Preferences</p>
        </div>
        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          {menu.map((m, i) => (
            <button
              key={m.label}
              onClick={() => {
                haptic("light");
                setActiveMenu(m.key);
              }}
              className={`flex w-full items-center gap-3 px-4 py-4 text-left transition-colors hover:bg-card-elevated ${i !== menu.length - 1 ? "border-b border-border" : ""}`}
            >
              <m.icon className="h-[18px] w-[18px] text-foreground" strokeWidth={1.7} />
              <span className="flex-1 text-[15px]">{m.label}</span>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </button>
          ))}
        </div>
      </section>

      <section className="mt-10 flex justify-center px-5 pb-10">
        <button
          onClick={() => haptic("medium")}
          className="flex items-center gap-2 rounded-full border border-border-strong px-6 py-2.5 text-[14px] text-[oklch(0.78_0.08_30)] transition-colors hover:bg-card-elevated"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </section>

      <Sheet open={editOpen} onClose={() => setEditOpen(false)} title="Изменить имя">
        <input
          value={editName}
          onChange={(e) => setEditName(e.target.value)}
          placeholder="Как тебя представить"
          className="w-full rounded-xl border border-border bg-card-elevated px-4 py-3 text-[15px] outline-none focus:border-foreground"
        />
        <button
          onClick={() => { haptic("medium"); setEditOpen(false); }}
          disabled={!editName.trim()}
          className="mt-4 w-full rounded-xl bg-foreground py-3 text-[15px] font-medium text-background disabled:opacity-40"
        >
          Сохранить
        </button>
      </Sheet>

      <Sheet
        open={activeMenu !== null}
        onClose={() => setActiveMenu(null)}
        title={activeMenuItem?.label ?? ""}
      >
        <p className="text-[14px] leading-relaxed text-muted-foreground">
          {activeMenuItem?.description}
        </p>
        <div className="mt-5 rounded-xl border border-dashed border-border bg-card-elevated/40 px-4 py-3 text-[12px] text-muted-foreground">
          Этот раздел подтянет реальные данные, как только бэкенд /api/profile вернёт настройки пользователя.
        </div>
      </Sheet>
    </div>
  );
}

function Sheet({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  return (
    <div
      className={`fixed inset-0 z-50 flex items-end justify-center transition-opacity duration-300 ${open ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"}`}
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-background/60 backdrop-blur-md" />
      <div
        onClick={(e) => e.stopPropagation()}
        className={`relative w-full max-w-md rounded-t-3xl border border-border-strong border-b-0 bg-card p-5 pb-8 shadow-2xl transition-transform duration-300 ease-out ${open ? "translate-y-0" : "translate-y-full"}`}
      >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-border-strong" />
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-[17px] font-semibold">{title}</h3>
          <button onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-full text-muted-foreground hover:bg-card-elevated">
            <X className="h-4 w-4" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}