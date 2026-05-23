import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/PageHeader";
import { haptic, hapticSelect } from "@/lib/telegram";
import { meQuery, studioQuery } from "@/lib/queries";

export const Route = createFileRoute("/")({
  component: StudioPage,
});

function StudioPage() {
  const me = useQuery(meQuery());
  const studio = useQuery(studioQuery());
  const navigate = useNavigate();
  const [selectedDay, setSelectedDay] = useState<number | null>(null);

  const name = me.data?.first_name ?? "...";
  const avatar = me.data?.photo_url ?? undefined;
  const data = studio.data;
  const activity = data?.activity ?? Array.from({ length: 30 }, () => 0);
  const intensityLabel = ["Без активности", "Лёгкий день", "Хороший день", "Огонь"] as const;

  return (
    <div className="page-in">
      <PageHeader title={`Привет, ${name}`} avatar={avatar} />

      <div className="px-5 pt-6">
        <h2 className="text-[34px] font-bold leading-none tracking-tight">Сегодня</h2>
      </div>

      <section className="mt-6 space-y-5 px-5">
        {data ? (
          data.goals.map((g) => <Goal key={g.key} label={g.label} value={g.value} total={g.total} />)
        ) : (
          <SkeletonLines n={2} />
        )}
      </section>

      <section className="mt-10 px-5">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">Активность · 30 дней</p>
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
            меньше
            {[0, 1, 2, 3].map((v) => (
              <span
                key={v}
                className="h-2.5 w-2.5 rounded-[3px]"
                style={{
                  backgroundColor:
                    v === 0 ? "oklch(0.14 0 0)" : v === 1 ? "oklch(0.22 0 0)" : v === 2 ? "oklch(0.45 0 0)" : "oklch(0.98 0 0)",
                }}
              />
            ))}
            больше
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-card p-4">
          <div className="grid grid-cols-10 gap-1.5">
            {activity.map((v, i) => {
              const daysAgo = activity.length - 1 - i;
              const isSelected = selectedDay === i;
              return (
                <button
                  key={i}
                  onClick={() => {
                    hapticSelect();
                    setSelectedDay(isSelected ? null : i);
                  }}
                  aria-label={`${daysAgo === 0 ? "Сегодня" : `${daysAgo} дн. назад`}: ${intensityLabel[v]}`}
                  className={`aspect-square rounded-[4px] transition-all duration-150 active:scale-90 ${
                    isSelected ? "ring-2 ring-foreground ring-offset-2 ring-offset-card" : ""
                  }`}
                  style={{
                    backgroundColor:
                      v === 0 ? "oklch(0.14 0 0)" : v === 1 ? "oklch(0.22 0 0)" : v === 2 ? "oklch(0.45 0 0)" : "oklch(0.98 0 0)",
                  }}
                />
              );
            })}
          </div>
          <div
            className={`grid overflow-hidden transition-[grid-template-rows,margin] duration-300 ${
              selectedDay !== null ? "mt-4 grid-rows-[1fr]" : "grid-rows-[0fr]"
            }`}
          >
            <div className="min-h-0">
              {selectedDay !== null && (
                <div className="flex items-center justify-between rounded-xl bg-card-elevated px-3 py-2.5 text-[13px]">
                  <span className="text-muted-foreground">
                    {activity.length - 1 - selectedDay === 0
                      ? "Сегодня"
                      : `${activity.length - 1 - selectedDay} дн. назад`}
                  </span>
                  <span className="font-medium">{intensityLabel[activity[selectedDay]]}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="mt-10 px-5 pb-10">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">Бэклог идей</p>
          <button
            onClick={() => {
              haptic("medium");
              try { sessionStorage.setItem("ideas:compose", "1"); } catch {}
              navigate({ to: "/ideas" });
            }}
            className="flex items-center gap-1 rounded-full border border-border-strong px-3 py-1 text-xs text-foreground transition-colors hover:bg-card-elevated"
          >
            <Plus className="h-3.5 w-3.5" /> Новая
          </button>
        </div>
        {data ? (
          <div className="overflow-hidden rounded-2xl border border-border bg-card">
            {data.ideas.length === 0 ? (
              <div className="px-4 py-10 text-center text-sm text-muted-foreground">
                Пока пусто. Нажми «Новая».
              </div>
            ) : (
              data.ideas.slice(0, 5).map((idea, i, arr) => (
                <button
                  key={idea.id}
                  onClick={() => {
                    hapticSelect();
                    navigate({ to: "/ideas" });
                  }}
                  className={`flex w-full items-center gap-3 px-4 py-4 text-left transition-colors hover:bg-card-elevated ${i !== arr.length - 1 ? "border-b border-border" : ""}`}
                >
                  <span
                    className={`h-2 w-2 rounded-full ${idea.status === "planned" ? "bg-foreground" : "bg-muted-foreground/40"}`}
                  />
                  <span className="flex-1 text-[15px]">{idea.title}</span>
                  <span className="rounded-full bg-card-elevated px-2 py-0.5 text-[10px] uppercase tracking-wider text-muted-foreground">
                    {idea.platform}
                  </span>
                </button>
              ))
            )}
          </div>
        ) : (
          <SkeletonLines n={3} />
        )}
      </section>
    </div>
  );
}

function Goal({ label, value, total }: { label: string; value: number; total: number }) {
  const pct = Math.min(100, (value / total) * 100);
  return (
    <div>
      <div className="mb-2 flex items-baseline justify-between">
        <span className="text-[15px] font-medium">{label}</span>
        <span className="text-xs tabular-nums text-muted-foreground">
          {value}/{total}
        </span>
      </div>
      <div className="h-[2px] w-full overflow-hidden rounded-full bg-border">
        <div
          className="h-full bg-foreground transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function SkeletonLines({ n }: { n: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: n }).map((_, i) => (
        <div key={i} className="h-14 animate-pulse rounded-2xl bg-card" />
      ))}
    </div>
  );
}
