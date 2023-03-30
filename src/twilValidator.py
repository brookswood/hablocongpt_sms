from flask import request, Response
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
import os

TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

def validate_twilio_request():
    #only works in prod, sandbox validation is handled by phone number
    def extra(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            validator = RequestValidator(TWILIO_AUTH_TOKEN)
            https_url = 'https://' + request.url.lstrip('http://') # with ngrok, request.url shows http when https is used, so we need to fix it
            twilio_signature = request.headers.get('X-Twilio-Signature')
            params = request.form
            if not twilio_signature:
                return MessagingResponse('No signature', 400)  
            elif not validator.validate(https_url, params, twilio_signature):
                return MessagingResponse('Incorrect signature', 403)
            return f(*args, **kwargs)
        return decorated
    return extra