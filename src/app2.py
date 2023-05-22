from functools import wraps
from flask import Flask, request, session, abort, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from pymongo import MongoClient
from dotenv import load_dotenv
import chatbot as ch 
import os
import jarvis as jarvis
from twilio.rest import Client
from datetime import date
from datetime import datetime
import time 

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')
jarvis_phone_number = os.environ.get('JARVIS_PHONE_NUMBER')

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

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def validate_date_format(date_string, date_format):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

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
        update_user(phone_number, 'stage', 'name')
        resp.message("It looks like you are new around here!  I'm J.A.R.V.I.S., your friendly and helpful A.I. assistant. Please respond with your name")
    else:
        # If the user exists, check the expected input based on the user's stage
        stage = user['stage']
        # Start checking stage names
        if stage == 'name':
            # Update the user's name and ask for their email address
            update_user(phone_number, 'name', message_body)
            update_user(phone_number, 'stage', 'email')
            resp.message("Thank you! Please reply with your email address.")
        elif stage == 'email':
            # Update the user's email address and complete the registration
            update_user(phone_number, 'email', message_body)
            update_user(phone_number, 'stage', 'agree')
            resp.message("Please respond with 'yes' or 'agree'. By continuing to send messages to this service, you are agreeing to Our Terms of Service. https://convoswithgpt.com/tos and Privacy Policy https://beta.convowithgpt.com/privacy-policy/")
        elif stage == 'agree':
            update_user(phone_number, 'agree', message_body)
            update_user(phone_number, 'stage', 'dob')
            resp.message("Thank you! Please reply with your birthdate. in the format of month day year 01-01-2023")
        elif stage == 'dob':
            born = message_body
            #check date format
            date_format = "%m-%d-%Y"
            if validate_date_format(born, date_format) == True:
                age = calculate_age(born)
                if born <= 18:
                    update_user(phone_number, 'dob', message_body)
                    update_user(phone_number, 'age', age)
                    update_user(phone_number, 'stage', 'name') 
                    resp.message("Registration complete! Thank you for providing your information and using J.A.R.V.I.S. from https://beta.convoswithgpt.com/jarvis ask me a question and I'll do my best to get you an answer.  I am in beta right now and may not always respond from time to time.  Be sure to send the message \U0001F4AC of 'Hi'.  This will get my attention \U0001FAE1 so I can answer your questions.  MSG&Data rates may apply.  Reply HElP for help, STOP to cancel.")
                else:
                    resp.message("User registration rejected, we are currently only enrolling users 18 or older.")
                    print(f'Error! User {phone_number}too young to sign up')
        else:
            if user['agree'] is None:
                agree = 'empty'
            else:
                agree = user['agree']
            age = user['age']
            if agree == 'yes' or agree == 'agree':
                if age <= 18:
                    initial_response = 'gathering those details \U0001F50D \U0001F4DD \U0001F4CB now...' 
                    twilio_client.messages.create(
                        body=initial_response,
                        from_=jarvis_phone_number,
                        to=phone_number
                    )

                    incoming_msg = request.values['Body']
                    chat_log = session.get('jarivs_chat_log')

                    answer, chat_log = ch.askgpt(incoming_msg, chat_log)
                    session['jarvis_chat_log'] = chat_log
            
                    print(f'sending answer to {user}')
                    # print(answer)

                    # Define the maximum number of characters per SMS message
                    max_chars = 1500

                    # Split the response into chunks if it exceeds the maximum character limit
                    response_chunks = [answer[i:i + max_chars] for i in range(0, len(answer), max_chars)]

                    # Send each chunk as a separate SMS message
                    for chunk in response_chunks:
                        time.sleep(0.02)
                        twilio_client.messages.create(
                            body=chunk,
                            from_=jarvis_phone_number,
                            to=phone_number
                        )

                        print(f'this is chunk {chunk}')
            else:
                print('user has not yet agreed to TOS')
                # update_user(phone_number, 'agree', message_body)
                update_user(phone_number, 'stage', 'agree')
                resp.message("Our Terms of Service and Privacy Policy have recently updated, you can read them here https://beta.convowithgpt.com/terms-of-service/ & https://beta.convowithgpt.com/privacy-policy/. Please respond with 'yes' or 'agree'. By continuing to send messages to this service, you are agreeing to Our Terms of Service.")

        return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
