/**
 * Logger Module - Clean Code Example
 * This should pass all checks (has tests, no issues)
 */

const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
};

class Logger {
  constructor(options = {}) {
    this.level = options.level || LOG_LEVELS.INFO;
    this.prefix = options.prefix || '';
  }

  error(message, meta = {}) {
    if (this.level >= LOG_LEVELS.ERROR) {
      this.write('ERROR', message, meta);
    }
  }

  warn(message, meta = {}) {
    if (this.level >= LOG_LEVELS.WARN) {
      this.write('WARN', message, meta);
    }
  }

  info(message, meta = {}) {
    if (this.level >= LOG_LEVELS.INFO) {
      this.write('INFO', message, meta);
    }
  }

  debug(message, meta = {}) {
    if (this.level >= LOG_LEVELS.DEBUG) {
      this.write('DEBUG', message, meta);
    }
  }

  write(level, message, meta) {
    const timestamp = new Date().toISOString();
    const prefix = this.prefix ? `[${this.prefix}] ` : '';
    const metaStr = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';
    console.log(`${timestamp} ${prefix}[${level}] ${message}${metaStr}`);
  }
}

module.exports = { Logger, LOG_LEVELS };
