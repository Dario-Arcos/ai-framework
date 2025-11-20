#!/usr/bin/env node

/**
 * Chrome Remote Debugging Launcher
 *
 * Platform Support: macOS only
 * - Uses macOS-specific Chrome path: /Applications/Google Chrome.app/...
 * - Uses rsync for profile sync (standard on macOS)
 *
 * For Linux/Windows support, see: https://github.com/Dario-Arcos/ai-framework/issues
 */

import { spawn, execSync } from "node:child_process";
import puppeteer from "puppeteer-core";

const useProfile = process.argv[2] === "--profile";

if (process.argv[2] && process.argv[2] !== "--profile") {
  console.log("Usage: start.js [--profile]");
  console.log("\nOptions:");
  console.log(
    "  --profile  Copy your default Chrome profile (cookies, logins)",
  );
  console.log("\nExamples:");
  console.log("  start.js            # Start with fresh profile");
  console.log("  start.js --profile  # Start with your Chrome profile");
  process.exit(1);
}

// Don't kill user's Chrome - use isolated instance with different port
// User's Chrome sessions remain untouched

// CRITICAL: Clean scraping directory to ensure isolated profile
// Prevents "Who's using Chrome?" selector and session contamination
execSync(`rm -rf "${process.env["HOME"]}/.cache/scraping"`, { stdio: "ignore" });
execSync(`mkdir -p "${process.env["HOME"]}/.cache/scraping/Default"`, { stdio: "ignore" });

if (useProfile) {
  try {
    // Sync ONLY Default profile (not all profiles) to avoid multi-profile selector
    execSync(
      `rsync -a "${process.env["HOME"]}/Library/Application Support/Google/Chrome/Default/" "${process.env["HOME"]}/.cache/scraping/Default/"`,
      { stdio: "pipe" },
    );
  } catch (error) {
    console.error("⚠ Warning: Could not sync Chrome profile. Starting with fresh profile.");
    console.error("  Make sure Chrome is installed at the default location.");
  }
}

// Start Chrome in background (detached so Node can exit)
// Using port 9223 to avoid conflicts with user's Chrome (9222)
spawn(
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  [
    "--remote-debugging-port=9223",
    `--user-data-dir=${process.env["HOME"]}/.cache/scraping`,
    "--profile-directory=Default", // Force single profile (defense in depth)
  ],
  { detached: true, stdio: "ignore" },
).unref();

// Wait for Chrome to be ready by attempting to connect
let connected = false;
for (let i = 0; i < 30; i++) {
  try {
    const browser = await puppeteer.connect({
      browserURL: "http://localhost:9223",
      defaultViewport: null,
    });
    await browser.disconnect();
    connected = true;
    break;
  } catch {
    await new Promise((r) => setTimeout(r, 500));
  }
}

if (!connected) {
  console.error("✗ Failed to connect to Chrome");
  process.exit(1);
}

console.log(
  `✓ Chrome started on :9223${useProfile ? " with your profile" : ""}`,
);
