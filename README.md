# Aurox Signal Logger

Logs the Aurox signals to a database.

## Configuration
- Copy __.env.sample__ to __.env__ 
- Set environment variables `DATABASE_URL` and `WEBHOOK_PASSWORD`

## Run
Generate certificates using [mkcert](https://github.com/FiloSottile/mkcert)
```
# If it's the firt install of mkcert, run
mkcert -install

# Generate certificate for domain "docker.localhost", "domain.local" and their sub-domains
mkcert -cert-file certs/local-cert.pem -key-file certs/local-key.pem "docker.localhost" "*.docker.localhost" "domain.local" "*.domain.local"
```
Create networks that will be used by Traefik:
```
docker network create proxy
```

Now, start containers with:

```
# Start Traefik
docker-compose -f docker-compose.yaml up -d
# Start "whoami" example
docker-compose -f aurox-logger.yaml up
```


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

### Credits
[Traefik v2 HTTPS (SSL) on localhost](https://github.com/Heziode/traefik-v2-https-ssl-localhost)