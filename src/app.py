from flask import Flask, request, session, abort
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from functools import wraps
import chatbot as ch 
import os

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')

def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', ''))

        # Continue processing the request if it's valid, return a 403 error if
        # it's not
        if request_valid:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function

@app.route('/sms', methods=['POST'])
@validate_twilio_request
# @validate_twilio_request()
def bot():
    incoming_msg = request.values['Body']
    chat_log = session.get('chat_log')

    answer, chat_log = ch.askgpt(incoming_msg, chat_log)
    session['chat_log'] = chat_log
    
    print(answer)

    r = MessagingResponse()
    r.message(answer)
    return str(r)


@app.route('/hablar', methods=['POST'])
@validate_twilio_request
def hablarbot():
    incoming_msg = request.values['Body']
    hablar_chat_log = session.get('hablar_chat_log')

    answer, hablar_chat_log = ch.askhablar(incoming_msg, hablar_chat_log)
    session['hablar_chat_log'] = hablar_chat_log

    print(answer)

    r = MessagingResponse()
    r.message(answer)
    return str(r)

@app.route('/hablar_translate', methods=['POST'])
@validate_twilio_request
def hablarbot_translate():
    incoming_msg = request.values['Body']
    hablar_translate_chat_log = session.get('hablar_translate_chat_log')

    answer, hablar_translate_chat_log = ch.askhablartranslate(incoming_msg, hablar_translate_chat_log)
    session['hablar_translate_chat_log'] = hablar_translate_chat_log

    print(answer)

    r = MessagingResponse()
    r.message(answer)
    return str(r)


@app.route('/sherlock', methods=['POST'])
@validate_twilio_request
def sherlockbot():
    incoming_msg = request.values['Body']
    sherlock_chat_log = session.get('sherlock_chat_log')

    print(f'this is sherlock session {sherlock_chat_log}')

    answer, sherlock_chat_log = ch.asksherlock(incoming_msg, sherlock_chat_log)
    session['sherlock_chat_log'] = sherlock_chat_log

    print(answer)

    r = MessagingResponse()
    r.message(answer)
    return str(r)

if __name__ == "__main__":
    app.run(debug=True, port=5001)