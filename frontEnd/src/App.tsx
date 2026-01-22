import "./App.css";
import "./responsive.css";
import "./styles/buttons.css";
import "./styles/app.css";
import { useEffect, useMemo, useState } from "react";
import { AppShell, InlineAlert, Stepper } from "ui";
import type { ParsedDataset } from "./app/parsing/fileParsing";
import { parseDataset } from "./app/parsing/fileParsing";
import type { ValidationConfig } from "./app/config/types";
import { downloadJson, downloadPublicFile } from "./app/utils/download";
import { ConsoleLogger } from "./app/utils/logger";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { SourcesStep } from "./components/SourcesStep";
import { MappingStep } from "./components/MappingStep";
import { ReviewStep } from "./components/ReviewStep";
import { useConfigState } from "./hooks/useConfigState";

const log = new ConsoleLogger("app");

type StepId = "sources" | "mapping" | "review";

function App() {
  const steps = useMemo(
    () => [
      { id: "sources", label: "Data sources" },
      { id: "mapping", label: "Mapping & keys" },
      { id: "review", label: "Review & download" },
    ],
    []
  );

  const [activeStepId, setActiveStepId] = useState<StepId>("sources");
  const { config, setConfig, normalizeConfigForCli } = useConfigState();
  const [file1Type, setFile1Type] = useState<string>(".xlsx");
  const [file2Type, setFile2Type] = useState<string>(".xlsx");
  const [file1, setFile1] = useState<ParsedDataset | null>(null);
  const [file2, setFile2] = useState<ParsedDataset | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mappingRows, setMappingRows] = useState<{ left?: string; right?: string }[]>([{}]);
  const [joinRows, setJoinRows] = useState<{ left?: string; right?: string }[]>([{}]);
  const [mappingRowsInitialized, setMappingRowsInitialized] = useState(false);
  const [joinRowsInitialized, setJoinRowsInitialized] = useState(false);
  const [file1Metrics, setFile1Metrics] = useState<string[]>(() => config.file1_metric_list || []);
  const [file2Metrics, setFile2Metrics] = useState<string[]>(() => config.file2_metric_list || []);
  const [useSourceFileForOutput, setUseSourceFileForOutput] = useState<boolean>(() => {
    if (config.number_of_files === 1) {
      return config.output_path === config.file1_path && (config.file_format === ".xlsx" || config.number_of_files === 1);
    } else if (config.number_of_files === 2) {
      const file1IsExcel = file1Type === ".xlsx";
      const file2IsExcel = file2Type === ".xlsx";
      if (file1IsExcel || file2IsExcel) {
        return config.output_path === config.file1_path || config.output_path === config.file2_path;
      }
    }
    return false;
  });

  useEffect(() => {
    if (useSourceFileForOutput) {
      if (config.number_of_files === 1) {
        if (config.file1_path && config.output_path !== config.file1_path) {
          setConfig((c) => ({ ...c, output_path: c.file1_path }));
        }
      } else if (config.number_of_files === 2) {
        const file1IsExcel = file1Type === ".xlsx";
        const file2IsExcel = file2Type === ".xlsx";
        if (file1IsExcel || file2IsExcel) {
          const usingFile1 = config.output_path === config.file1_path;
          const usingFile2 = config.output_path === config.file2_path;
          if (!usingFile1 && !usingFile2) {
            if (file1IsExcel && config.file1_path) {
              setConfig((c) => ({ ...c, output_path: c.file1_path }));
            } else if (file2IsExcel && config.file2_path) {
              setConfig((c) => ({ ...c, output_path: c.file2_path }));
            }
          }
        } else {
          setUseSourceFileForOutput(false);
        }
      }
    }
  }, [useSourceFileForOutput, config.file1_path, config.file2_path, config.file_format, config.number_of_files, file1Type, file2Type, setConfig]);

  const [file1AdditionalColumns, setFile1AdditionalColumns] = useState<Array<{ column?: string }>>(() => {
    const cols = config.additional_columns_file1;
    if (!cols) return [];
    if (Array.isArray(cols)) {
      return cols.map((col) => ({ column: col }));
    }
    return Object.keys(cols).map((column) => ({ column }));
  });
  const [file2AdditionalColumns, setFile2AdditionalColumns] = useState<Array<{ column?: string }>>(() => {
    const cols = config.additional_columns_file2;
    if (!cols) return [];
    if (Array.isArray(cols)) {
      return cols.map((col) => ({ column: col }));
    }
    return Object.keys(cols).map((column) => ({ column }));
  });

  const file1Columns = useMemo(() => getColumnsForConfigSide(file1, config, "file1"), [file1, config]);
  const file2Columns = useMemo(() => getColumnsForConfigSide(file2 ?? file1, config, "file2"), [file2, file1, config]);
  const file1SheetOptions = useMemo(() => (file1?.sheetNames ? file1.sheetNames.map((s) => ({ label: s, value: s })) : []), [file1]);
  const file2SheetOptions = useMemo(() => {
    if (config.number_of_files === 1) return file1SheetOptions;
    return file2?.sheetNames ? file2.sheetNames.map((s) => ({ label: s, value: s })) : [];
  }, [config.number_of_files, file1SheetOptions, file2]);

  useEffect(() => {
    if (!mappingRowsInitialized && config.column_mapping && Object.keys(config.column_mapping).length > 0) {
      const fromConfig = Object.entries(config.column_mapping).map(([left, right]) => ({ left, right }));
      setMappingRows(fromConfig);
      setMappingRowsInitialized(true);
    } else if (!mappingRowsInitialized && (!config.column_mapping || Object.keys(config.column_mapping).length === 0)) {
      setMappingRows([{}]);
      setMappingRowsInitialized(true);
    }
  }, [config.column_mapping, mappingRowsInitialized]);

  useEffect(() => {
    if (!joinRowsInitialized && config.join_keys && Object.keys(config.join_keys).length > 0) {
      const fromConfig = Object.entries(config.join_keys).map(([left, right]) => ({ left, right }));
      setJoinRows(fromConfig);
      setJoinRowsInitialized(true);
    } else if (!joinRowsInitialized && (!config.join_keys || Object.keys(config.join_keys).length === 0)) {
      setJoinRows([{}]);
      setJoinRowsInitialized(true);
    }
  }, [config.join_keys, joinRowsInitialized]);

  const columnMappingRows = mappingRows;
  const joinKeyRows = joinRows;

  const setColumnMappingRows = (rows: { left?: string; right?: string }[]) => {
    setMappingRows(rows);
    setMappingRowsInitialized(true);
    const next: Record<string, string> = {};
    for (const r of rows) {
      if (r.left && r.right) next[r.left] = r.right;
    }
    setConfig((c) => ({ ...c, column_mapping: next }));
  };

  const setJoinKeyRows = (rows: { left?: string; right?: string }[]) => {
    setJoinRows(rows);
    setJoinRowsInitialized(true);
    const next: Record<string, string> = {};
    for (const r of rows) {
      if (r.left && r.right) next[r.left] = r.right;
    }
    setConfig((c) => ({ ...c, join_keys: next }));
  };

  const mappedFile1Columns = useMemo(() => {
    return Object.keys(config.column_mapping || {});
  }, [config.column_mapping]);

  const mappedFile2Columns = useMemo(() => {
    return Object.values(config.column_mapping || {});
  }, [config.column_mapping]);

  const availableFile1Columns = useMemo(() => {
    const mapped = new Set(mappedFile1Columns);
    const joinKeys = new Set(Object.keys(config.join_keys || {}));
    const metrics = new Set(file1Metrics);
    return file1Columns.filter((col) => !mapped.has(col) && !joinKeys.has(col) && !metrics.has(col));
  }, [file1Columns, mappedFile1Columns, config.join_keys, file1Metrics]);

  const availableFile2Columns = useMemo(() => {
    const mapped = new Set(mappedFile2Columns);
    const joinKeys = new Set(Object.values(config.join_keys || {}));
    const metrics = new Set(file2Metrics);
    return file2Columns.filter((col) => !mapped.has(col) && !joinKeys.has(col) && !metrics.has(col));
  }, [file2Columns, mappedFile2Columns, config.join_keys, file2Metrics]);

  const setFile1MetricsWithSync = (metrics: string[]) => {
    setFile1Metrics(metrics);
    const columnMapping = config.column_mapping || {};
    const reverseMapping: Record<string, string> = {};
    Object.entries(columnMapping).forEach(([file1, file2]) => {
      reverseMapping[file2] = file1;
    });

    const newFile2Metrics = file2Metrics.filter((file2Metric) => {
      const file1Mapped = reverseMapping[file2Metric];
      if (!file1Mapped) {
        return true;
      }
      return metrics.includes(file1Mapped);
    });

    metrics.forEach((file1Metric) => {
      const file2Mapped = columnMapping[file1Metric];
      if (file2Mapped && !newFile2Metrics.includes(file2Mapped)) {
        newFile2Metrics.push(file2Mapped);
      }
    });

    setFile2Metrics(newFile2Metrics);
    setConfig((c) => ({
      ...c,
      file1_metric_list: metrics,
      file2_metric_list: newFile2Metrics,
    }));
  };

  const setFile2MetricsWithSync = (metrics: string[]) => {
    setFile2Metrics(metrics);
    const columnMapping = config.column_mapping || {};
    const reverseMapping: Record<string, string> = {};
    Object.entries(columnMapping).forEach(([file1, file2]) => {
      reverseMapping[file2] = file1;
    });

    const newFile1Metrics = file1Metrics.filter((file1Metric) => {
      const file2Mapped = columnMapping[file1Metric];
      if (!file2Mapped) {
        return true;
      }
      return metrics.includes(file2Mapped);
    });

    metrics.forEach((file2Metric) => {
      const file1Mapped = reverseMapping[file2Metric];
      if (file1Mapped && !newFile1Metrics.includes(file1Mapped)) {
        newFile1Metrics.push(file1Mapped);
      }
    });

    setFile1Metrics(newFile1Metrics);
    setConfig((c) => ({
      ...c,
      file1_metric_list: newFile1Metrics,
      file2_metric_list: metrics,
    }));
  };

  const setFile1AdditionalColumnsWithConfig = (rows: Array<{ column?: string }>) => {
    setFile1AdditionalColumns(rows);
    const columnList = rows.filter((r) => r.column).map((r) => r.column!);
    setConfig((c) => ({
      ...c,
      additional_columns_file1: columnList.length > 0 ? columnList : {},
      additional_columns_file1_types: undefined,
    }));
  };

  const setFile2AdditionalColumnsWithConfig = (rows: Array<{ column?: string }>) => {
    setFile2AdditionalColumns(rows);
    const columnList = rows.filter((r) => r.column).map((r) => r.column!);
    setConfig((c) => ({
      ...c,
      additional_columns_file2: columnList.length > 0 ? columnList : {},
      additional_columns_file2_types: undefined,
    }));
  };

  const onUploadDataset1 = async (file: File) => {
    try {
      setError(null);
      const parsed = await parseDataset(file);
      const inferred = inferFileFormat(parsed);
      if ((config.number_of_files || 1) === 1 && inferred !== ".xlsx") {
        setError("Single-file mode supports only Excel (.xlsx) with two sheets.");
        return;
      }
      setFile1(parsed);
      setFile1Type((config.number_of_files || 1) === 1 ? ".xlsx" : inferred);
      setConfig((c) => {
        const numFiles = c.number_of_files || 1;
        const nextFormat = deriveFileFormat((numFiles === 1 ? ".xlsx" : inferred), file2Type, numFiles);
        const updatedConfig = {
          ...c,
          file_format: nextFormat,
          number_of_files: numFiles,
          file1_path: file.name,
        };
        if (useSourceFileForOutput && (nextFormat === ".xlsx" || numFiles === 1)) {
          updatedConfig.output_path = file.name;
        }
        return updatedConfig;
      });
      log.info("Dataset 1 uploaded", { name: file.name, kind: parsed.kind });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to parse dataset");
      log.error("Dataset 1 parse failed", e);
    }
  };

  const onUploadDataset2 = async (file: File) => {
    try {
      setError(null);
      const parsed = await parseDataset(file);
      setFile2(parsed);
      const inferred = inferFileFormat(parsed);
      setFile2Type(inferred);
      setConfig((c) => ({
        ...c,
        number_of_files: 2,
        file_format: deriveFileFormat(file1Type, inferred, 2),
        file2_path: file.name,
      }));
      log.info("Dataset 2 uploaded", { name: file.name, kind: parsed.kind });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to parse dataset");
      log.error("Dataset 2 parse failed", e);
    }
  };

  const footer = (
    <div className="footer-container">
      <div className="footer-left">
        {activeStepId === "review" ? (
          <>
            <button type="button" onClick={() => downloadPublicFile("/config_template.json", "config_template.json")} className="linkButton">
              Template
            </button>
            <button type="button" onClick={() => downloadJson("config.json", normalizeConfigForCli(config))} className="primaryButton">
              Download Config
            </button>
          </>
        ) : null}
      </div>
      <div className="footer-right">
        {activeStepId !== "sources" ? (
          <button type="button" onClick={() => setActiveStepId(prevStep(activeStepId))} className="secondaryButton">
            Back
          </button>
        ) : null}
        {activeStepId !== "review" ? (
          <button type="button" onClick={() => setActiveStepId(nextStep(activeStepId))} className="primaryButton">
            Next
          </button>
        ) : null}
      </div>
    </div>
  );

  return (
    <ErrorBoundary>
      <AppShell title="Config Builder" footer={footer}>
        <Stepper steps={steps} activeStepId={activeStepId} />

        {error ? (
          <div className="error-container">
            <InlineAlert variant="error" title="Error">
              {error}
            </InlineAlert>
          </div>
        ) : null}

        {activeStepId === "sources" ? (
          <SourcesStep
            config={config}
            file1Type={file1Type}
            file2Type={file2Type}
            file1={file1}
            file2={file2}
            file1SheetOptions={file1SheetOptions}
            file2SheetOptions={file2SheetOptions}
            useSourceFileForOutput={useSourceFileForOutput}
            onConfigChange={setConfig}
            onFile1TypeChange={setFile1Type}
            onFile2TypeChange={setFile2Type}
            onUploadDataset1={onUploadDataset1}
            onUploadDataset2={onUploadDataset2}
            onUseSourceFileForOutputChange={setUseSourceFileForOutput}
          />
        ) : null}

        {activeStepId === "mapping" ? (
          <MappingStep
            config={config}
            file1Columns={file1Columns}
            file2Columns={file2Columns}
            columnMappingRows={columnMappingRows}
            joinKeyRows={joinKeyRows}
            file1Metrics={file1Metrics}
            file2Metrics={file2Metrics}
            file1AdditionalColumns={file1AdditionalColumns}
            file2AdditionalColumns={file2AdditionalColumns}
            mappedFile1Columns={mappedFile1Columns}
            mappedFile2Columns={mappedFile2Columns}
            availableFile1Columns={availableFile1Columns}
            availableFile2Columns={availableFile2Columns}
            onColumnMappingChange={setColumnMappingRows}
            onJoinKeysChange={setJoinKeyRows}
            onFile1MetricsChange={setFile1MetricsWithSync}
            onFile2MetricsChange={setFile2MetricsWithSync}
            onFile1AdditionalColumnsChange={setFile1AdditionalColumnsWithConfig}
            onFile2AdditionalColumnsChange={setFile2AdditionalColumnsWithConfig}
            onAggregationChange={(agg) => setConfig((c) => ({ ...c, aggregation: agg }))}
            onConfigChange={setConfig}
          />
        ) : null}

        {activeStepId === "review" ? (
          <ReviewStep config={config} normalizeConfig={normalizeConfigForCli} />
        ) : null}
      </AppShell>
    </ErrorBoundary>
  );
}

