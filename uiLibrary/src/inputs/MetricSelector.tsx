import { useEffect, useMemo, useRef, useState } from "react";

type SelectOption = { label: string; value: string };

export function MetricSelector({
  label,
  options,
  selected,
  onChange,
}: {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState("");
  const containerRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);

  const displayOptions = useMemo(() => {
    const lowerFilter = filter.trim().toLowerCase();
    const filtered = lowerFilter.length === 0
      ? options
      : options.filter((opt) => opt.toLowerCase().includes(lowerFilter));
    
    return filtered.map((opt) => ({
      label: opt,
      value: opt,
      selected: selected.includes(opt),
    }));
  }, [options, selected, filter]);

  useEffect(() => {
    if (open) {
      setFilter("");
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
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

  const toggleSelection = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

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
        <span style={{ color: selected.length > 0 ? "#111827" : "#9ca3af", fontSize: 14, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1 }}>
          {selected.length > 0 ? `${selected.length} selected` : "Select metrics..."}
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
                      toggleSelection(opt.value);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        toggleSelection(opt.value);
                      }
                    }}
                    style={{
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 10px",
                      borderRadius: 4,
                      border: "none",
                      background: opt.selected ? "#eef2ff" : "transparent",
                      color: "#111827",
                      cursor: "pointer",
                      fontSize: 13,
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      outline: "none",
                    }}
                    onMouseEnter={(e) => {
                      if (!opt.selected) {
                        e.currentTarget.style.background = "#f3f4f6";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!opt.selected) {
                        e.currentTarget.style.background = "transparent";
                      }
                    }}
                  >
                    <span style={{ width: 16, height: 16, border: "2px solid #d1d5db", borderRadius: 3, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, background: opt.selected ? "#2563eb" : "white" }}>
                      {opt.selected ? (
                        <span style={{ color: "white", fontSize: 10 }}>✓</span>
                      ) : null}
                    </span>
                    <span>{opt.label}</span>
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
