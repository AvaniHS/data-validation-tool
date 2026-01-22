import Papa from "papaparse";
import * as XLSX from "xlsx";

export type ParsedDataset = {
  kind: "csv" | "xlsx" | "json";
  fileName: string;
  sheetNames?: string[];
  columnsBySheet?: Record<string, string[]>;
  columns?: string[];
};

export async function parseDataset(file: File): Promise<ParsedDataset> {
  const name = file.name.toLowerCase();
  if (name.endsWith(".csv")) return parseCsv(file);
  if (name.endsWith(".xlsx") || name.endsWith(".xls")) return parseXlsx(file);
  if (name.endsWith(".json")) return parseJson(file);
  throw new Error(`Unsupported file type: ${file.name}`);
}

async function readAsArrayBuffer(file: File): Promise<ArrayBuffer> {
  return await file.arrayBuffer();
}

async function readAsText(file: File): Promise<string> {
  return await file.text();
}

async function parseCsv(file: File): Promise<ParsedDataset> {
  const text = await readAsText(file);
  const parsed = Papa.parse<Record<string, unknown>>(text, { header: true, skipEmptyLines: true });
  const fields = parsed.meta.fields ?? [];
  return { kind: "csv", fileName: file.name, columns: unique(fields) };
}

async function parseXlsx(file: File): Promise<ParsedDataset> {
  const buf = await readAsArrayBuffer(file);
  const wb = XLSX.read(buf, { type: "array" });
  const sheetNames = wb.SheetNames ?? [];

  const columnsBySheet: Record<string, string[]> = {};
  for (const sheetName of sheetNames) {
    const ws = wb.Sheets[sheetName];
    if (!ws) continue;
    const json = XLSX.utils.sheet_to_json<Record<string, unknown>>(ws, { defval: null });
    const first = json[0];
    const keys = first ? Object.keys(first) : [];
    columnsBySheet[sheetName] = unique(keys);
  }

  return { kind: "xlsx", fileName: file.name, sheetNames, columnsBySheet };
}

async function parseJson(file: File): Promise<ParsedDataset> {
  const text = await readAsText(file);
  const data = JSON.parse(text);
  const columns = inferJsonColumns(data);
  return { kind: "json", fileName: file.name, columns };
}

function inferJsonColumns(data: unknown): string[] {
  if (Array.isArray(data)) {
    const firstObj = data.find((x) => x && typeof x === "object" && !Array.isArray(x)) as Record<string, unknown> | undefined;
    return firstObj ? unique(Object.keys(firstObj)) : [];
  }
  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>;
    if (Array.isArray(obj.data) && obj.data.length > 0 && typeof obj.data[0] === "object") {
      if (Array.isArray(obj.columns)) return unique(obj.columns.map(String));
      return unique(Object.keys(obj.data[0] as Record<string, unknown>));
    }
    return unique(Object.keys(obj));
  }
  return [];
}

function unique(values: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const v of values) {
    const trimmed = v?.trim();
    if (!trimmed) continue;
    if (seen.has(trimmed)) continue;
    seen.add(trimmed);
    out.push(trimmed);
  }
  return out;
}