function inferFileFormat(ds: ParsedDataset): string {
  return ds.kind === "csv" ? ".csv" : ds.kind === "xlsx" ? ".xlsx" : ".json";
}

function deriveFileFormat(type1: string, type2: string, numberOfFiles: number): string {
  if (numberOfFiles === 1) return type1 || ".xlsx";
  if (!type1 || !type2) return "mixed";
  return type1 === type2 ? type1 : "mixed";
}

function getColumnsForConfigSide(ds: ParsedDataset | null, config: ValidationConfig, side: "file1" | "file2"): string[] {
  if (!ds) return [];
  if (ds.kind === "xlsx") {
    const sheetName = side === "file1" ? config.file1_sheet1 : config.number_of_files === 1 ? config.file1_sheet2 : config.file2_sheet;
    const cols = sheetName && ds.columnsBySheet ? ds.columnsBySheet[sheetName] : undefined;
    if (cols && cols.length) return cols;
    const first = ds.sheetNames?.[0];
    return first && ds.columnsBySheet ? ds.columnsBySheet[first] ?? [] : [];
  }
  return ds.columns ?? [];
}

function nextStep(step: StepId): StepId {
  return step === "sources" ? "mapping" : step === "mapping" ? "review" : "review";
}

function prevStep(step: StepId): StepId {
  return step === "review" ? "mapping" : step === "mapping" ? "sources" : "sources";
}

export default App;
