export function ConfigPreview({ config }: { config: object }) {
  return (
    <div style={{ width: "100%", minWidth: 0, overflow: "hidden" }}>
      <pre
        style={{
          background: "#f9fafb",
          border: "1px solid #e5e7eb",
          color: "#111827",
          padding: 24,
          borderRadius: 8,
          fontSize: 13,
          lineHeight: 1.6,
          minHeight: "calc(100vh - 350px)",
          maxHeight: "calc(100vh - 350px)",
          margin: 0,
          width: "100%",
          minWidth: 0,
          maxWidth: "100%",
          boxSizing: "border-box",
          display: "block",
          whiteSpace: "pre",
          overflowX: "auto",
          overflowY: "auto",
        }}
        className="config-preview-pre"
      >
        {JSON.stringify(config, null, 2)}
      </pre>
    </div>
  );
}
