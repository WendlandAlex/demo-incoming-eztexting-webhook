This is a demo of the method to validate authentication headers when receiving sms over webhook from EZ Texting. The provider sends an hmacSHA1 hash of the request body in an 'X-Signature' header, signed with a shared secret key. 

This app mocks up a "sign up based on day" inbound sms processing

Usage:
- open an Ngrok tunnel on port 8080 and record the ephemeral URL in .env
- define a shared secret in .env
- run the flask app in main.py in one terminal, run the test_send.py loop in another

TODO: demonstrate dispatching messages to queue with Redis and rq to parse messages offline with regex and send customized responses
