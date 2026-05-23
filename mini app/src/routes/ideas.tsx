import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Plus,
  Search,
  Sparkles,
  Trash2,
  Check,
  CalendarClock,
  FileText,
  Loader2,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { haptic, hapticSelect } from "@/lib/telegram";
import {
  createIdea,
  deleteIdea,
  studioQuery,
  updateIdea,
} from "@/lib/queries";
import type { Idea, StudioData } from "@/lib/types";

export const Route = createFileRoute("/ideas")({
  component: IdeasPage,
});

type Platform = Idea["platform"];
type Status = Idea["status"];

const PLATFORMS: Platform[] = ["Reels", "YT", "TikTok", "VK"];
const STATUS_TABS: { value: Status | "all"; label: string }[] = [
  { value: "all", label: "Все" },
  { value: "draft", label: "Черновики" },
  { value: "planned", label: "В плане" },
  { value: "published", label: "Готово" },
];

const STATUS_META: Record<Status, { label: string; icon: typeof FileText; dot: string }> = {
  draft: { label: "Черновик", icon: FileText, dot: "bg-muted-foreground/50" },
  planned: { label: "В плане", icon: CalendarClock, dot: "bg-foreground" },
  published: { label: "Опубликовано", icon: Check, dot: "bg-emerald-400" },
};

