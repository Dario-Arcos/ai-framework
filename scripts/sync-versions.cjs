#!/usr/bin/env node
/**
 * Version Synchronization Script
 *
 * Automatically synchronizes version information across:
 * - human-handbook/.vitepress/config.js (themeConfig.version + themeConfig.previousVersion)
 * - README.md (version references)
 * - .claude-plugin/plugin.json (plugin version)
 * - Validates CHANGELOG.md entry exists for new version
 *
 * Triggered by: npm version <calver-string> (e.g. npm version 2026.1.0)
 * Exit codes: 0 (success), 1 (CHANGELOG validation failure)
 */

const fs = require("fs");
const path = require("path");

// File paths
const PACKAGE_JSON_PATH = path.join(__dirname, "../package.json");
const CHANGELOG_PATH = path.join(__dirname, "../CHANGELOG.md");
const CONFIG_JS_PATH = path.join(
  __dirname,
  "../human-handbook/.vitepress/config.js",
);
const README_PATH = path.join(__dirname, "../README.md");
const PLUGIN_JSON_PATH = path.join(__dirname, "../.claude-plugin/plugin.json");

function main() {
  try {
    // Step 1: Read current version from package.json
    const pkg = require(PACKAGE_JSON_PATH);
    const version = pkg.version;
    console.log(`[sync-versions] New version: ${version}`);

    // Step 2: Parse CHANGELOG.md for previous version
    const previousVersion = extractPreviousVersion(version);
    console.log(`[sync-versions] Previous version: ${previousVersion}`);

    // Step 3: Update .vitepress/config.js
    updateConfigJS(version, previousVersion);
    console.log(`[sync-versions] ✓ Updated config.js`);

    // Step 4: Update README.md
    updateReadme(version);
    console.log(`[sync-versions] ✓ Updated README.md`);

    // Step 5: Update .claude-plugin/plugin.json
    updatePluginJSON(version);
    console.log(`[sync-versions] ✓ Updated plugin.json`);

    // Step 6: Sync CHANGELOG to docs
    syncDocsChangelog();
    console.log(`[sync-versions] ✓ Synced docs/changelog.md`);

    // Step 7: Validate CHANGELOG.md entry exists
    validateChangelog(version);
    console.log(`[sync-versions] ✓ CHANGELOG.md validated`);

    console.log(`[sync-versions] ✅ Success - All files synchronized`);
    process.exit(0);
  } catch (error) {
    console.error(`[sync-versions] ❌ Error: ${error.message}`);
    process.exit(1);
  }
}

function extractPreviousVersion(currentVersion) {
  if (!fs.existsSync(CHANGELOG_PATH)) {
    console.warn(
      `[sync-versions] ⚠️  CHANGELOG.md not found - using current version as previousVersion`,
    );
    return currentVersion;
  }

  const changelog = fs.readFileSync(CHANGELOG_PATH, "utf8");
  const versionRegex = /## \[(\d+\.\d+\.\d+)\]/g;
  const matches = [...changelog.matchAll(versionRegex)];

  if (matches.length === 0) {
    console.warn(
      `[sync-versions] ⚠️  No versions found in CHANGELOG.md - using current version as previousVersion`,
    );
    return currentVersion;
  }

  if (matches.length === 1) {
    console.warn(
      `[sync-versions] ⚠️  Only one version in CHANGELOG.md - using current version as previousVersion`,
    );
    return currentVersion;
  }

  return matches[1][1];
}

function updateConfigJS(version, previousVersion) {
  if (!fs.existsSync(CONFIG_JS_PATH)) {
    throw new Error(`config.js not found at ${CONFIG_JS_PATH}`);
  }

  let config = fs.readFileSync(CONFIG_JS_PATH, "utf8");

  config = config.replace(/version:\s*["'][\d.]+["']/, `version: "${version}"`);
  config = config.replace(
    /previousVersion:\s*["'][\d.]+["']/,
    `previousVersion: "${previousVersion}"`,
  );

  fs.writeFileSync(CONFIG_JS_PATH, config, "utf8");
}

function updateReadme(version) {
  if (!fs.existsSync(README_PATH)) {
    throw new Error(`README.md not found at ${README_PATH}`);
  }

  let readme = fs.readFileSync(README_PATH, "utf8");

  readme = readme.replace(
    /\*\*Version:\*\*\s+[\d.]+([-+][\w.]+)?(?:\s+\([^)]+\))?/g,
    `**Version:** ${version}`,
  );

  fs.writeFileSync(README_PATH, readme, "utf8");
}

function updatePluginJSON(version) {
  if (!fs.existsSync(PLUGIN_JSON_PATH)) {
    throw new Error(`plugin.json not found at ${PLUGIN_JSON_PATH}`);
  }

  const plugin = JSON.parse(fs.readFileSync(PLUGIN_JSON_PATH, "utf8"));
  plugin.version = version;

  fs.writeFileSync(PLUGIN_JSON_PATH, JSON.stringify(plugin, null, 2) + "\n", "utf8");
}

function syncDocsChangelog() {
  const DOCS_CHANGELOG_PATH = path.join(
    __dirname,
    "../human-handbook/docs/changelog.md",
  );

  if (!fs.existsSync(CHANGELOG_PATH)) {
    throw new Error(`CHANGELOG.md not found - cannot sync to docs`);
  }

  fs.copyFileSync(CHANGELOG_PATH, DOCS_CHANGELOG_PATH);
}

function validateChangelog(version) {
  if (!fs.existsSync(CHANGELOG_PATH)) {
    throw new Error(`CHANGELOG.md not found - cannot validate version entry`);
  }

  const changelog = fs.readFileSync(CHANGELOG_PATH, "utf8");
  const versionHeader = `## [${version}]`;

  if (!changelog.includes(versionHeader)) {
    throw new Error(
      `CHANGELOG.md validation failed: No entry found for version ${version}\n` +
        `Please add a changelog entry with header: ${versionHeader}`,
    );
  }
}

// Execute
main();
