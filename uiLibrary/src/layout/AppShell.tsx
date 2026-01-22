import type { ReactNode } from "react";

export function AppShell(props: {
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  const { title, children, footer } = props;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", width: "100%", minWidth: 0, overflow: "hidden" }}>
      <header
        style={{
          position: "sticky",
          top: 0,
          background: "white",
          borderBottom: "1px solid #e5e7eb",
          padding: "12px 16px",
          zIndex: 10,
          width: "100%",
          flexShrink: 0,
        }}
      >
        <div style={{ fontSize: 16, fontWeight: 600, maxWidth: 1200, margin: "0 auto" }}>{title}</div>
      </header>

      <main style={{ flex: 1, padding: 16, maxWidth: 1200, width: "100%", minWidth: 0, margin: "0 auto", boxSizing: "border-box", overflow: "hidden", flexShrink: 0 }}>
        {children}
      </main>

      {footer ? (
        <footer style={{ borderTop: "1px solid #e5e7eb", padding: 12, background: "white" }}>
          <div style={{ maxWidth: 1200, margin: "0 auto" }}>{footer}</div>
        </footer>
      ) : null}
    </div>
  );
}

