import { describe, it, before, after, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import { mkdir, writeFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { createServer } from '../server.js';

// Use separate test directory to avoid conflicts with readers.test.js
const TEST_DIR = join(import.meta.dirname, '..', '.server-test-fixtures');
const STATUS_PATH = join(TEST_DIR, 'status.json');
const LOGS_DIR = join(TEST_DIR, 'logs');
const METRICS_PATH = join(LOGS_DIR, 'metrics.json');
const ITERATION_LOG = join(LOGS_DIR, 'iteration.log');

describe('Server API', () => {
  let server;
  let baseUrl;

  beforeEach(async () => {
    // Create test directories fresh for each test
    await mkdir(LOGS_DIR, { recursive: true });

    server = createServer({
      statusPath: STATUS_PATH,
      metricsPath: METRICS_PATH,
      logsPath: ITERATION_LOG,
      port: 0 // Random available port for testing
    });
    await new Promise(resolve => server.listen(0, resolve));
    const address = server.address();
    baseUrl = `http://localhost:${address.port}`;
  });

  afterEach(async () => {
    await new Promise(resolve => server.close(resolve));
    // Clean up test files
    await rm(STATUS_PATH, { force: true });
    await rm(METRICS_PATH, { force: true });
    await rm(ITERATION_LOG, { force: true });
  });

  after(async () => {
    await rm(TEST_DIR, { recursive: true, force: true });
  });

  describe('GET /api/status', () => {
    it('returns JSON with status, metrics, recentLogs when files exist', async () => {
      const statusData = {
        current_iteration: 5,
        consecutive_failures: 0,
        status: 'running',
        mode: 'build',
        branch: 'feat/dashboard',
        timestamp: '2026-01-29T10:30:00Z'
      };
      const metricsData = {
        total_iterations: 10,
        successful: 8,
        failed: 2,
        avg_duration_seconds: 45
      };
      const logLines = [
        '[2026-01-29T10:30:00Z] SUCCESS - Task completed',
        '[2026-01-29T10:29:00Z] START - Iteration 5'
      ];

      await writeFile(STATUS_PATH, JSON.stringify(statusData));
      await writeFile(METRICS_PATH, JSON.stringify(metricsData));
      await writeFile(ITERATION_LOG, logLines.join('\n'));

      const response = await fetch(`${baseUrl}/api/status`);
      const data = await response.json();

      assert.strictEqual(response.status, 200);
      assert.strictEqual(response.headers.get('content-type'), 'application/json');
      assert.strictEqual(data.active, true);
      assert.deepStrictEqual(data.status, statusData);
      assert.deepStrictEqual(data.metrics, metricsData);
      assert.strictEqual(data.recentLogs.length, 2);
      assert.ok(data.lastUpdate); // ISO timestamp present
    });

    it('returns active:false with error when no files exist', async () => {
      const response = await fetch(`${baseUrl}/api/status`);
      const data = await response.json();

      assert.strictEqual(response.status, 200);
      assert.strictEqual(data.active, false);
      assert.strictEqual(data.error, 'No loop running');
    });

    it('returns active:false when status.json is malformed', async () => {
      await writeFile(STATUS_PATH, '{ invalid json }');

      const response = await fetch(`${baseUrl}/api/status`);
      const data = await response.json();

      assert.strictEqual(data.active, false);
      assert.ok(data.error);
    });
  });

  describe('GET /', () => {
    it('returns 200', async () => {
      const response = await fetch(`${baseUrl}/`);

      assert.strictEqual(response.status, 200);
    });
  });

  describe('CORS headers', () => {
    it('includes Access-Control-Allow-Origin on /api/status', async () => {
      const response = await fetch(`${baseUrl}/api/status`);

      assert.ok(response.headers.get('access-control-allow-origin'));
    });

    it('includes Access-Control-Allow-Origin on /', async () => {
      const response = await fetch(`${baseUrl}/`);

      assert.ok(response.headers.get('access-control-allow-origin'));
    });
  });

  describe('404 handling', () => {
    it('returns 404 for unknown routes', async () => {
      const response = await fetch(`${baseUrl}/unknown`);

      assert.strictEqual(response.status, 404);
    });
  });

  describe('Static file serving', () => {
    const PUBLIC_DIR = join(TEST_DIR, 'public');

    beforeEach(async () => {
      await mkdir(PUBLIC_DIR, { recursive: true });
    });

    afterEach(async () => {
      await rm(PUBLIC_DIR, { recursive: true, force: true });
    });

    it('serves public/index.html for GET / when file exists', async () => {
      const htmlContent = '<!DOCTYPE html><html><body>Test Dashboard</body></html>';
      await writeFile(join(PUBLIC_DIR, 'index.html'), htmlContent);

      // Create a new server with the test public directory
      await new Promise(resolve => server.close(resolve));
      server = createServer({
        statusPath: STATUS_PATH,
        metricsPath: METRICS_PATH,
        logsPath: ITERATION_LOG,
        publicPath: PUBLIC_DIR
      });
      await new Promise(resolve => server.listen(0, resolve));
      const address = server.address();
      baseUrl = `http://localhost:${address.port}`;

      const response = await fetch(`${baseUrl}/`);
      const body = await response.text();

      assert.strictEqual(response.status, 200);
      assert.strictEqual(response.headers.get('content-type'), 'text/html');
      assert.strictEqual(body, htmlContent);
    });

    it('serves CSS files with correct MIME type', async () => {
      const cssContent = 'body { color: red; }';
      await writeFile(join(PUBLIC_DIR, 'styles.css'), cssContent);

      await new Promise(resolve => server.close(resolve));
      server = createServer({
        statusPath: STATUS_PATH,
        metricsPath: METRICS_PATH,
        logsPath: ITERATION_LOG,
        publicPath: PUBLIC_DIR
      });
      await new Promise(resolve => server.listen(0, resolve));
      const address = server.address();
      baseUrl = `http://localhost:${address.port}`;

      const response = await fetch(`${baseUrl}/styles.css`);
      const body = await response.text();

      assert.strictEqual(response.status, 200);
      assert.strictEqual(response.headers.get('content-type'), 'text/css');
      assert.strictEqual(body, cssContent);
    });

    it('serves JavaScript files with correct MIME type', async () => {
      const jsContent = 'console.log("test");';
      await writeFile(join(PUBLIC_DIR, 'app.js'), jsContent);

      await new Promise(resolve => server.close(resolve));
      server = createServer({
        statusPath: STATUS_PATH,
        metricsPath: METRICS_PATH,
        logsPath: ITERATION_LOG,
        publicPath: PUBLIC_DIR
      });
      await new Promise(resolve => server.listen(0, resolve));
      const address = server.address();
      baseUrl = `http://localhost:${address.port}`;

      const response = await fetch(`${baseUrl}/app.js`);
      const body = await response.text();

      assert.strictEqual(response.status, 200);
      assert.strictEqual(response.headers.get('content-type'), 'text/javascript');
      assert.strictEqual(body, jsContent);
    });

    it('returns 404 for non-existent static files', async () => {
      await new Promise(resolve => server.close(resolve));
      server = createServer({
        statusPath: STATUS_PATH,
        metricsPath: METRICS_PATH,
        logsPath: ITERATION_LOG,
        publicPath: PUBLIC_DIR
      });
      await new Promise(resolve => server.listen(0, resolve));
      const address = server.address();
      baseUrl = `http://localhost:${address.port}`;

      const response = await fetch(`${baseUrl}/nonexistent.css`);

      assert.strictEqual(response.status, 404);
    });

    it('returns placeholder HTML for GET / when public/index.html does not exist', async () => {
      // No index.html created, should fall back to placeholder
      await new Promise(resolve => server.close(resolve));
      server = createServer({
        statusPath: STATUS_PATH,
        metricsPath: METRICS_PATH,
        logsPath: ITERATION_LOG,
        publicPath: PUBLIC_DIR
      });
      await new Promise(resolve => server.listen(0, resolve));
      const address = server.address();
      baseUrl = `http://localhost:${address.port}`;

      const response = await fetch(`${baseUrl}/`);
      const body = await response.text();

      assert.strictEqual(response.status, 200);
      assert.strictEqual(response.headers.get('content-type'), 'text/html');
      assert.ok(body.includes('Ralph Dashboard'));
    });
  });
});
