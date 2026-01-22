import type { ReactNode } from "react";

export function StepContainer({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr",
        gap: 20,
        width: "100%",
        minWidth: 0,
        minHeight: "calc(100vh - 250px)",
        maxHeight: "calc(100vh - 250px)",
        overflowY: "auto",
        boxSizing: "border-box",
        alignContent: "start",
      }}
    >
      {children}
    </div>
  );
}
