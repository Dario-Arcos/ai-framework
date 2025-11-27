/**
 * User Query Module
 * CRITICAL ISSUE: SQL Injection vulnerability
 */

class UserQuery {
  constructor(database) {
    this.db = database;
  }

  // CRITICAL: SQL Injection - string concatenation in query
  async findUserByEmail(email) {
    const query = `SELECT * FROM users WHERE email = '${email}'`;
    const result = await this.db.query(query);
    return result.rows[0];
  }

  // CRITICAL: SQL Injection - unsanitized input
  async searchUsers(searchTerm) {
    const query = `SELECT * FROM users WHERE name LIKE '%${searchTerm}%'`;
    return await this.db.query(query);
  }
}

module.exports = UserQuery;
