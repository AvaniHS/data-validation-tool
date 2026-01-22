import { z } from "zod";

export const FileFormatSchema = z.enum([".csv", ".xlsx", ".json", "mixed"]);

export type FileFormat = z.infer<typeof FileFormatSchema>;

export const YesNoSchema = z.enum(["yes", "no"]);

export const JoinKeyTypeSchema = z.enum(["numeric", "non_numeric", "NA", "mixed", "unknown"]);

export const ConfigSchema = z.object({
  file_format: z.string(),
  number_of_files: z.number().int(),
  file1_path: z.string(),
  file2_path: z.string(),
  file1_sheet1: z.string(),
  file1_sheet2: z.string(),
  file2_sheet: z.string(),
  output_path: z.string(),
  output_sheet: z.string(),
  column_mapping: z.record(z.string(), z.string()),
  additional_columns_file1: z.union([z.array(z.string()), z.record(z.string(), z.string())]),
  additional_columns_file1_types: z.union([z.array(z.string()), z.undefined()]).optional(),
  additional_columns_file2: z.union([z.array(z.string()), z.record(z.string(), z.string())]),
  additional_columns_file2_types: z.union([z.array(z.string()), z.undefined()]).optional(),
  join_keys: z.record(z.string(), z.string()),
  join_keys_types: z.union([z.record(z.string(), JoinKeyTypeSchema), z.array(z.any())]).optional(),
  aggregation: z.any().optional(),
  file1_metric_list: z.array(z.string()).optional(),
  file2_metric_list: z.array(z.string()).optional(),
  detailed_join_analysis: z.string().optional(),
  detailed_metric_delta_analysis: z.string().optional(),
});

export type ValidationConfig = z.infer<typeof ConfigSchema>;

export function createEmptyConfig(): ValidationConfig {
  return {
    file_format: ".xlsx",
    number_of_files: 1,
    file1_path: "",
    file2_path: "NA",
    file1_sheet1: "",
    file1_sheet2: "",
    file2_sheet: "NA",
    output_path: "",
    output_sheet: "",
    column_mapping: {},
    additional_columns_file1: {},
    additional_columns_file2: {},
    join_keys: {},
    join_keys_types: {},
    aggregation: "NA",
    file1_metric_list: [],
    file2_metric_list: [],
    detailed_join_analysis: "no",
    detailed_metric_delta_analysis: "no",
  };
}

