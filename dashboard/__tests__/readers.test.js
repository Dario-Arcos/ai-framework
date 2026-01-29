import { describe, it, before, after } from 'node:test';
import assert from 'node:assert';
import { mkdir, writeFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { readStatusFile, readMetricsFile, readRecentLogs } from '../lib/readers.js';

const TEST_DIR = join(import.meta.dirname, '..', '.test-fixtures');
const STATUS_PATH = join(TEST_DIR, 'status.json');
const LOGS_DIR = join(TEST_DIR, 'logs');
const METRICS_PATH = join(LOGS_DIR, 'metrics.json');
const ITERATION_LOG = join(LOGS_DIR, 'iteration.log');

describe('readStatusFile', () => {
  before(async () => {
    await mkdir(TEST_DIR, { recursive: true });
  });

  after(async () => {
    await rm(TEST_DIR, { recursive: true, force: true });
  });

  it('returns null when file does not exist', async () => {
    const result = await readStatusFile(join(TEST_DIR, 'nonexistent.json'));
    assert.strictEqual(result, null);
  });

  it('returns parsed object when file exists', async () => {
    const statusData = {
      current_iteration: 5,
      consecutive_failures: 0,
      status: 'running',
      mode: 'build',
      branch: 'feat/dashboard',
      timestamp: '2026-01-29T10:30:00Z'
    };
    await writeFile(STATUS_PATH, JSON.stringify(statusData));

    const result = await readStatusFile(STATUS_PATH);

    assert.deepStrictEqual(result, statusData);
  });

  it('returns null for malformed JSON', async () => {
    await writeFile(STATUS_PATH, '{ invalid json }');

    const result = await readStatusFile(STATUS_PATH);

    assert.strictEqual(result, null);
  });
});

describe('readMetricsFile', () => {
  before(async () => {
    await mkdir(LOGS_DIR, { recursive: true });
  });

  after(async () => {
    await rm(TEST_DIR, { recursive: true, force: true });
  });

  it('returns null when file does not exist', async () => {
    const result = await readMetricsFile(join(LOGS_DIR, 'nonexistent.json'));
    assert.strictEqual(result, null);
  });

  it('returns parsed object when file exists', async () => {
    const metricsData = {
      total_iterations: 10,
      successful: 8,
      failed: 2,
      avg_duration_seconds: 45
    };
    await writeFile(METRICS_PATH, JSON.stringify(metricsData));

    const result = await readMetricsFile(METRICS_PATH);

    assert.deepStrictEqual(result, metricsData);
  });

  it('returns null for malformed JSON', async () => {
    await writeFile(METRICS_PATH, 'not json');

    const result = await readMetricsFile(METRICS_PATH);

    assert.strictEqual(result, null);
  });
});

describe('readRecentLogs', () => {
  before(async () => {
    await mkdir(LOGS_DIR, { recursive: true });
  });

  after(async () => {
    await rm(TEST_DIR, { recursive: true, force: true });
  });

  it('returns empty array when file does not exist', async () => {
    const result = await readRecentLogs(join(LOGS_DIR, 'nonexistent.log'), 5);
    assert.deepStrictEqual(result, []);
  });

  it('returns last N lines from log file', async () => {
    const logLines = Array.from({ length: 20 }, (_, i) =>
      `[2026-01-29T10:${String(i).padStart(2, '0')}:00Z] START - Iteration ${i + 1}`
    );
    await writeFile(ITERATION_LOG, logLines.join('\n'));

    const result = await readRecentLogs(ITERATION_LOG, 5);

    assert.strictEqual(result.length, 5);
    assert.ok(result[0].includes('Iteration 16'));
    assert.ok(result[4].includes('Iteration 20'));
  });

  it('returns all lines if file has fewer than N', async () => {
    const logLines = [
      '[2026-01-29T10:00:00Z] START - Iteration 1',
      '[2026-01-29T10:01:00Z] SUCCESS - Done'
    ];
    await writeFile(ITERATION_LOG, logLines.join('\n'));

    const result = await readRecentLogs(ITERATION_LOG, 10);

    assert.strictEqual(result.length, 2);
  });

  it('filters empty lines', async () => {
    const content = 'Line 1\n\nLine 2\n\n';
    await writeFile(ITERATION_LOG, content);

    const result = await readRecentLogs(ITERATION_LOG, 10);

    assert.strictEqual(result.length, 2);
    assert.deepStrictEqual(result, ['Line 1', 'Line 2']);
  });
});
