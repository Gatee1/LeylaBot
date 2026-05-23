export function AnimatedBackground() {
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      {/* base gradient */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(120% 80% at 50% 0%, oklch(0.10 0 0) 0%, oklch(0.04 0 0) 60%, oklch(0.03 0 0) 100%)",
        }}
      />
      {/* aurora blob 1 — cold */}
      <div
        className="absolute -top-32 left-1/2 h-[60vh] w-[80vw] -translate-x-1/2 rounded-full opacity-40 blur-3xl"
        style={{
          background:
            "radial-gradient(closest-side, oklch(0.55 0.18 260 / 0.55), transparent 70%)",
          animation: "aurora-drift 18s ease-in-out infinite",
        }}
      />
      {/* aurora blob 2 — warm */}
      <div
        className="absolute bottom-[-20vh] right-[-10vw] h-[55vh] w-[70vw] rounded-full opacity-30 blur-3xl"
        style={{
          background:
            "radial-gradient(closest-side, oklch(0.62 0.21 18 / 0.5), transparent 70%)",
          animation: "aurora-drift-2 22s ease-in-out infinite",
        }}
      />
      {/* aurora blob 3 — accent */}
      <div
        className="absolute top-1/3 -left-20 h-[40vh] w-[60vw] rounded-full opacity-25 blur-3xl"
        style={{
          background:
            "radial-gradient(closest-side, oklch(0.7 0.16 170 / 0.4), transparent 70%)",
          animation: "aurora-drift 26s ease-in-out infinite reverse",
        }}
      />
      {/* floating dust particles */}
      {Array.from({ length: 14 }).map((_, i) => {
        const left = (i * 37) % 100;
        const top = (i * 53) % 100;
        const delay = (i % 7) * 0.6;
        const size = (i % 3) + 2;
        return (
          <span
            key={i}
            className="absolute rounded-full bg-foreground/30"
            style={{
              left: `${left}%`,
              top: `${top}%`,
              width: size,
              height: size,
              animation: `float-slow ${6 + (i % 5)}s ease-in-out ${delay}s infinite`,
            }}
          />
        );
      })}
      {/* grain / vignette */}
      <div
        className="absolute inset-0 opacity-[0.06] mix-blend-overlay"
        style={{
          backgroundImage:
            "radial-gradient(rgba(255,255,255,.7) 1px, transparent 1px)",
          backgroundSize: "3px 3px",
        }}
      />
    </div>
  );
}