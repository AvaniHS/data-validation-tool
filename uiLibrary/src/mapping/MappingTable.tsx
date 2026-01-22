import { useEffect, useMemo, useRef, useState } from "react";

export type MappingRow = { left?: string; right?: string };
type SelectOption = { label: string; value: string };

export function MappingTable(props: {
  title: string;
  leftLabel: string;
  rightLabel: string;
  leftOptions: string[];
  rightOptions: string[];
  rows: MappingRow[];
  onChange: (rows: MappingRow[]) => void;
}) {
  const { title, leftLabel, rightLabel, leftOptions, rightOptions, rows, onChange } = props;

  const buildOptions = (
    options: string[] | undefined,
    allRows: MappingRow[],
    currentIndex: number,
    side: "left" | "right",
    filter: string
  ): SelectOption[] => {
    const safeOptions = options ?? [];
    
    if (safeOptions.length === 0) {
      return [{ label: "Select...", value: "" }];
    }
    
    const currentValue = side === "left" ? allRows[currentIndex]?.left : allRows[currentIndex]?.right;
    const used = new Set(
      allRows
        .map((r, idx) => (idx === currentIndex ? undefined : side === "left" ? r.left : r.right))
        .filter(Boolean) as string[]
    );
    const lowerFilter = filter.trim().toLowerCase();
    const pool = safeOptions.filter((c) => !used.has(c));
    
    let source: string[];
    if (lowerFilter.length === 0) {
      source = pool;
    } else {
      source = pool.filter((c) => c.toLowerCase().includes(lowerFilter));
    }
    
    const optionList: SelectOption[] = source.map((c) => ({ label: c, value: c }));
    if (currentValue && !optionList.find((o) => o.value === currentValue)) {
      optionList.unshift({ label: currentValue, value: currentValue });
    }
    
    return [{ label: "Select...", value: "" }, ...optionList];
  };

  const updateRow = (idx: number, patch: MappingRow) => {
    const next = rows.map((r, i) => (i === idx ? { ...r, ...patch } : r));
    onChange(next);
  };

  const addRow = () => onChange([...rows, {}]);
  const removeRow = (idx: number) => onChange(rows.filter((_, i) => i !== idx));

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, overflow: "visible" }}>
      <div style={{ padding: 12, borderBottom: "1px solid #e5e7eb", background: "#f9fafb", fontWeight: 700 }}>
        {title}
      </div>

      <div style={{ padding: 12, display: "grid", gap: 10 }}>
        {rows.map((row, idx) => (
          <div
            key={`row-${idx}-${row.left || ""}-${row.right || ""}`}
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr auto",
              gap: 10,
              alignItems: "end",
            }}
          >
            <SearchableSelect
              key={`left-${idx}-${leftOptions.length}`}
              label={leftLabel}
              value={row.left ?? ""}
              build={(filter) => buildOptions(leftOptions, rows, idx, "left", filter)}
              onChange={(v) => {
                const newValue = v === "" ? undefined : v;
                updateRow(idx, { left: newValue });
              }}
            />
            <SearchableSelect
              key={`right-${idx}-${rightOptions.length}`}
              label={rightLabel}
              value={row.right ?? ""}
              build={(filter) => buildOptions(rightOptions, rows, idx, "right", filter)}
              onChange={(v) => {
                const newValue = v === "" ? undefined : v;
                updateRow(idx, { right: newValue });
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
            Add row
          </button>
        </div>
      </div>
    </div>
  );
}

function SearchableSelect({
  label,
  value,
  build,
  onChange,
}: {
  label: string;
  value: string;
  build: (filter: string) => SelectOption[];
  onChange: (value: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState("");
  const containerRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);
  
  const displayOptions = useMemo(() => {
    try {
      const options = build(filter);
      if (!options || !Array.isArray(options) || options.length === 0) {
        return [{ label: "Select...", value: "" }];
      }
      return options;
    } catch (e) {
      return [{ label: "Select...", value: "" }];
    }
  }, [build, filter]);

  useEffect(() => {
    if (open) {
      setFilter("");
      setTimeout(() => {
        if (listRef.current) {
          listRef.current.scrollTop = 0;
        }
      }, 0);
    }
  }, [open]);

  useEffect(() => {
    const onClickAway = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setFilter("");
      }
    };
    if (open) {
      document.addEventListener("mousedown", onClickAway);
      return () => document.removeEventListener("mousedown", onClickAway);
    }
  }, [open]);

  useEffect(() => {
    if (filter && listRef.current) {
      listRef.current.scrollTop = 0;
    }
  }, [filter]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setOpen(false);
      setFilter("");
    } else if (e.key === "ArrowDown" && open && displayOptions.length > 0) {
      e.preventDefault();
      const firstButton = listRef.current?.querySelector("button") as HTMLButtonElement;
      firstButton?.focus();
    }
  };

  return (
    <div ref={containerRef} style={{ position: "relative", display: "grid", gap: 6, width: "100%", zIndex: open ? 1000 : "auto" }}>
      <span style={{ fontSize: 12, fontWeight: 600, color: "#111827" }}>{label}</span>
      <div
        role="button"
        tabIndex={0}
        onClick={() => setOpen((o) => !o)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            setOpen((o) => !o);
          }
        }}
        style={{
          padding: "10px 12px",
          border: "1px solid #d1d5db",
          borderRadius: 8,
          background: "white",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 8,
          minHeight: 40,
        }}
      >
        <span style={{ color: value ? "#111827" : "#9ca3af", fontSize: 14, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1 }}>
          {value || "Select..."}
        </span>
        <span style={{ fontSize: 12, color: "#6b7280", flexShrink: 0 }}>▾</span>
      </div>

      {open ? (
        <div
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            marginTop: 6,
            border: "1px solid #d1d5db",
            borderRadius: 8,
            background: "white",
            boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
            zIndex: 1001,
            padding: 8,
            display: "flex",
            flexDirection: "column",
            gap: 8,
            maxHeight: 320,
            overflow: "visible",
            minHeight: 50,
          }}
        >
          <input
            ref={inputRef}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type to search..."
            style={{
              padding: "8px 10px",
              border: "1px solid #d1d5db",
              borderRadius: 6,
              fontSize: 12,
              outline: "none",
              width: "100%",
              boxSizing: "border-box",
            }}
            onClick={(e) => e.stopPropagation()}
          />
          <div
            ref={listRef}
            style={{
              maxHeight: 240,
              minHeight: 40,
              overflowY: "auto",
              overflowX: "hidden",
              display: "flex",
              flexDirection: "column",
              gap: 2,
              width: "100%",
            }}
          >
            {displayOptions && Array.isArray(displayOptions) ? (
              displayOptions.length > 0 ? (
                displayOptions.map((opt) => (
                <button
                  type="button"
                  key={opt.value}
                  onClick={(e) => {
                    e.stopPropagation();
                    onChange(opt.value);
                    setOpen(false);
                    setFilter("");
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      onChange(opt.value);
                      setOpen(false);
                      setFilter("");
                    }
                  }}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    padding: "8px 10px",
                    borderRadius: 4,
                    border: "none",
                    background: opt.value === value ? "#eef2ff" : "transparent",
                    color: "#111827",
                    cursor: "pointer",
                    fontSize: 13,
                    display: "flex",
                    alignItems: "center",
                    outline: "none",
                  }}
                  onMouseEnter={(e) => {
                    if (opt.value !== value) {
                      e.currentTarget.style.background = "#f3f4f6";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (opt.value !== value) {
                      e.currentTarget.style.background = "transparent";
                    }
                  }}
                >
                  {opt.label}
                </button>
              ))
              ) : (
                <div style={{ padding: "16px", color: "#6b7280", fontSize: 12, textAlign: "center" }}>
                  No options available
                </div>
              )
            ) : (
              <div style={{ padding: "16px", color: "#6b7280", fontSize: 12, textAlign: "center" }}>
                Loading...
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
