from flask import abort, Flask, request
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from twilValidator import validate_twilio_request
import os

# def validate_twilio_request(f):
#     """Validates that incoming requests genuinely originated from Twilio"""
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # Create an instance of the RequestValidator class
#         validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

#         # Validate the request using its URL, POST data,
#         # and X-TWILIO-SIGNATURE header
#         request_valid = validator.validate(
#             request.url,
#             request.form,
#             request.headers.get('X-TWILIO-SIGNATURE', ''))

#         # Continue processing the request if it's valid, return a 403 error if
#         # it's not
#         if request_valid:
#             return f(*args, **kwargs)
#         else:
#             return abort(403)
#     return decorated_function

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
@validate_twilio_request
def sms_reply():
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
