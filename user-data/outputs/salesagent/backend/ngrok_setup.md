# ngrok Setup for SalesAgent Demo

To receive external leads (WhatsApp/SMS) via Twilio, you must expose your local backend.

## 1. Start ngrok
Run the following command in your terminal:
```bash
ngrok http 8000
```

## 2. Update Webhooks
Once ngrok starts, it will give you a public URL (e.g., `https://xxxx-xxxx.ngrok-free.app`).

- **Twilio**: Update your WhatsApp Sandbox or Phone Number webhook to:
  `https://xxxx-xxxx.ngrok-free.app/leads/whatsapp`
- **Frontend**: Ensure your `.env` (or internal config) points to this URL if you're testing from an external device.

## 3. Verify
Watch the ngrok console or the SalesAgent "Agent Activity" log to see incoming requests being processed in real-time.
