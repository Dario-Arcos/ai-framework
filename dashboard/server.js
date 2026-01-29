import { createServer as createHttpServer } from 'node:http';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readStatusFile, readMetricsFile, readRecentLogs } from './lib/readers.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Default paths relative to project root (parent of dashboard/)
const DEFAULT_STATUS_PATH = join(__dirname, '..', 'status.json');
const DEFAULT_METRICS_PATH = join(__dirname, '..', 'logs', 'metrics.json');
const DEFAULT_LOGS_PATH = join(__dirname, '..', 'logs', 'iteration.log');

const RECENT_LOGS_COUNT = 20;

/**
 * Creates an HTTP server for the dashboard
 * @param {object} options - Server configuration
 * @param {string} options.statusPath - Path to status.json
 * @param {string} options.metricsPath - Path to metrics.json
 * @param {string} options.logsPath - Path to iteration.log
 * @param {number} options.port - Server port
 * @returns {http.Server} HTTP server instance
 */
export function createServer(options = {}) {
  const {
    statusPath = DEFAULT_STATUS_PATH,
    metricsPath = DEFAULT_METRICS_PATH,
    logsPath = DEFAULT_LOGS_PATH
  } = options;

  const server = createHttpServer(async (req, res) => {
    // CORS headers for all responses
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    const url = new URL(req.url, `http://${req.headers.host}`);

    if (url.pathname === '/api/status' && req.method === 'GET') {
      await handleApiStatus(req, res, { statusPath, metricsPath, logsPath });
    } else if (url.pathname === '/' && req.method === 'GET') {
      handleRoot(req, res);
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Not found' }));
    }
  });

  return server;
}

/**
 * Handle GET /api/status
 */
async function handleApiStatus(req, res, paths) {
  res.setHeader('Content-Type', 'application/json');

  const [status, metrics, recentLogs] = await Promise.all([
    readStatusFile(paths.statusPath),
    readMetricsFile(paths.metricsPath),
    readRecentLogs(paths.logsPath, RECENT_LOGS_COUNT)
  ]);

  // No loop running if status file is missing
  if (status === null) {
    res.writeHead(200);
    res.end(JSON.stringify({
      active: false,
      error: 'No loop running'
    }));
    return;
  }

  res.writeHead(200);
  res.end(JSON.stringify({
    status,
    metrics,
    recentLogs,
    active: true,
    lastUpdate: new Date().toISOString()
  }));
}

/**
 * Handle GET / - Serve HTML dashboard (placeholder for now)
 */
function handleRoot(req, res) {
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end(`<!DOCTYPE html>
<html>
<head>
  <title>Ralph Dashboard</title>
</head>
<body>
  <h1>Ralph Dashboard</h1>
  <p>Dashboard UI coming in Task 03</p>
</body>
</html>`);
}

// Run server if this is the main module
const isMainModule = import.meta.url === `file://${process.argv[1]}`;

if (isMainModule) {
  const PORT = process.env.PORT || 3456;
  const server = createServer();
  server.listen(PORT, () => {
    console.log(`Dashboard running on http://localhost:${PORT}`);
  });
}
