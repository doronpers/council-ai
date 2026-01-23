/**
 * Centralized logging abstraction for Council AI Web Application
 *
 * Provides environment-aware logging with structured output and future integration
 * points for error tracking services (Sentry, LogRocket, etc.)
 */

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

export interface LogContext {
  component?: string;
  action?: string;
  userId?: string;
  sessionId?: string;
  [key: string]: unknown;
}

class Logger {
  private isDevelopment: boolean;
  private enabledLevels: Set<LogLevel>;

  constructor() {
    // Check if we're in development mode (Vite sets import.meta.env.DEV)
    this.isDevelopment = import.meta.env.DEV;
    this.enabledLevels = new Set([LogLevel.WARN, LogLevel.ERROR]);

    if (this.isDevelopment) {
      this.enabledLevels.add(LogLevel.INFO);
      this.enabledLevels.add(LogLevel.DEBUG);
    }
  }

  private shouldLog(level: LogLevel): boolean {
    return this.enabledLevels.has(level);
  }

  private formatMessage(level: LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` | ${JSON.stringify(context)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}`;
  }

  /**
   * Log debug information (development only)
   */
  debug(message: string, context?: LogContext): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(this.formatMessage(LogLevel.DEBUG, message, context));
    }
  }

  /**
   * Log informational messages (development only)
   */
  info(message: string, context?: LogContext): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.formatMessage(LogLevel.INFO, message, context));
    }
  }

  /**
   * Log warning messages (always shown)
   */
  warn(message: string, error?: Error, context?: LogContext): void {
    if (this.shouldLog(LogLevel.WARN)) {
      const fullContext = { ...context, error: error?.message };
      console.warn(this.formatMessage(LogLevel.WARN, message, fullContext));
      if (error && this.isDevelopment) {
        console.warn(error.stack);
      }
    }
  }

  /**
   * Log error messages (always shown)
   */
  error(message: string, error?: Error, context?: LogContext): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      const fullContext = { ...context, error: error?.message, stack: error?.stack };
      console.error(this.formatMessage(LogLevel.ERROR, message, fullContext));

      // Future integration point for error tracking services
      // Example: Sentry.captureException(error, { extra: fullContext });
    }
  }

  /**
   * Convenience method for localStorage operation errors
   */
  storageError(operation: string, error: unknown, context?: LogContext): void {
    this.warn(`localStorage ${operation} failed`, error instanceof Error ? error : undefined, {
      ...context,
      operation,
    });
  }
}

// Export singleton instance
export const logger = new Logger();

/**
 * Type-safe log context builder
 *
 * @example
 * ```typescript
 * import { logger, createLogContext } from '../utils/logger';
 *
 * const context = createLogContext('AppContext');
 * logger.error('Failed to load config', err, context);
 * ```
 */
export function createLogContext(component: string): LogContext {
  return { component };
}
