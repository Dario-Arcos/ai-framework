/**
 * Payment Processing Module
 * NO TESTS: Should trigger ⚠️ Tests observation
 */

class PaymentProcessor {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://payments.api.com';
  }

  async processPayment(amount, currency, cardToken) {
    const response = await fetch(`${this.baseUrl}/charges`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount: Math.round(amount * 100), // Convert to cents
        currency: currency.toUpperCase(),
        source: cardToken,
        description: 'Payment processing'
      })
    });

    if (!response.ok) {
      throw new Error(`Payment failed: ${response.statusText}`);
    }

    return response.json();
  }

  async refundPayment(chargeId, amount) {
    const response = await fetch(`${this.baseUrl}/refunds`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        charge: chargeId,
        amount: amount ? Math.round(amount * 100) : undefined
      })
    });

    return response.json();
  }
}

module.exports = PaymentProcessor;
