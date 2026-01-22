import type { DragEvent } from "react";
import { useCallback, useRef, useState } from "react";

export function FileDropzone(props: {
  label: string;
  accept?: string;
  onFileSelected: (file: File) => void;
  helperText?: string;
  disabled?: boolean;
}) {
  const { label, accept, onFileSelected, helperText, disabled } = props;
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const openPicker = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const onDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) onFileSelected(file);
    },
    [onFileSelected]
  );

  return (
    <div style={{ display: "grid", gap: 6 }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: "#111827" }}>{label}</div>
      <div
        onClick={disabled ? undefined : openPicker}
        onDragEnter={(e) => {
          if (disabled) return;
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragOver={(e) => {
          if (disabled) return;
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={(e) => {
          if (disabled) return;
          e.preventDefault();
          setIsDragging(false);
        }}
        onDrop={disabled ? undefined : onDrop}
        role="button"
        tabIndex={disabled ? -1 : 0}
        style={{
          padding: 16,
          borderRadius: 10,
          border: `2px dashed ${isDragging && !disabled ? "#2563eb" : "#d1d5db"}`,
          background: disabled ? "#f3f4f6" : isDragging ? "#eff6ff" : "white",
          cursor: disabled ? "not-allowed" : "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          opacity: disabled ? 0.6 : 1,
        }}
      >
        <div style={{ display: "grid", gap: 4 }}>
          <div style={{ fontWeight: 600, color: "#111827" }}>Drop a file here, or click to browse</div>
          {helperText ? <div style={{ fontSize: 12, color: "#6b7280" }}>{helperText}</div> : null}
        </div>
        <div style={{ fontSize: 12, color: "#6b7280" }}>{accept ?? "any"}</div>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        disabled={disabled}
        style={{ display: "none" }}
        onChange={(e) => {
          if (disabled) return;
          const file = e.target.files?.[0];
          if (file) onFileSelected(file);
          e.target.value = "";
        }}
      />
    </div>
  );
}

