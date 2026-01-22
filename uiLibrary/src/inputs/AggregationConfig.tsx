import { Select } from "./Select";
import { TextField } from "./TextField";

export type AggregationConfig = {
  file1_columns?: {
    sum?: string[];
    avg?: string[];
    count?: string[];
    min?: string[];
    max?: string[];
  };
  file1_groupby_columns?: string[];
  file2_columns?: {
    sum?: string[];
    avg?: string[];
    count?: string[];
    min?: string[];
    max?: string[];
  };
  file2_groupby_columns?: string[];
  final_aggregated_columns?: {
    sum?: string[];
    avg?: string[];
    count?: string[];
    min?: string[];
    max?: string[];
  };
  final_groupby_columns?: string[];
};

type AggregationSectionProps = {
  title: string;
  columns: string[];
  aggregationColumns: {
    sum: string[];
    avg: string[];
    count: string[];
    min: string[];
    max: string[];
  };
  onAggregationChange: (type: "sum" | "avg" | "count" | "min" | "max", columns: string[]) => void;
};

function AggregationSection({
  title,
  columns,
  aggregationColumns,
  onAggregationChange,
}: AggregationSectionProps) {
  const aggregationTypes: Array<{ key: "sum" | "avg" | "count" | "min" | "max"; label: string }> = [
    { key: "sum", label: "Sum" },
    { key: "avg", label: "Average" },
    { key: "count", label: "Count" },
    { key: "min", label: "Minimum" },
    { key: "max", label: "Maximum" },
  ];

  const handleColumnAdd = (type: "sum" | "avg" | "count" | "min" | "max", column: string) => {
    const current = aggregationColumns[type] || [];
    if (!current.includes(column)) {
      onAggregationChange(type, [...current, column]);
    }
  };

  const handleColumnRemove = (type: "sum" | "avg" | "count" | "min" | "max", column: string) => {
    const current = aggregationColumns[type] || [];
    onAggregationChange(type, current.filter((c) => c !== column));
  };

  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#f9fafb" }}>
      <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 16, color: "#111827" }}>{title}</div>
      <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 16 }}>
        All columns not specified for aggregation will be automatically used as group by columns.
      </div>

      <div style={{ display: "grid", gap: 12 }}>
        {aggregationTypes.map(({ key, label }) => {
          const selectedCols = aggregationColumns[key] || [];
          const availableCols = columns.filter((c) => !selectedCols.includes(c));
          
          return (
            <div key={key} style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: 12, background: "#fff" }}>
              <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8, color: "#374151" }}>{label}</div>
              <Select
                label=""
                value=""
                options={[
                  { label: `Select column for ${label.toLowerCase()}...`, value: "" },
                  ...availableCols.map((c) => ({ label: c, value: c })),
                ]}
                onChange={(v: string) => {
                  if (v) handleColumnAdd(key, v);
                }}
              />
              {selectedCols.length > 0 ? (
                <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {selectedCols.map((col) => (
                    <div
                      key={col}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 6,
                        padding: "4px 8px",
                        background: "#f3f4f6",
                        border: "1px solid #d1d5db",
                        borderRadius: 6,
                        fontSize: 12,
                      }}
                    >
                      <span>{col}</span>
                      <button
                        type="button"
                        onClick={() => handleColumnRemove(key, col)}
                        style={{
                          background: "none",
                          border: "none",
                          cursor: "pointer",
                          color: "#ef4444",
                          fontSize: 14,
                          padding: 0,
                          width: 16,
                          height: 16,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function AggregationConfig({
  file1Columns,
  file2Columns,
  config,
  onChange,
}: {
  file1Columns: string[];
  file2Columns: string[];
  config: AggregationConfig | string | undefined;
  onChange: (config: AggregationConfig | "NA") => void;
}) {
  if (typeof config === "string" && config === "NA") {
    return (
      <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#f9fafb" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 4, color: "#111827" }}>Aggregation</div>
            <div style={{ fontSize: 14, color: "#6b7280" }}>
              Aggregation is disabled. All non-aggregated columns will be auto-grouped by default.
            </div>
          </div>
          <button
            type="button"
            onClick={() => onChange({})}
            style={{
              padding: "8px 16px",
              background: "#2563eb",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
              fontSize: 14,
              fontWeight: 600,
            }}
          >
            Enable Aggregation
          </button>
        </div>
      </div>
    );
  }

  const aggConfig = (typeof config === "object" && config ? config : {}) as AggregationConfig;

  const createUpdateColumns = (key: "file1_columns" | "file2_columns" | "final_aggregated_columns") =>
    (type: "sum" | "avg" | "count" | "min" | "max", columns: string[]) => {
      onChange({
        ...aggConfig,
        [key]: {
          ...aggConfig[key],
          [type]: columns.length > 0 ? columns : undefined,
        },
      });
    };

  const updateFile1Columns = createUpdateColumns("file1_columns");
  const updateFile2Columns = createUpdateColumns("file2_columns");
  const updateFinalColumns = createUpdateColumns("final_aggregated_columns");

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 4, color: "#111827" }}>Aggregation Configuration</div>
          <div style={{ fontSize: 14, color: "#6b7280" }}>
            Configure how columns are aggregated. All non-aggregated columns will be auto-grouped by default.
          </div>
        </div>
        <button
          type="button"
          onClick={() => onChange("NA")}
          style={{
            padding: "8px 16px",
            background: "#ef4444",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: 14,
            fontWeight: 600,
          }}
        >
          Disable Aggregation
        </button>
      </div>

      <div style={{ display: "grid", gap: 16 }}>
        <AggregationSection
          title="File 1 Aggregation"
          columns={file1Columns}
          aggregationColumns={{
            sum: aggConfig.file1_columns?.sum || [],
            avg: aggConfig.file1_columns?.avg || [],
            count: aggConfig.file1_columns?.count || [],
            min: aggConfig.file1_columns?.min || [],
            max: aggConfig.file1_columns?.max || [],
          }}
          onAggregationChange={updateFile1Columns}
        />

        <AggregationSection
          title="File 2 Aggregation"
          columns={file2Columns}
          aggregationColumns={{
            sum: aggConfig.file2_columns?.sum || [],
            avg: aggConfig.file2_columns?.avg || [],
            count: aggConfig.file2_columns?.count || [],
            min: aggConfig.file2_columns?.min || [],
            max: aggConfig.file2_columns?.max || [],
          }}
          onAggregationChange={updateFile2Columns}
        />

        <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#f9fafb" }}>
          <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 16, color: "#111827" }}>Final Aggregation (After Join)</div>
          <div style={{ fontSize: 14, color: "#6b7280", marginBottom: 16 }}>
            Configure final aggregation after datasets are joined. Enter column names manually as they may have different names after the join.
            All columns not specified for aggregation will be automatically used as group by columns.
          </div>
          <div style={{ display: "grid", gap: 12 }}>
            {(["sum", "avg", "count", "min", "max"] as const).map((type) => {
              const label = type === "sum" ? "Sum" : type === "avg" ? "Average" : type === "count" ? "Count" : type === "min" ? "Minimum" : "Maximum";
              const cols = aggConfig.final_aggregated_columns?.[type] || [];
              return (
                <div key={type} style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: 12, background: "#fff" }}>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8, color: "#374151" }}>{label}</div>
                  <TextField
                    label=""
                    value={cols.join(", ")}
                    onChange={(v: string) => {
                      const columnList = v.split(",").map((c) => c.trim()).filter(Boolean);
                      updateFinalColumns(type, columnList);
                    }}
                    placeholder={`Enter column names for ${label.toLowerCase()} separated by commas`}
                  />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
