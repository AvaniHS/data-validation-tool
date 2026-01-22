import { AdditionalColumnsTable, AggregationConfig, Card, MappingTable, MetricSelector, Select, StepContainer } from "ui";
import type { ValidationConfig } from "../app/config/types";
import "../styles/mapping-step.css";

interface MappingStepProps {
  config: ValidationConfig;
  file1Columns: string[];
  file2Columns: string[];
  columnMappingRows: Array<{ left?: string; right?: string }>;
  joinKeyRows: Array<{ left?: string; right?: string }>;
  file1Metrics: string[];
  file2Metrics: string[];
  file1AdditionalColumns: Array<{ column?: string }>;
  file2AdditionalColumns: Array<{ column?: string }>;
  mappedFile1Columns: string[];
  mappedFile2Columns: string[];
  availableFile1Columns: string[];
  availableFile2Columns: string[];
  onColumnMappingChange: (rows: Array<{ left?: string; right?: string }>) => void;
  onJoinKeysChange: (rows: Array<{ left?: string; right?: string }>) => void;
  onFile1MetricsChange: (metrics: string[]) => void;
  onFile2MetricsChange: (metrics: string[]) => void;
  onFile1AdditionalColumnsChange: (rows: Array<{ column?: string }>) => void;
  onFile2AdditionalColumnsChange: (rows: Array<{ column?: string }>) => void;
  onAggregationChange: (agg: any) => void;
  onConfigChange: (updater: (c: ValidationConfig) => ValidationConfig) => void;
}

export function MappingStep({
  config,
  file1Columns,
  file2Columns,
  columnMappingRows,
  joinKeyRows,
  file1Metrics,
  file2Metrics,
  file1AdditionalColumns,
  file2AdditionalColumns,
  mappedFile1Columns,
  mappedFile2Columns,
  availableFile1Columns,
  availableFile2Columns,
  onColumnMappingChange,
  onJoinKeysChange,
  onFile1MetricsChange,
  onFile2MetricsChange,
  onFile1AdditionalColumnsChange,
  onFile2AdditionalColumnsChange,
  onAggregationChange,
  onConfigChange,
}: MappingStepProps) {
  return (
    <StepContainer>
      <Card title="Column Mapping" helperText="Map columns between files for comparison">
        <div className="mapping-section">
          <MappingTable
            title=""
            leftLabel="File 1"
            rightLabel="File 2"
            leftOptions={file1Columns}
            rightOptions={file2Columns}
            rows={columnMappingRows.length ? columnMappingRows : [{}]}
            onChange={onColumnMappingChange}
          />
        </div>
      </Card>

      <Card title="Join Keys" helperText="Select keys to join records between files">
        <div className="mapping-section">
          <MappingTable
            title=""
            leftLabel="File 1"
            rightLabel="File 2"
            leftOptions={file1Columns}
            rightOptions={file2Columns}
            rows={joinKeyRows.length ? joinKeyRows : [{}]}
            onChange={onJoinKeysChange}
          />
        </div>
      </Card>

      <Card
        title="Metrics"
        helperText="Select columns to be treated as metrics for numerical comparison. When you select a column from File 1, its mapped column in File 2 will be automatically added."
      >
        <div className="responsive-grid-2 metrics-section">
          <MetricSelector
            label="File 1 Metrics"
            options={mappedFile1Columns}
            selected={file1Metrics}
            onChange={onFile1MetricsChange}
          />
          <MetricSelector
            label="File 2 Metrics"
            options={mappedFile2Columns}
            selected={file2Metrics}
            onChange={onFile2MetricsChange}
          />
        </div>
      </Card>

      <Card
        title="Additional Columns"
        helperText="Select additional columns to include in the comparison. These columns are not mapped between files."
      >
        <div className="responsive-grid-2 additional-columns-section">
          <AdditionalColumnsTable
            label="File 1 Additional Columns"
            options={availableFile1Columns}
            rows={file1AdditionalColumns.length > 0 ? file1AdditionalColumns : [{}]}
            onChange={onFile1AdditionalColumnsChange}
          />
          <AdditionalColumnsTable
            label="File 2 Additional Columns"
            options={availableFile2Columns}
            rows={file2AdditionalColumns.length > 0 ? file2AdditionalColumns : [{}]}
            onChange={onFile2AdditionalColumnsChange}
          />
        </div>
      </Card>

      <Card>
        <AggregationConfig
          file1Columns={file1Columns}
          file2Columns={file2Columns}
          config={config.aggregation}
          onChange={onAggregationChange}
        />
      </Card>

      <Card
        title="Analysis Options"
        helperText="Configure additional analysis options for the validation process."
      >
        <div className="responsive-grid-2 analysis-options">
          <Select
            label="Detailed Join Analysis"
            value={config.detailed_join_analysis || "no"}
            options={[
              { label: "No", value: "no" },
              { label: "Yes", value: "yes" },
            ]}
            onChange={(v: string) => onConfigChange((c) => ({ ...c, detailed_join_analysis: v }))}
          />
          <Select
            label="Detailed Metric Delta Analysis"
            value={config.detailed_metric_delta_analysis || "no"}
            options={[
              { label: "No", value: "no" },
              { label: "Yes", value: "yes" },
            ]}
            onChange={(v: string) => onConfigChange((c) => ({ ...c, detailed_metric_delta_analysis: v }))}
          />
        </div>
      </Card>
    </StepContainer>
  );
}
