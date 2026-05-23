import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/PageHeader";
import { statsQuery } from "@/lib/queries";
import { hapticSelect } from "@/lib/telegram";

export const Route = createFileRoute("/stats")({
  component: StatsPage,
});

function StatsPage() {
  const { data } = useQuery(statsQuery());
  const bars = data?.reach_by_day ?? Array.from({ length: 12 }, () => 0);
  const maxBar = Math.max(1, ...bars);
  const peakIdx = bars.indexOf(maxBar);
  const [selected, setSelected] = useState<number | null>(null);
  const activeIdx = selected ?? peakIdx;
  const formatK = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(1)}K` : `${n}`);
  const periodLabel = (i: number) => {
    // 12 столбиков ≈ окна по ~2.3 дня; показываем «n-я неделя назад» с шагом
    const weeksAgo = Math.round((bars.length - 1 - i) * (28 / Math.max(1, bars.length - 1)) / 7);
    if (weeksAgo === 0) return "Эта неделя";
    if (weeksAgo === 1) return "Прошлая неделя";
    return `${weeksAgo} нед. назад`;
  };

  return (
    <div className="page-in">
      <PageHeader title="Creator Studio" />

      <div className="px-5 pt-6">
        <h2 className="text-[34px] font-bold leading-none tracking-tight">Статистика</h2>
        <p className="mt-2 text-[13px] text-muted-foreground">Последние 28 дней</p>
      </div>

      <section className="mt-8 px-5">
        <div className="flex items-baseline justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
              {selected !== null ? periodLabel(selected) : "Охват аудитории"}
            </p>
            {selected !== null && (
              <p className="mt-0.5 text-[11px] text-muted-foreground/70">Нажми ещё раз, чтобы сбросить</p>
            )}
          </div>
          <p className="text-2xl font-semibold tabular-nums transition-all">
            {selected !== null ? formatK(bars[selected] * 1000) : data?.total_reach_label ?? "—"}
          </p>
        </div>
        <div className="mt-5 h-px bg-border" />
        <div className="mt-6 flex h-32 items-end justify-between gap-2">
          {bars.map((h, i) => {
            const isActive = i === activeIdx;
            return (
              <button
                key={i}
                onClick={() => {
                  hapticSelect();
                  setSelected(selected === i ? null : i);
                }}
                aria-label={`${periodLabel(i)}: ${formatK(h * 1000)}`}
                className="group flex-1 rounded-sm transition-all duration-200 active:scale-95"
                style={{
                  height: `${Math.max(4, (h / maxBar) * 100)}%`,
                  backgroundColor: isActive ? "oklch(0.98 0 0)" : "oklch(0.28 0 0)",
                }}
              />
            );
          })}
        </div>
        <div className="mt-6 h-px bg-border" />
      </section>

      <section className="mt-8 grid grid-cols-2 gap-3 px-5">
        {(data?.reach_by_platform ?? []).map((r) => (
          <div key={r.platform} className="rounded-2xl border border-border bg-card p-4">
            <p className="text-[11px] uppercase tracking-wider text-muted-foreground">{r.label}</p>
            <p className="mt-2 text-2xl font-semibold tabular-nums">{r.reach_label}</p>
          </div>
        ))}
        {!data && Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-[88px] animate-pulse rounded-2xl bg-card" />
        ))}
      </section>

      {(data?.metrics ?? []).map((m) => (
        <Metric
          key={m.key}
          label={m.label}
          value={m.value}
          delta={`${m.delta_pct > 0 ? "+" : ""}${m.delta_pct}%`}
          positive={m.delta_pct >= 0}
        />
      ))}

      <section className="mt-10 px-5 pb-10">
        <p className="mb-3 text-xs uppercase tracking-[0.14em] text-muted-foreground">Топ Reels</p>
        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          {(data?.top_videos ?? []).map((c, i, arr) => (
            <div
              key={c.id}
              className={`flex items-center gap-3 px-3 py-3 ${i !== arr.length - 1 ? "border-b border-border" : ""}`}
            >
              <div
                className="h-12 w-12 flex-shrink-0 overflow-hidden rounded-md bg-gradient-to-br from-card-elevated to-background ring-1 ring-border"
                style={c.thumbnail_url ? { backgroundImage: `url(${c.thumbnail_url})`, backgroundSize: "cover" } : undefined}
              />
              <div className="min-w-0 flex-1">
                <p className="truncate text-[14px] font-medium">{c.title}</p>
                <p className="text-[11px] uppercase tracking-wider text-muted-foreground">{c.platform}</p>
              </div>
              <p className="text-[15px] font-semibold tabular-nums">{c.views_label}</p>
            </div>
          ))}
          {!data &&
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-[68px] animate-pulse border-b border-border last:border-0 bg-card" />
            ))}
        </div>
      </section>
    </div>
  );
}

function Metric({
  label,
  value,
  delta,
  positive,
}: {
  label: string;
  value: string;
  delta: string;
  positive?: boolean;
}) {
  return (
    <section className="mt-6 px-5">
      <p className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <div className="mt-1 flex items-baseline gap-2">
        <p className="text-3xl font-semibold tabular-nums">{value}</p>
        <span className={`text-xs tabular-nums ${positive ? "text-foreground/80" : "text-muted-foreground"}`}>
          {delta}
        </span>
      </div>
    </section>
  );
}