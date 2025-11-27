/**
 * Logger Tests - Clean test coverage
 */

const { Logger, LOG_LEVELS } = require('./logger');

describe('Logger', () => {
  let logger;
  let consoleSpy;

  beforeEach(() => {
    logger = new Logger({ level: LOG_LEVELS.DEBUG });
    consoleSpy = jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  test('should log error messages', () => {
    logger.error('test error', { code: 500 });
    expect(consoleSpy).toHaveBeenCalled();
    expect(consoleSpy.mock.calls[0][0]).toContain('[ERROR]');
    expect(consoleSpy.mock.calls[0][0]).toContain('test error');
  });

  test('should log warn messages', () => {
    logger.warn('test warning');
    expect(consoleSpy).toHaveBeenCalled();
    expect(consoleSpy.mock.calls[0][0]).toContain('[WARN]');
  });

  test('should respect log level', () => {
    const infoLogger = new Logger({ level: LOG_LEVELS.INFO });
    infoLogger.debug('should not log');
    expect(consoleSpy).not.toHaveBeenCalled();
  });

  test('should include prefix when provided', () => {
    const prefixLogger = new Logger({ prefix: 'APP' });
    prefixLogger.info('test');
    expect(consoleSpy.mock.calls[0][0]).toContain('[APP]');
  });

  test('should include metadata', () => {
    logger.info('test', { user: 'john', action: 'login' });
    expect(consoleSpy.mock.calls[0][0]).toContain('{"user":"john"');
  });
});
