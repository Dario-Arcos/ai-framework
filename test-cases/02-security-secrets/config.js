/**
 * Application Configuration
 * SECURITY ISSUE: Hardcoded credentials (should trigger Security Review High)
 * NOTE: These are FAKE credentials for testing purposes
 */

const config = {
  database: {
    host: 'localhost',
    port: 5432,
    user: 'admin',
    password: 'admin123'
  },

  api: {
    // CRITICAL: Pattern matches API_KEY detection
    API_KEY: 'sk-test-abc123',
    SECRET_KEY: 'secret_456',
    endpoint: 'https://api.service.com/v1',
    timeout: 30000
  },

  oauth: {
    // CRITICAL: Pattern matches TOKEN detection
    GITHUB_TOKEN: 'ghp_fake123',
    PRIVATE_KEY: 'pk_test_xyz',
    redirectUri: 'http://localhost:3000/callback'
  }
};

module.exports = config;
