import { createServer as createHttpServer } from 'node:http';
import { join, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFile, access } from 'node:fs/promises';
import { constants } from 'node:fs';
import { readStatusFile, readMetricsFile, readRecentLogs } from './lib/readers.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

// MIME type mapping for static files
const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

/**
 * Get MIME type for a file extension
 * @param {string} filePath - Path to file
 * @returns {string} MIME type
 */
function getMimeType(filePath) {
  const ext = extname(filePath).toLowerCase();
  return MIME_TYPES[ext] || 'application/octet-stream';
}

// Default paths relative to project root (parent of dashboard/)
const DEFAULT_STATUS_PATH = join(__dirname, '..', 'status.json');
const DEFAULT_METRICS_PATH = join(__dirname, '..', 'logs', 'metrics.json');
const DEFAULT_LOGS_PATH = join(__dirname, '..', 'logs', 'iteration.log');
const DEFAULT_PUBLIC_PATH = join(__dirname, 'public');

const RECENT_LOGS_COUNT = 20;

/**
 * Creates an HTTP server for the dashboard
 * @param {object} options - Server configuration
 * @param {string} options.statusPath - Path to status.json
 * @param {string} options.metricsPath - Path to metrics.json
 * @param {string} options.logsPath - Path to iteration.log
 * @param {string} options.publicPath - Path to public directory for static files
 * @param {number} options.port - Server port
 * @returns {http.Server} HTTP server instance
 */
export function createServer(options = {}) {
  const {
    statusPath = DEFAULT_STATUS_PATH,
    metricsPath = DEFAULT_METRICS_PATH,
    logsPath = DEFAULT_LOGS_PATH,
    publicPath = DEFAULT_PUBLIC_PATH
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
      await handleRoot(req, res, publicPath);
    } else if (req.method === 'GET') {
      await handleStaticFile(req, res, url.pathname, publicPath);
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
 * Handle GET / - Serve public/index.html or placeholder
 * @param {http.IncomingMessage} req - Request
 * @param {http.ServerResponse} res - Response
 * @param {string} publicPath - Path to public directory
 */
async function handleRoot(req, res, publicPath) {
  const indexPath = join(publicPath, 'index.html');

  try {
    await access(indexPath, constants.R_OK);
    const content = await readFile(indexPath, 'utf-8');
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(content);
  } catch {
    // Fallback to placeholder when index.html doesn't exist
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
}

/**
 * Handle static file requests from public directory
 * @param {http.IncomingMessage} req - Request
 * @param {http.ServerResponse} res - Response
 * @param {string} pathname - URL pathname
 * @param {string} publicPath - Path to public directory
 */
async function handleStaticFile(req, res, pathname, publicPath) {
  // Prevent directory traversal attacks
  const safePath = pathname.replace(/\.\./g, '');
  const filePath = join(publicPath, safePath);

  try {
    await access(filePath, constants.R_OK);
    const content = await readFile(filePath);
    const mimeType = getMimeType(filePath);
    res.writeHead(200, { 'Content-Type': mimeType });
    res.end(content);
  } catch {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
  }
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
