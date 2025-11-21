#!/usr/bin/env node

import { execSync } from "node:child_process";
import puppeteer from "puppeteer-core";

const PORT = 9223;

// Try to close browser gracefully first
try {
  const browser = await puppeteer.connect({
    browserURL: `http://localhost:${PORT}`,
    defaultViewport: null,
  });
  await browser.close();
  console.log(`✓ Chrome stopped on :${PORT}`);
} catch {
  console.log(`✓ No Chrome instance running on :${PORT}`);
}
