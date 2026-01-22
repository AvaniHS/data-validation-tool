import type { ReactNode } from "react";

export function Card({ title, helperText, children }: { title?: string; helperText?: string; children: ReactNode }) {
  return (
    <div
      style={{
        background: "white",
        border: "1px solid #e5e7eb",
        borderRadius: 12,
        padding: 20,
        width: "100%",
        minWidth: 0,
        maxWidth: "100%",
        boxSizing: "border-box",
        display: "block",
        overflow: "visible",
        position: "relative",
      }}
    >
      {title ? (
        <div
          style={{
            fontSize: 16,
            fontWeight: 600,
            color: "#111827",
            marginBottom: 16,
          }}
        >
          {title}
        </div>
      ) : null}
      {helperText ? (
        <div
          style={{
            fontSize: 12,
            color: "#6b7280",
            marginTop: 4,
            marginBottom: 16,
          }}
        >
          {helperText}
        </div>
      ) : null}
      {children}
    </div>
  );
}
