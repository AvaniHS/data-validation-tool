import { Select } from "./Select";

export type AdditionalColumnRow = { column?: string };

export function AdditionalColumnsTable({
  label,
  options,
  rows,
  onChange,
}: {
  label: string;
  options: string[];
  rows: AdditionalColumnRow[];
  onChange: (rows: AdditionalColumnRow[]) => void;
}) {
  const updateRow = (idx: number, patch: AdditionalColumnRow) => {
    const next = rows.map((r, i) => (i === idx ? { ...r, ...patch } : r));
    onChange(next);
  };

  const addRow = () => onChange([...rows, {}]);
  const removeRow = (idx: number) => onChange(rows.filter((_, i) => i !== idx));

  const buildColumnOptions = (allRows: AdditionalColumnRow[], currentIndex: number): Array<{ label: string; value: string }> => {
    const used = new Set(
      allRows
        .map((r, idx) => (idx === currentIndex ? undefined : r.column))
        .filter(Boolean) as string[]
    );
    const currentValue = allRows[currentIndex]?.column;
    const available = options.filter((c) => !used.has(c));
    const optionList = available.map((c) => ({ label: c, value: c }));
    
    if (currentValue && !optionList.find((o) => o.value === currentValue)) {
      optionList.unshift({ label: currentValue, value: currentValue });
    }
    
    return [{ label: "Select column...", value: "" }, ...optionList];
  };

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, overflow: "visible" }}>
      <div style={{ padding: 12, borderBottom: "1px solid #e5e7eb", background: "#f9fafb", fontWeight: 700 }}>
        {label}
      </div>

      <div style={{ padding: 12, display: "grid", gap: 10 }}>
        {rows.map((row, idx) => (
          <div
            key={`row-${idx}-${row.column || ""}`}
            style={{
              display: "grid",
              gridTemplateColumns: "1fr auto",
              gap: 10,
              alignItems: "end",
            }}
          >
            <Select
              label="Column"
              value={row.column ?? ""}
              options={buildColumnOptions(rows, idx)}
              onChange={(v: string) => {
                const newValue = v === "" ? undefined : v;
                updateRow(idx, { column: newValue });
              }}
            />
            <button
              type="button"
              onClick={() => removeRow(idx)}
              style={{
                height: 40,
                padding: "0 12px",
                borderRadius: 8,
                border: "1px solid #e5e7eb",
                background: "white",
                cursor: "pointer",
              }}
            >
              Remove
            </button>
          </div>
        ))}

        <div>
          <button
            type="button"
            onClick={addRow}
            style={{
              height: 40,
              padding: "0 12px",
              borderRadius: 8,
              border: "1px solid #2563eb",
              background: "#2563eb",
              color: "white",
              cursor: "pointer",
              fontWeight: 700,
            }}
          >
            Add column
          </button>
        </div>
      </div>
    </div>
  );
}
