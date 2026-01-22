import type { ReactNode } from "react";

export function InlineAlert(props: { title: string; children?: ReactNode; variant: "info" | "warning" | "error" }) {
  const { title, children, variant } = props;
  const colors = {
    info: { bg: "#eff6ff", border: "#93c5fd", text: "#1e3a8a" },
    warning: { bg: "#fffbeb", border: "#fcd34d", text: "#92400e" },
    error: { bg: "#fef2f2", border: "#fca5a5", text: "#991b1b" },
  }[variant];

  return (
    <div
      style={{
        border: `1px solid ${colors.border}`,
        background: colors.bg,
        color: colors.text,
        borderRadius: 10,
        padding: 12,
        display: "grid",
        gap: 6,
      }}
    >
      <div style={{ fontWeight: 700 }}>{title}</div>
      {children ? <div style={{ fontSize: 13 }}>{children}</div> : null}
    </div>
  );
}

