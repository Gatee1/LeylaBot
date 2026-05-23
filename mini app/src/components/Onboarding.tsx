import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { completeOnboarding } from "@/lib/queries";
import { haptic } from "@/lib/telegram";
import type { Me } from "@/lib/types";

export function Onboarding({ initialName }: { initialName: string }) {
  const [name, setName] = useState(initialName);
  const qc = useQueryClient();

  const mutation = useMutation({
    mutationFn: completeOnboarding,
    onSuccess: (data) => {
      qc.setQueryData<Me>(["me"], data);
      qc.invalidateQueries();
      haptic("medium");
    },
  });

  return (
    <div className="fixed inset-0 z-[60] flex flex-col bg-background px-6 pb-8 pt-16">
      <div className="flex-1">
        <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Шаг 1 из 1</p>
        <h1 className="mt-3 text-[34px] font-bold leading-tight tracking-tight">
          Добро пожаловать
          <br />в Creator Studio
        </h1>
        <p className="mt-3 text-[15px] leading-relaxed text-muted-foreground">
          Пара секунд на знакомство — и переходим к работе.
        </p>

        <div className="mt-10">
          <label className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
            Как тебя называть
          </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Алекс"
            autoFocus
            className="mt-2 w-full border-0 border-b border-border bg-transparent pb-3 text-2xl font-semibold tracking-tight outline-none focus:border-foreground"
          />
        </div>

        {mutation.isError ? (
          <p className="mt-4 text-sm text-[oklch(0.78_0.08_30)]">
            Не удалось сохранить. Попробуй ещё раз.
          </p>
        ) : null}
      </div>

      <button
        disabled={!name.trim() || mutation.isPending}
        onClick={() => {
          haptic("light");
          mutation.mutate({
            first_name: name.trim(),
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          });
        }}
        className="w-full rounded-full bg-foreground py-4 text-[15px] font-semibold text-background transition-opacity disabled:opacity-40"
      >
        {mutation.isPending ? "Сохраняем..." : "Начать"}
      </button>
    </div>
  );
}