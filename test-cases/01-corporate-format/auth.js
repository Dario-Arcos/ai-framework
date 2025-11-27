/**
 * OAuth2 Authentication Module
 * Implements basic OAuth flow
 */

class OAuth2Client {
  constructor(clientId, clientSecret, redirectUri) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.redirectUri = redirectUri;
  }

  getAuthorizationUrl() {
    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      response_type: 'code',
      scope: 'read write'
    });
    return `https://oauth.provider.com/authorize?${params}`;
  }

  async exchangeCodeForToken(code) {
    const response = await fetch('https://oauth.provider.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code,
        client_id: this.clientId,
        client_secret: this.clientSecret,
        redirect_uri: this.redirectUri,
        grant_type: 'authorization_code'
      })
    });
    return response.json();
  }
}

module.exports = OAuth2Client;