function IdeasPage() {
  const studio = useQuery(studioQuery());
  const qc = useQueryClient();

  const [filter, setFilter] = useState<Status | "all">("all");
  const [search, setSearch] = useState("");
  const [composerOpen, setComposerOpen] = useState(false);
  const [draftTitle, setDraftTitle] = useState("");
  const [draftDescription, setDraftDescription] = useState("");
  const [draftPlatform, setDraftPlatform] = useState<Platform>("Reels");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Триггер с вкладки «Студия»: открыть composer
  useEffect(() => {
    try {
      if (sessionStorage.getItem("ideas:compose") === "1") {
        sessionStorage.removeItem("ideas:compose");
        setComposerOpen(true);
      }
    } catch {}
  }, []);

  const ideas = studio.data?.ideas ?? [];
  const visible = useMemo(() => {
    return ideas.filter((i) => {
      if (filter !== "all" && i.status !== filter) return false;
      if (search && !i.title.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [ideas, filter, search]);

  const counts = useMemo(() => {
    const c: Record<Status, number> = { draft: 0, planned: 0, published: 0 };
    for (const i of ideas) c[i.status]++;
    return c;
  }, [ideas]);

  const patchLocal = (fn: (data: StudioData) => StudioData) => {
    const prev = qc.getQueryData<StudioData>(["studio"]);
    if (prev) qc.setQueryData<StudioData>(["studio"], fn(prev));
    return prev;
  };

  const addMutation = useMutation({
    mutationFn: createIdea,
    onMutate: async (input) => {
      await qc.cancelQueries({ queryKey: ["studio"] });
      const optimistic: Idea = {
        id: `tmp-${Date.now()}`,
        title: input.title,
        platform: input.platform,
        status: "draft",
        created_at: new Date().toISOString(),
        description: input.description,
      };
      const prev = patchLocal((d) => ({ ...d, ideas: [optimistic, ...d.ideas] }));
      return { prev };
    },
    onError: (_e, _v, ctx) => ctx?.prev && qc.setQueryData(["studio"], ctx.prev),
    onSettled: () => qc.invalidateQueries({ queryKey: ["studio"] }),
  });

  const statusMutation = useMutation({
    mutationFn: (v: { id: string; status: Status }) => updateIdea(v),
    onMutate: async (v) => {
      await qc.cancelQueries({ queryKey: ["studio"] });
      const prev = patchLocal((d) => ({
        ...d,
        ideas: d.ideas.map((i) => (i.id === v.id ? { ...i, status: v.status } : i)),
      }));
      return { prev };
    },
    onError: (_e, _v, ctx) => ctx?.prev && qc.setQueryData(["studio"], ctx.prev),
    onSettled: () => qc.invalidateQueries({ queryKey: ["studio"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteIdea(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: ["studio"] });
      const prev = patchLocal((d) => ({ ...d, ideas: d.ideas.filter((i) => i.id !== id) }));
      return { prev };
    },
    onError: (_e, _v, ctx) => ctx?.prev && qc.setQueryData(["studio"], ctx.prev),
    onSettled: () => qc.invalidateQueries({ queryKey: ["studio"] }),
  });

  const submit = () => {
    const title = draftTitle.trim();
    if (!title) return;
    haptic("medium");
    addMutation.mutate({ title, platform: draftPlatform, description: draftDescription.trim() || undefined });
    setDraftTitle("");
    setDraftDescription("");
    setComposerOpen(false);
  };

  const cycleStatus = (idea: Idea) => {
    const next: Status = idea.status === "draft" ? "planned" : idea.status === "planned" ? "published" : "draft";
    haptic("light");
    statusMutation.mutate({ id: idea.id, status: next });
  };

  return (
    <div className="page-in">
      <PageHeader title="Идеи" />

      <div className="px-5 pt-6">
        <div className="flex items-end justify-between gap-3">
          <div>
            <h2 className="text-[34px] font-bold leading-none tracking-tight shimmer-text">
              Бэклог
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {ideas.length} идей · {counts.planned} в плане
            </p>
          </div>
          <button
            onClick={() => {
              haptic("medium");
              setComposerOpen((v) => !v);
            }}
            className="flex h-11 w-11 items-center justify-center rounded-full bg-foreground text-background shadow-lg shadow-foreground/10 transition-transform active:scale-90"
            aria-label="Новая идея"
          >
            <Plus className={`h-5 w-5 transition-transform duration-300 ${composerOpen ? "rotate-45" : ""}`} />
          </button>
        </div>
      </div>

      {/* Composer */}
      <div
        className={`grid px-5 transition-[grid-template-rows,opacity,margin] duration-300 ease-out ${composerOpen ? "mt-5 grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}
      >
        <div className="overflow-hidden">
          <div className="rounded-2xl border border-border-strong bg-card/80 p-4 backdrop-blur-xl">
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.14em] text-muted-foreground">
              <Sparkles className="h-3.5 w-3.5" /> Новая идея
            </div>
            <input
              value={draftTitle}
              onChange={(e) => setDraftTitle(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit()}
              autoFocus={composerOpen}
              placeholder="О чём снимем?"
              className="mt-3 w-full bg-transparent text-[17px] font-medium text-foreground outline-none placeholder:text-muted-foreground/60"
            />
            <textarea
              value={draftDescription}
              onChange={(e) => setDraftDescription(e.target.value)}
              placeholder="Короткое описание (необязательно)"
              rows={2}
              className="mt-2 w-full resize-none bg-transparent text-[13px] text-muted-foreground outline-none placeholder:text-muted-foreground/40"
            />
            <div className="mt-4 flex flex-wrap gap-2">
              {PLATFORMS.map((p) => (
                <button
                  key={p}
                  onClick={() => {
                    hapticSelect();
                    setDraftPlatform(p);
                  }}
                  className={`rounded-full border px-3 py-1 text-xs transition-all ${
                    draftPlatform === p
                      ? "border-foreground bg-foreground text-background"
                      : "border-border text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {p}
                </button>
              ))}
              <div className="ml-auto flex gap-2">
                <button
                  onClick={() => setComposerOpen(false)}
                  className="rounded-full px-3 py-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  Отмена
                </button>
                <button
                  onClick={submit}
                  disabled={!draftTitle.trim() || addMutation.isPending}
                  className="flex items-center gap-1 rounded-full bg-foreground px-3 py-1 text-xs text-background disabled:opacity-50"
                >
                  {addMutation.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Plus className="h-3 w-3" />}
                  Добавить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="mt-6 px-5">
        <div className="flex items-center gap-2 rounded-full border border-border bg-card/60 px-4 py-2.5 backdrop-blur-xl">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск по идеям"
            className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground/60"
          />
        </div>
      </div>

      {/* Filter tabs */}
      <div className="mt-4 flex gap-2 overflow-x-auto px-5 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {STATUS_TABS.map((t) => {
          const active = filter === t.value;
          const count = t.value === "all" ? ideas.length : counts[t.value];
          return (
            <button
              key={t.value}
              onClick={() => {
                hapticSelect();
                setFilter(t.value);
              }}
              className={`shrink-0 rounded-full border px-3 py-1.5 text-xs transition-all ${
                active
                  ? "border-foreground bg-foreground text-background"
                  : "border-border text-muted-foreground"
              }`}
            >
              {t.label} <span className="opacity-60">· {count}</span>
            </button>
          );
        })}
      </div>

      {/* List */}
      <section className="mt-5 space-y-2.5 px-5 pb-10">
        {!studio.data ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-2xl bg-card/60" />
          ))
        ) : visible.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border bg-card/30 px-4 py-12 text-center">
            <Sparkles className="mx-auto h-6 w-6 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">
              Ничего не найдено. Запиши идею, пока не забыл.
            </p>
          </div>
        ) : (
          visible.map((idea, i) => {
            const meta = STATUS_META[idea.status];
            const Icon = meta.icon;
            const isOpen = expandedId === idea.id;
            return (
              <div
                key={idea.id}
                className="pop-in group rounded-2xl border border-border bg-card/70 backdrop-blur-xl transition-colors hover:border-border-strong"
                style={{ animationDelay: `${Math.min(i * 40, 240)}ms` }}
              >
                <div className="flex items-center gap-3 p-4">
                  <button
                    onClick={(e) => { e.stopPropagation(); cycleStatus(idea); }}
                    className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-all ${
                      idea.status === "published"
                        ? "bg-emerald-400/20 text-emerald-300"
                        : idea.status === "planned"
                        ? "bg-foreground/10 text-foreground"
                        : "bg-card-elevated text-muted-foreground"
                    }`}
                    aria-label="Сменить статус"
                  >
                    <Icon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      hapticSelect();
                      setExpandedId(isOpen ? null : idea.id);
                    }}
                    className="min-w-0 flex-1 text-left"
                  >
                    <p
                      className={`truncate text-[15px] font-medium ${
                        idea.status === "published" ? "text-muted-foreground line-through" : "text-foreground"
                      }`}
                    >
                      {idea.title}
                    </p>
                    <div className="mt-1 flex items-center gap-2 text-[11px] text-muted-foreground">
                      <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
                      {meta.label}
                      <span>·</span>
                      <span>{idea.platform}</span>
                    </div>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      haptic("light");
                      deleteMutation.mutate(idea.id);
                    }}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-muted-foreground transition-opacity hover:bg-card-elevated hover:text-foreground sm:opacity-0 sm:group-hover:opacity-100"
                    aria-label="Удалить"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <div
                  className={`grid overflow-hidden px-4 transition-[grid-template-rows,padding] duration-300 ease-out ${
                    isOpen ? "grid-rows-[1fr] pb-4" : "grid-rows-[0fr]"
                  }`}
                >
                  <div className="min-h-0">
                    <div className="rounded-xl bg-card-elevated/60 p-3 text-[13px] leading-relaxed text-muted-foreground">
                      {idea.description ?? "Описания пока нет. Открой Telegram-бот, чтобы дополнить идею голосом или текстом."}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </section>
    </div>
  );
}