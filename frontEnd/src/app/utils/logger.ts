export type LogLevel = "debug" | "info" | "warn" | "error";

export interface ILogger {
  debug(message: string, meta?: unknown): void;
  info(message: string, meta?: unknown): void;
  warn(message: string, meta?: unknown): void;
  error(message: string, meta?: unknown): void;
}

export class ConsoleLogger implements ILogger {
  private readonly scope: string;
  constructor(scope: string) {
    this.scope = scope;
  }

  debug(message: string, meta?: unknown) {
    this.log("debug", message, meta);
  }
  info(message: string, meta?: unknown) {
    this.log("info", message, meta);
  }
  warn(message: string, meta?: unknown) {
    this.log("warn", message, meta);
  }
  error(message: string, meta?: unknown) {
    this.log("error", message, meta);
  }

  private log(level: LogLevel, message: string, meta?: unknown) {
    const prefix = `[dvt-ui][${this.scope}]`;
    const payload = meta === undefined ? [prefix, message] : [prefix, message, meta];
    let fn: typeof console.log;
    if (level === "debug") fn = console.debug;
    else if (level === "info") fn = console.info;
    else if (level === "warn") fn = console.warn;
    else fn = console.error;
    fn(...payload);
  }
}

