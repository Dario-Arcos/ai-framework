import { readFile } from 'node:fs/promises';

/**
 * Reads and parses status.json file
 * @param {string} filePath - Path to status.json
 * @returns {Promise<object|null>} Parsed status object or null if file missing/invalid
 */
export async function readStatusFile(filePath) {
  try {
    const content = await readFile(filePath, 'utf-8');
    return JSON.parse(content);
  } catch {
    return null;
  }
}

/**
 * Reads and parses metrics.json file
 * @param {string} filePath - Path to metrics.json
 * @returns {Promise<object|null>} Parsed metrics object or null if file missing/invalid
 */
export async function readMetricsFile(filePath) {
  try {
    const content = await readFile(filePath, 'utf-8');
    return JSON.parse(content);
  } catch {
    return null;
  }
}

/**
 * Reads last N lines from log file
 * @param {string} filePath - Path to log file
 * @param {number} n - Number of lines to return
 * @returns {Promise<string[]>} Array of last N non-empty lines
 */
export async function readRecentLogs(filePath, n) {
  try {
    const content = await readFile(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim() !== '');
    return lines.slice(-n);
  } catch {
    return [];
  }
}
