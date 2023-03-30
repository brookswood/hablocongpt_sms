from flask import abort, Flask, request, Response
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse, Conference, Dial, Say, Gather, Record, Leave, Hangup, Pay, Prompt, Connect
# from twilValidator import validate_twilio_request
import os

TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

def validate_twilio_request():
    def extra(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            validator = RequestValidator(TWILIO_AUTH_TOKEN)
            https_url = 'https://' + request.url.lstrip('http://') # with ngrok, request.url shows http when https is used, so we need to fix it
            twilio_signature = request.headers.get('X-Twilio-Signature')
            params = request.form
            if not twilio_signature:
                return Response('No signature', 400)  
            elif not validator.validate(https_url, params, twilio_signature):
                return Response('Incorrect signature', 403)
            return f(*args, **kwargs)
        return decorated
    return extra

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
@validate_twilio_request()
def sms_reply():
    # validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))
    # if not validator.validate(request.url, request.form, request.headers.get('X-Twilio-Signature')):
    #     abort(400)

    """Respond to incoming calls with a MMS message."""
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a text message
    msg = resp.message("The Robots are coming! Head for the hills!")

    # Add a picture message
    msg.media(
        "https://farm8.staticflickr.com/7090/6941316406_80b4d6d50e_z_d.jpg"
    )

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
