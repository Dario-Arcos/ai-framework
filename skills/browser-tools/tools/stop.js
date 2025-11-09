#!/usr/bin/env node

/**
 * Safe Chrome Debugging Instance Shutdown
 *
 * Stops ONLY the Chrome instance running on port 9223 (debugging instance).
 * Does NOT touch your main Chrome sessions on port 9222.
 *
 * Platform Support: macOS only (uses lsof)
 */

import { execSync } from "node:child_process";

/**
 * Get PID of process listening on specific port
 * @param {number} port - Port number to check
 * @returns {string|null} - PID or null if no process found
 */
function getPidOnPort(port) {
  try {
    const output = execSync(`lsof -ti :${port}`, {
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "ignore"], // Suppress stderr
    });
    return output.trim();
  } catch {
    return null; // No process found on port
  }
}

/**
 * Kill process by PID with optional signal
 * @param {string} pid - Process ID
 * @param {string} signal - Signal to send (default: TERM)
 * @returns {boolean} - True if kill succeeded
 */
function killProcess(pid, signal = "TERM") {
  try {
    execSync(`kill -${signal} ${pid}`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if process is still running
 * @param {string} pid - Process ID
 * @returns {boolean} - True if process exists
 */
function isProcessAlive(pid) {
  try {
    execSync(`kill -0 ${pid}`, { stdio: "ignore" });
    return true; // Process exists
  } catch {
    return false; // Process does not exist
  }
}

/**
 * Wait for process to terminate
 * @param {string} pid - Process ID
 * @param {number} maxWaitMs - Maximum time to wait in milliseconds
 * @returns {Promise<boolean>} - True if process terminated
 */
async function waitForTermination(pid, maxWaitMs = 5000) {
  const startTime = Date.now();
  while (Date.now() - startTime < maxWaitMs) {
    if (!isProcessAlive(pid)) {
      return true;
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

// Main execution
const PORT = 9223;

console.log(`Checking for Chrome debugging instance on port ${PORT}...`);

const pid = getPidOnPort(PORT);

if (!pid) {
  console.log("✓ No Chrome instance running on port 9223");
  console.log("  (Nothing to stop)");
  process.exit(0);
}

console.log(`Found Chrome process (PID: ${pid})`);
console.log("Sending graceful shutdown signal (TERM)...");

// Try graceful shutdown first
if (!killProcess(pid, "TERM")) {
  console.error("✗ Failed to send TERM signal");
  process.exit(1);
}

// Wait for graceful termination
const terminated = await waitForTermination(pid, 5000);

if (terminated) {
  console.log("✓ Chrome debugging instance stopped gracefully");
  process.exit(0);
}

// Force kill if still running
console.log("Process did not terminate gracefully, forcing shutdown...");

if (killProcess(pid, "9")) {
  // Wait a bit for force kill to take effect
  await new Promise((r) => setTimeout(r, 1000));

  if (!isProcessAlive(pid)) {
    console.log("✓ Chrome debugging instance force-stopped");
    process.exit(0);
  } else {
    console.error("✗ Failed to stop Chrome process");
    process.exit(1);
  }
} else {
  console.error("✗ Failed to send KILL signal");
  process.exit(1);
}
