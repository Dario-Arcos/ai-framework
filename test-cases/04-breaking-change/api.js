/**
 * User API Module
 * BREAKING CHANGE: getUserById signature changed (removed callback, now returns Promise)
 * This should be detected via BREAKING in commit message
 */

class UserAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  // BREAKING: Changed from callback to Promise
  // OLD: getUserById(id, callback)
  // NEW: getUserById(id) returns Promise
  async getUserById(id) {
    const response = await fetch(`${this.baseUrl}/users/${id}`);
    if (!response.ok) {
      throw new Error(`User not found: ${id}`);
    }
    return response.json();
  }

  // BREAKING: Removed support for username lookup
  // OLD: getUser(idOrUsername)
  // NEW: Only accepts numeric ID
  async getUser(id) {
    if (typeof id !== 'number') {
      throw new TypeError('ID must be a number');
    }
    return this.getUserById(id);
  }

  async updateUser(id, updates) {
    const response = await fetch(`${this.baseUrl}/users/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    return response.json();
  }
}

module.exports = UserAPI;
