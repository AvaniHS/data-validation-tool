export type Step = { id: string; label: string };

export function Stepper(props: { steps: Step[]; activeStepId: string }) {
  const { steps, activeStepId } = props;
  return (
    <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
      {steps.map((s, idx) => {
        const active = s.id === activeStepId;
        return (
          <div
            key={s.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 10px",
              borderRadius: 999,
              border: "1px solid",
              borderColor: active ? "#2563eb" : "#e5e7eb",
              background: active ? "#eff6ff" : "white",
            }}
          >
            <span
              style={{
                width: 20,
                height: 20,
                borderRadius: 999,
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 12,
                fontWeight: 600,
                color: active ? "white" : "#111827",
                background: active ? "#2563eb" : "#f3f4f6",
              }}
            >
              {idx + 1}
            </span>
            <span style={{ fontSize: 13, fontWeight: 600, color: "#111827" }}>{s.label}</span>
          </div>
        );
      })}
    </div>
  );
}

