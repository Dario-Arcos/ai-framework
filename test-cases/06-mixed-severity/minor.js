/**
 * Rate Limiter
 * MINOR ISSUE: Magic numbers should be constants
 */

class RateLimiter {
  constructor() {
    this.requests = new Map();
  }

  // MINOR: Magic number 100 should be a named constant
  isAllowed(clientId) {
    const now = Date.now();
    const clientRequests = this.requests.get(clientId) || [];

    // MINOR: Magic number 60000 (1 minute in ms)
    const recentRequests = clientRequests.filter(time => now - time < 60000);

    // MINOR: Magic number 100 (max requests)
    if (recentRequests.length >= 100) {
      return false;
    }

    recentRequests.push(now);
    this.requests.set(clientId, recentRequests);
    return true;
  }

  // MINOR: Magic number 3600000 (1 hour in ms)
  cleanup() {
    const now = Date.now();
    for (const [clientId, requests] of this.requests) {
      const recent = requests.filter(time => now - time < 3600000);
      if (recent.length === 0) {
        this.requests.delete(clientId);
      } else {
        this.requests.set(clientId, recent);
      }
    }
  }
}

module.exports = RateLimiter;
