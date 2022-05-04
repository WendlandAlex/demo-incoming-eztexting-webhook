This is a demo of the method to validate authentication headers when receiving sms over webhook from EZ Texting. The provider sends an hmacSHA1 hash of the request body in an `X-Signature` header, signed with a shared secret key. 

This app mocks up a "sign up based on day" inbound sms processing

Usage:
- open an Ngrok tunnel `ngrok http 8080` and record the ephemeral URL in `.env`
- define a shared secret in `.env`
- run `redis-server` on localhost with port 6379 (or elsewhere and set the environment variable `REDIS_URL` in .env)
- open up a bunch of terminals
    - webhook listener `python3 main.py`
    - inbound sms processor task queue `python3 in_tasks.py`
    - outbound confirmation sender task queue `python3 out_tasks.py`
    - random "sms" sending loop `python3 test_sending.py`

TODO: Package the queue workers as supervisord processes or docker containers to make start/stop easier