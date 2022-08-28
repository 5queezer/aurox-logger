# Aurox Signal Logger

Logs the Aurox webhook alerts to the database.

## Configuration
- Copy __.env.sample__ to __.env__ 
- Set environment variables `DATABASE_URL` and `WEBHOOK_PASSWORD`


## Aurox Webhook Format
The Aurox signal must have the default message and the default json fields. Add a password field. The request has following format:
```
{
  "message": "🔔 BTC Long 💱 Binance Futures:BTCUSDT ⏱️ 5 Minutes\n\nAND\n|  AI BGMCv1/Signal <None> became TRUE ✔️\n|  Volume Osc(5,10) <0> is less than <> ✔️",
  "price": "36.881",
  "symbol": "binance-futures:BTCUSDT",
  "timeUnit": "5 Minutes",
  "timestamp": "2022-08-23T18:36:53.733Z",
  "password": "Iwonttellyou123"
}
```
#### ⚠️ Danger
Never run the server without SSL (https), since the password would be exposed over the network.

