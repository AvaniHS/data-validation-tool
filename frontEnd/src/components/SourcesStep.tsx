import { Card, FileDropzone, Select, StepContainer, TextField } from "ui";
import type { ParsedDataset } from "../app/parsing/fileParsing";
import type { ValidationConfig } from "../app/config/types";
import "../styles/sources-step.css";

interface SourcesStepProps {
  config: ValidationConfig;
  file1Type: string;
  file2Type: string;
  file1: ParsedDataset | null;
  file2: ParsedDataset | null;
  file1SheetOptions: Array<{ label: string; value: string }>;
  file2SheetOptions: Array<{ label: string; value: string }>;
  useSourceFileForOutput: boolean;
  onConfigChange: (updater: (c: ValidationConfig) => ValidationConfig) => void;
  onFile1TypeChange: (type: string) => void;
  onFile2TypeChange: (type: string) => void;
  onUploadDataset1: (file: File) => Promise<void>;
  onUploadDataset2: (file: File) => Promise<void>;
  onUseSourceFileForOutputChange: (checked: boolean) => void;
}

export function SourcesStep({
  config,
  file1Type,
  file2Type,
  file1,
  file2,
  file1SheetOptions,
  file2SheetOptions,
  useSourceFileForOutput,
  onConfigChange,
  onFile1TypeChange,
  onFile2TypeChange,
  onUploadDataset1,
  onUploadDataset2,
  onUseSourceFileForOutputChange,
}: SourcesStepProps) {
  const deriveFileFormat = (type1: string, type2: string, numberOfFiles: number): string => {
    if (numberOfFiles === 1) return type1 || ".xlsx";
    if (!type1 || !type2) return "mixed";
    return type1 === type2 ? type1 : "mixed";
  };

  return (
    <StepContainer>
      <Card title="Setup">
        <div className="setup-grid">
          <Select
            label="Number of files"
            value={String(config.number_of_files || 1)}
            options={[
              { label: "1 file (two sheets)", value: "1" },
              { label: "2 files", value: "2" },
            ]}
            onChange={(v) => {
              const num = Number(v) === 2 ? 2 : 1;
              onConfigChange((c) => ({
                ...c,
                number_of_files: num,
                file_format: deriveFileFormat(num === 1 ? ".xlsx" : file1Type, file2Type, num),
                file2_path: num === 1 ? "NA" : c.file2_path,
                file2_sheet: num === 1 ? "NA" : c.file2_sheet,
              }));
              if (num === 1) {
                onFile1TypeChange(".xlsx");
              }
            }}
          />
          <Select
            label="File 1 type"
            value={file1Type}
            disabled={config.number_of_files === 1}
            options={[
              { label: "CSV", value: ".csv" },
              { label: "Excel", value: ".xlsx" },
              { label: "JSON", value: ".json" },
            ]}
            onChange={(v) => {
              onFile1TypeChange(v);
              onFile2TypeChange(v);
              onConfigChange((c) => ({ ...c, file_format: deriveFileFormat(v, v, c.number_of_files || 1) }));
            }}
          />
          <Select
            label="File 2 type"
            value={file2Type}
            disabled={config.number_of_files === 1}
            options={[
              { label: "CSV", value: ".csv" },
              { label: "Excel", value: ".xlsx" },
              { label: "JSON", value: ".json" },
            ]}
            onChange={(v) => {
              onFile2TypeChange(v);
              onConfigChange((c) => ({ ...c, file_format: deriveFileFormat(file1Type, v, 2) }));
            }}
          />
        </div>
        {config.number_of_files === 1 ? (
          <div className="helperText">Excel (.xlsx) only - two sheets in one file. File 2 options are disabled.</div>
        ) : null}
      </Card>

      <Card title="Upload Files">
        <div className="responsive-grid-2 upload-files-grid">
          <FileDropzone
            label={config.number_of_files === 1 ? "Upload Excel file" : "File 1"}
            accept=".csv,.xlsx,.xls,.json"
            onFileSelected={onUploadDataset1}
          />
          <FileDropzone
            label="File 2"
            accept=".csv,.xlsx,.xls,.json"
            onFileSelected={onUploadDataset2}
            disabled={config.number_of_files === 1}
          />
        </div>
        <div className="responsive-grid-2 file-paths">
          <TextField
            label="File 1 Path"
            value={config.file1_path || ""}
            onChange={(v: string) => {
              onConfigChange((c) => {
                const updated = { ...c, file1_path: v };
                if (useSourceFileForOutput && (c.file_format === ".xlsx" || c.number_of_files === 1)) {
                  updated.output_path = v;
                }
                return updated;
              });
            }}
            placeholder="Enter file path or use uploaded file name"
          />
          <TextField
            label="File 2 Path"
            value={config.file2_path || ""}
            onChange={(v: string) => onConfigChange((c) => ({ ...c, file2_path: v }))}
            placeholder="Enter file path or use uploaded file name"
            disabled={config.number_of_files === 1}
          />
        </div>
        <div className="helperText">
          Note: Browser security prevents access to full file paths. The file name is auto-filled when you upload.
          Please update the path to the absolute file path on your system if needed.
        </div>
      </Card>

      {(file1?.kind === "xlsx" || file2?.kind === "xlsx") ? (
        <Card title="Sheet Names">
          <div className="responsive-grid-2 sheet-names-grid">
            {file1SheetOptions.length ? (
              <Select
                label="Sheet 1"
                value={config.file1_sheet1 ?? ""}
                options={[{ label: "Select sheet", value: "" }, ...file1SheetOptions]}
                onChange={(v) => onConfigChange((c) => ({ ...c, file1_sheet1: v }))}
              />
            ) : (
              <TextField
                label="Sheet 1"
                value={config.file1_sheet1 ?? ""}
                onChange={(v: string) => onConfigChange((c) => ({ ...c, file1_sheet1: v }))}
                placeholder="Enter sheet name"
              />
            )}

            {file2SheetOptions.length ? (
              <Select
                label={config.number_of_files === 1 ? "Sheet 2" : "File 2 Sheet"}
                value={config.number_of_files === 1 ? config.file1_sheet2 ?? "" : config.file2_sheet ?? ""}
                options={[{ label: "Select sheet", value: "" }, ...file2SheetOptions]}
                onChange={(v) =>
                  onConfigChange((c) =>
                    c.number_of_files === 1 ? { ...c, file1_sheet2: v } : { ...c, file2_sheet: v }
                  )
                }
                disabled={config.number_of_files === 2 && !file2}
              />
            ) : (
              <TextField
                label={config.number_of_files === 1 ? "Sheet 2" : "File 2 Sheet"}
                value={config.number_of_files === 1 ? config.file1_sheet2 ?? "" : config.file2_sheet ?? ""}
                onChange={(v: string) =>
                  onConfigChange((c) => (c.number_of_files === 1 ? { ...c, file1_sheet2: v } : { ...c, file2_sheet: v }))
                }
                placeholder="Enter sheet name"
                disabled={config.number_of_files === 2 && !file2}
              />
            )}
          </div>
        </Card>
      ) : null}

      <Card title="Output Settings">
        <div className="output-settings">
          {config.number_of_files === 1 ? (
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="useSourceFile"
                checked={useSourceFileForOutput}
                onChange={(e) => {
                  const checked = e.target.checked;
                  onUseSourceFileForOutputChange(checked);
                  if (checked) {
                    onConfigChange((c) => ({
                      ...c,
                      output_path: c.file1_path || "",
                      output_sheet: c.output_sheet || "ValidationSummary",
                    }));
                  }
                }}
                className="checkbox-input"
              />
              <label htmlFor="useSourceFile" className="checkbox-label">
                Use source file for output report
              </label>
            </div>
          ) : config.number_of_files === 2 && (file1Type === ".xlsx" || file2Type === ".xlsx") ? (
            <Select
              label="Output Source"
              value={useSourceFileForOutput ? (config.output_path === config.file1_path ? "file1" : config.output_path === config.file2_path ? "file2" : "custom") : "custom"}
              options={[
                { label: "Custom output path", value: "custom" },
                ...(file1Type === ".xlsx" ? [{ label: "Use File 1", value: "file1" }] : []),
                ...(file2Type === ".xlsx" ? [{ label: "Use File 2", value: "file2" }] : []),
              ]}
              onChange={(v) => {
                if (v === "file1" && file1Type === ".xlsx") {
                  onUseSourceFileForOutputChange(true);
                  onConfigChange((c) => ({
                    ...c,
                    output_path: c.file1_path || "",
                    output_sheet: c.output_sheet || "ValidationSummary",
                  }));
                } else if (v === "file2" && file2Type === ".xlsx") {
                  onUseSourceFileForOutputChange(true);
                  onConfigChange((c) => ({
                    ...c,
                    output_path: c.file2_path || "",
                    output_sheet: c.output_sheet || "ValidationSummary",
                  }));
                } else {
                  onUseSourceFileForOutputChange(false);
                }
              }}
            />
          ) : null}

          {config.number_of_files === 2 ? (
            <>
              <TextField
                label="Output Path"
                value={config.output_path || ""}
                onChange={(v: string) => {
                  onConfigChange((c) => ({ ...c, output_path: v }));
                  const file1IsExcel = file1Type === ".xlsx";
                  const file2IsExcel = file2Type === ".xlsx";
                  if (file1IsExcel || file2IsExcel) {
                    if (v === config.file1_path || v === config.file2_path) {
                      onUseSourceFileForOutputChange(true);
                    } else {
                      onUseSourceFileForOutputChange(false);
                    }
                  } else {
                    onUseSourceFileForOutputChange(false);
                  }
                }}
                placeholder="Enter output file path (e.g., results/comparison.xlsx or results/comparison.csv)"
                disabled={false}
              />
              {(() => {
                const outputPath = config.output_path || "";
                const isExcelOutput = outputPath.toLowerCase().endsWith(".xlsx") || outputPath.toLowerCase().endsWith(".xls");
                const file1IsExcel = file1Type === ".xlsx";
                const file2IsExcel = file2Type === ".xlsx";
                const shouldShowSheet = isExcelOutput || file1IsExcel || file2IsExcel || useSourceFileForOutput;
                return shouldShowSheet ? (
                  <TextField
                    label="Output Sheet Name"
                    value={config.output_sheet || ""}
                    onChange={(v: string) => onConfigChange((c) => ({ ...c, output_sheet: v }))}
                    placeholder="Enter sheet name (e.g., ValidationSummary)"
                  />
                ) : null;
              })()}
            </>
          ) : !useSourceFileForOutput ? (
            <>
              <TextField
                label="Output Path"
                value={config.output_path || ""}
                onChange={(v: string) => onConfigChange((c) => ({ ...c, output_path: v }))}
                placeholder="Enter output file path (e.g., results/comparison.xlsx)"
              />
              {(() => {
                const outputPath = config.output_path || "";
                const isExcelOutput = outputPath.toLowerCase().endsWith(".xlsx") || outputPath.toLowerCase().endsWith(".xls");
                const shouldShowSheet = isExcelOutput || config.file_format === ".xlsx";
                return shouldShowSheet ? (
                  <TextField
                    label="Output Sheet Name"
                    value={config.output_sheet || ""}
                    onChange={(v: string) => onConfigChange((c) => ({ ...c, output_sheet: v }))}
                    placeholder="Enter sheet name (e.g., ValidationSummary)"
                  />
                ) : null;
              })()}
            </>
          ) : (
            <TextField
              label="Output Sheet Name"
              value={config.output_sheet || ""}
              onChange={(v: string) => onConfigChange((c) => ({ ...c, output_sheet: v }))}
              placeholder="Enter sheet name (e.g., ValidationSummary)"
            />
          )}
        </div>
        {useSourceFileForOutput ? (
          <div className="helperText">
            {config.number_of_files === 1 ? (
              <>Output will be written to the source file ({config.file1_path || "file1"}) in a new sheet.</>
            ) : (
              <>Output will be written to {config.output_path === config.file1_path ? "File 1" : "File 2"} ({config.output_path || "source file"}) in a new sheet.</>
            )}
          </div>
        ) : config.number_of_files === 2 ? (
          <div className="helperText">
            Specify the output file path. If the output format is Excel (.xlsx), you can also specify a sheet name.
          </div>
        ) : null}
      </Card>
    </StepContainer>
  );
}
