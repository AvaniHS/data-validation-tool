import { useCallback, useMemo, useState } from "react";
import type { ValidationConfig } from "../app/config/types";
import { createEmptyConfig } from "../app/config/types";

export function useConfigState() {
  const [config, setConfig] = useState<ValidationConfig>(() => createEmptyConfig());

  const updateConfig = useCallback((updater: (c: ValidationConfig) => ValidationConfig) => {
    setConfig(updater);
  }, []);

  const normalizeConfigForCli = useCallback((config: ValidationConfig): ValidationConfig => {
    const file2Path = config.number_of_files === 1 ? "NA" : config.file2_path || "";
    const file2Sheet = config.number_of_files === 1 ? "NA" : config.file2_sheet || "NA";

    const file1AdditionalCols = config.additional_columns_file1;
    const file1AdditionalColsArray = Array.isArray(file1AdditionalCols)
      ? file1AdditionalCols
      : typeof file1AdditionalCols === "object" && file1AdditionalCols
        ? Object.keys(file1AdditionalCols)
        : [];

    const file2AdditionalCols = config.additional_columns_file2;
    const file2AdditionalColsArray = Array.isArray(file2AdditionalCols)
      ? file2AdditionalCols
      : typeof file2AdditionalCols === "object" && file2AdditionalCols
        ? Object.keys(file2AdditionalCols)
        : [];

    return {
      ...config,
      file2_path: file2Path,
      file2_sheet: file2Sheet,
      additional_columns_file1: file1AdditionalColsArray.length > 0 ? file1AdditionalColsArray : [],
      additional_columns_file1_types: undefined,
      additional_columns_file2: file2AdditionalColsArray.length > 0 ? file2AdditionalColsArray : [],
      additional_columns_file2_types: undefined,
      aggregation: config.aggregation ?? "NA",
      detailed_join_analysis: (config.detailed_join_analysis ?? "no").toLowerCase(),
      detailed_metric_delta_analysis: (config.detailed_metric_delta_analysis ?? "no").toLowerCase(),
    };
  }, []);

  return {
    config,
    setConfig: updateConfig,
    normalizeConfigForCli,
  };
}
