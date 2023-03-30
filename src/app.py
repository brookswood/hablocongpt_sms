from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
# from twilio.twiml.voice_response import VoiceResponse, Conference, Dial, Say, Gather, Record, Leave, Hangup, Pay, Prompt, Connect
from twilValidator import validate_twilio_request
from chatbot import askgpt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')

@app.route("/sms", methods=['GET', 'POST'])
# @validate_twilio_request()
def sms_reply():
    print(f'valid signature sending message')

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

@app.route('/bot', methods=['POST'])
# @validate_twilio_request()
def bot():
    incoming_msg = request.values['Body']
    chat_log = session.get('chat_log')

    answer, chat_log = askgpt(incoming_msg, chat_log)
    session['chat_log'] = chat_log

    r = MessagingResponse()
    r.message(answer)
    return str(r)

if __name__ == "__main__":
    app.run(debug=True)