#!/usr/bin/env node

import { spawn, execSync } from "node:child_process";
import puppeteer from "puppeteer-core";

const PORT = 9223;
const PROFILE_DIR = `${process.env["HOME"]}/.cache/web-browser-skill`;

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

// Try to connect to existing instance first
try {
  const browser = await puppeteer.connect({
    browserURL: `http://localhost:${PORT}`,
    defaultViewport: null,
  });
  await browser.disconnect();
  console.log(`⚠️  Chrome already running on :${PORT}`);
  console.log(`   Run 'stop.js' first if you want to change profile mode`);
  process.exit(0);
} catch {
  // No existing instance, will start new one
}

// Setup profile directory
execSync(`mkdir -p ${PROFILE_DIR}`, { stdio: "ignore" });

if (useProfile) {
  // Sync profile with rsync (much faster on subsequent runs)
  const defaultProfilePath = `${process.env["HOME"]}/Library/Application Support/Google/Chrome/`;
  execSync(
    `rsync -a --delete "${defaultProfilePath}" ${PROFILE_DIR}/`,
    { stdio: "pipe" },
  );
}

// Start Chrome in background (detached so Node can exit)
spawn(
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  [
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE_DIR}`,
  ],
  { detached: true, stdio: "ignore" },
).unref();

// Wait for Chrome to be ready by attempting to connect
let connected = false;
for (let i = 0; i < 30; i++) {
  try {
    const browser = await puppeteer.connect({
      browserURL: `http://localhost:${PORT}`,
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
  `✓ Chrome started on :${PORT}${useProfile ? " with your profile" : ""}`,
);
