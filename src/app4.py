from functools import wraps
from flask import Flask, request, session, abort, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from pymongo import MongoClient
from dotenv import load_dotenv
import chatbot as ch 
import os
import john as john
from twilio.rest import Client
import time 

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')
john_phone_number = os.environ.get('JOHN_PHONE_NUMBER')

# Load environment variables from the .env file
load_dotenv()

twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')

# Initialize the Twilio client
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Retrieve the MongoDB username and password from environment variables
mongo_username = os.getenv('MONGO_USERNAME')
mongo_password = os.getenv('MONGO_PASSWORD')

# MongoDB connection parameters
# mongo_host = 'localhost'
mongo_host = os.getenv('MONGO_HOST')
# mongo_port = '27017'
mongo_auth_db = 'admin'

# Connect to MongoDB with authentication
mongo_uri = f'mongodb+srv://{mongo_username}:{mongo_password}@{mongo_host}/{mongo_auth_db}'
client = MongoClient(mongo_uri)
db = client['convos']
users = db['users']

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

def create_user(phone_number):
    # Create a new user document with the given phone number
    user = {
        'phone_number': phone_number,
        'name': None,
        'email': None,
        'stage': 'name'  # Indicates the next expected input from the user
    }
    users.insert_one(user)

def update_user(phone_number, field, value):
    # Update the specified field for the user with the given phone number
    users.update_one({'phone_number': phone_number}, {'$set': {field: value}})

@app.route('/sms', methods=['POST'])
@validate_twilio_request
def sms_reply():
    # Get the sender's phone number and the message body
    phone_number = request.form['From']
    message_body = request.form['Body']

    # Check if the user exists in the database
    user = users.find_one({'phone_number': phone_number})

    # Create a Twilio MessagingResponse object to formulate the response
    resp = MessagingResponse()

    if user is None:
        # If the user does not exist, create a new account and ask for their name
        create_user(phone_number)
        resp.message("It looks like you are new around here!  I'm John, your Theology Biblical Scholar and expert of the Bible.  If you want to keep receiving messages, Please reply with your name.")
    else:
        # If the user exists, check the expected input based on the user's stage
        stage = user['stage']
        if stage == 'name':
            # Update the user's name and ask for their email address
            update_user(phone_number, 'name', message_body)
            update_user(phone_number, 'stage', 'email')
            resp.message("Thank you! Please reply with your email address.")
        elif stage == 'email':
            # Update the user's email address and complete the registration
            update_user(phone_number, 'email', message_body)
            update_user(phone_number, 'stage', 'complete')
            resp.message("Registration complete! Thank you for providing your information and using John from https://convoswithgpt.com/john ask me a question and I'll do my best to get you an answer.  I am in beta right now and may not always respond from time to time.  Be sure to send the message \U0001F4AC of 'Hi'.  This will get my attention \U0001FAE1 so I can answer your questions.  MSG&Data rates may apply.  Reply HElP for help, STOP to cancel.")
        else:
            initial_response = 'gathering those details \U0001F50D \U0001F4DD \U0001F4CB \U0001F4C3 now...' 
            twilio_client.messages.create(
                body=initial_response,
                from_=john_phone_number,
                to=phone_number
            )

            incoming_msg = request.values['Body']
            chat_log = session.get('johns_chat_log')

            answer, chat_log = ch.askjohn(incoming_msg, chat_log)
            session['johns_chat_log'] = chat_log
    
            print(f'sending answer to {user} in chunks')
            print(answer)

            # Define the maximum number of characters per SMS message
            max_chars = 1500

            # Split the response into chunks if it exceeds the maximum character limit
            response_chunks = [answer[i:i + max_chars] for i in range(0, len(answer), max_chars)]

            # Send each chunk as a separate SMS message
            for chunk in response_chunks:
                time.sleep(0.02)
                twilio_client.messages.create(
                    body=chunk,
                    from_=john_phone_number,
                    to=phone_number
                )

                # print(f'this is chunk {chunk}')

        return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
