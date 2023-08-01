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
import sherlock as sherlock
from twilio.rest import Client
from datetime import date
from datetime import datetime, timedelta
import time 
from googlesearch import search
import requests
from bs4 import BeautifulSoup

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')
# jarvis_phone_number = os.environ.get('JARVIS_PHONE_NUMBER')
# jarvis_phone_number = os.environ.get('SONIA_PHONE_NUMBER')

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
        print(f'this is request_valid: {request_valid}')
        if request_valid:
            return f(*args, **kwargs)
        else:
            print(request.headers.get('X-TWILIO-SIGNATURE', ''))
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
users_history = db['usersHistory']

def update_user_history(phone_number, field, value):
    users_history.insert_one({'phone_number': phone_number, field: value, 'time_stamp': time.time()})

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

def increment_msgCount(phone_number):
    users.update_one({'phone_number': phone_number}, {'$inc': {'msg_count': 1}})

def check_user_message_allocation(phone_number):
    user_details = users.find_one({'phone_number': phone_number, 'msg_allocation': {'$exists': True}})
    current_count = int(user_details['msg_count'])
    allocation_count = int(user_details['msg_allocation'])
    print(f"this is allocation {allocation_count} this is current count {current_count}")
    if current_count < allocation_count:
        return True
    else: 
        return False

def get_user_message_allocation(phone_number):
    allocation = users.find_one({'phone_number': phone_number, 'msg_allocation': {'$exists': True}})
    # current_count = users.get_one({'phone_number': phone_number, 'msg_count': {'$exists': True}}) 
    return allocation

def calculate_age(born, date_format):
    born = datetime.strptime(born, date_format)
    print(f'this is born year {born.year}')
    today = date.today()
    age = int(today.year) - int(born.year) - ((int(today.month), int(today.day)) < (int(born.month), int(born.day)))
    print(f'this is age {age}')
    return age

def validate_date_format(date_string, date_format):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def check_stage_stamp(stage_time_stamp):
    current_stamp = time.time()
    time_difference = current_stamp - stage_time_stamp
    max_time_difference = 3 * 60
    #if current stamp is less than 3 minutes oldtiue
    if time_difference < max_time_difference:
        return True
    else:
        return False  

def google_search(search_query):
    search_results = search(search_query, num_results=3, lang='en')
    return search_results

def google_search_summary(search_query):
    search_results = search(search_query, num_results=1, lang='en') 
    first_result_url = next(search_results)
    get_request = requests.get(first_result_url)
    soup = BeautifulSoup(get_request.text, 'html.parser')
    main_content = soup.find("body")
    text_content = main_content.get_text(separator=" ")
    return text_content

@app.route('/jarvis', methods=['POST'])
# @validate_twilio_request
def jarvis_run():
    bot_name = 'jarvis'
    # try:
    twil_sig = request.headers['X-Twilio-Signature']
    print(f"X-Twilio-Signature: {twil_sig}")
    if twil_sig is not None:
        phone_number = request.form['From']
        message_body = request.form['Body']
        chat_log_name = 'jarvis_chat_log'
        sms_number = os.environ.get('JARVIS_PHONE_NUMBER')
        print(f'this is sms_reply details: {phone_number} {message_body} {chat_log_name} {sms_number}')
        msg_reply = sms_reply(phone_number, message_body, chat_log_name, sms_number, bot_name)
        print(msg_reply)
        return (msg_reply)
    # except KeyError:
    else:
        return('Unauthorized', 401)

@app.route('/sherlock', methods=['POST'])
# @validate_twilio_request
def sherlock_run():
    bot_name = 'sherlock'
    try:
        twil_sig = request.headers['X-Twilio-Signature']
        print(f"X-Twilio-Signature: {twil_sig}")
        phone_number = request.form['From']
        message_body = request.form['Body']
        chat_log_name = 'sherlock_chat_log'
        sms_number = os.environ.get('SHERLOCK_PHONE_NUMBER')
        print(f'this is sms_reply details: {phone_number} {message_body} {chat_log_name} {sms_number}')
        msg_reply = sms_reply(phone_number, message_body, chat_log_name, sms_number, bot_name)
        print(msg_reply)
        return (msg_reply)
    except KeyError:
        return('Unauthorized', 401)

def sms_reply(phone_number, message_body, chat_log_name, sms_number, bot_name):
    if bot_name == 'jarvis':
        signup_new = jarvis.jarvis.signup_new
        signup_complete = jarvis.jarvis.signup_complete
        questions = jarvis.jarvis.questions
        print('jarvis')
    elif bot_name == 'sherlock':
        signup_new = sherlock.sherlock.signup_new
        signup_complete = sherlock.sherlock.signup_complete
        questions = sherlock.sherlock.questions
        print('sherlock')
    elif bot_name == 'sonia':
        signup_new = jarvis.jarvis.signup_new
        signup_complete = jarvis.jarvis.signup_complete
        questions = jarvis.jarvis.questions
        print('sonia')
    elif bot_name == 'john':
        signup_new = jarvis.jarvis.signup_new
        signup_complete = jarvis.jarvis.signup_complete
        questions = jarvis.jarvis.questions
        print('john')

    # Check if the user exists in the database
    user = users.find_one({'phone_number': phone_number})

    # Create a Twilio MessagingResponse object to formulate the response
    resp = MessagingResponse()

    if user is None:
        # If the user does not exist, create a new account and ask for their name
        create_user(phone_number)
        update_user(phone_number, 'stage', 'name')
        update_user(phone_number, 'dob', '')
        update_user(phone_number, 'agree', '')
        update_user(phone_number, 'msg_count', 0)
        update_user(phone_number, 'msg_allocation', 25)
        update_user(phone_number, 'stage_process_time_stamp', time.time())
        resp.message(signup_new)
    else:
        # If the user exists, check the expected input based on the user's stage
        stage = user['stage']
        if stage == 'optout':
            update_user(phone_number, 'stage', '')
            update_user(phone_number, 'dob', '')
            update_user(phone_number, 'agree', '')
            update_user(phone_number, 'stage_process_time_stamp', time.time())
            resp.message(signup_new) 
        if stage == 'user_update':
            update_user(phone_number, 'stage', 'name')
            update_user(phone_number, 'dob', '')
            update_user(phone_number, 'agree', '')
            update_user(phone_number, 'stage_process_time_stamp', time.time())
            resp.message("You requested to updated your user details.  Please respond with your name") 
        # Start checking stage names
        elif stage == 'incomplete':
            update_user(phone_number, 'stage', 'name')
            resp.message("It looks like you still need to add some details.  Please respond with your name")
        elif stage == 'name':
            stage_stamp = user['stage_process_time_stamp']
            if check_stage_stamp(stage_stamp) == True:
                update_user(phone_number, 'name', message_body)
                update_user(phone_number, 'stage', 'email')
                update_user(phone_number, 'stage_process_time_stamp', time.time())
                resp.message("Thank you! Please reply with your email address.")
            else:
                update_user(phone_number, 'stage', 'incomplete')
                resp.message("You took too long to reply with your user registartion details, restarting user registartion, please respond with 'join' to restart")
        
        elif stage == 'email':
            # Update the user's email address and complete the registration
            stage_stamp = user['stage_process_time_stamp']
            if check_stage_stamp(stage_stamp) == True:
                update_user(phone_number, 'email', message_body)
                update_user(phone_number, 'stage', 'agree')
                update_user(phone_number, 'stage_process_time_stamp', time.time())
                resp.message("Please respond with 'agree'. By continuing to send messages to this service, you are agreeing to Our Terms of Service. https://beta.convowithgpt.com/terms-of-service/ and Privacy Policy https://beta.convowithgpt.com/privacy-policy/")
            else:
                update_user(phone_number, 'stage', 'incomplete')
                resp.message("You took too long to reply with your user registartion details, restarting user registartion, please respond with 'join' to restart") 

        elif stage == 'agree':
            agree = message_body
            agree = agree.lower()
            agree = agree.strip()
            if agree == 'agree':
                update_user(phone_number, 'agree', message_body)
                update_user(phone_number, 'stage', 'dob')
                update_user(phone_number, 'stage_process_time_stamp', time.time())
                resp.message("Thank you! Please reply with your birthdate in the format of month day year 01-01-2023")
            else:
                resp.message("Please respond with 'agree'. By continuing to send messages to this service, you are agreeing to Our Terms of Service. https://beta.convowithgpt.com/terms-of-service/ and Privacy Policy https://beta.convowithgpt.com/privacy-policy/")
        elif stage == 'early_tester':
            #handles for early testers and need to agree to TOS
            update_user(phone_number, 'msg_count', 0)
            update_user(phone_number, 'msg_allocation', 25)
            update_user(phone_number, 'stage', 'name')
            update_user(phone_number, 'stage_process_time_stamp', time.time())
            resp.message("Please respond to this this message with your name.  Thank you for trying our eary alpha test! As we move you into our beta test group, we need to run through your account details again and agree to our updated terms or service.")
        elif stage == 'dob':
            born = message_body
            #check date format
            date_format = "%m-%d-%Y"
            if validate_date_format(born, date_format) == True:
                age = calculate_age(born, date_format)
                if age >= 18:
                    update_user(phone_number, 'dob', message_body)
                    update_user(phone_number, 'age', age)
                    update_user(phone_number, 'stage', 'complete') 
                    update_user(phone_number, 'stage_process_time_stamp', time.time())
                    resp.message(signup_complete)
                    resp.message("Ask me anything and I'll do my best to find you the answer.")
                else:
                    resp.message("User registration rejected, we are currently only enrolling users 18 or older.")
                    update_user(phone_number, 'stage', 'incomplete')
                    print(f'Error! User {phone_number}too young to sign up')
            else: 
               resp.message(f"Invaild Birthdate format you entered '{message_body}' Please reply with your birthdate. in the format of month day year 01-01-2023") 
        else:
            agree = user['agree']
            agree = agree.lower()
            agree = agree.strip()
            age = user['age']
            incoming_msg = request.values['Body']

            if age >= 18:
                # print(f'********** this is agree: {agree}')
                if agree == 'agree':
                    value = 'Question'
                    update_user_history(phone_number, value, incoming_msg)
                    if incoming_msg == '?':
                        print('made it to question')
                        message_resp = questions
                        # resp.message(message_resp)
                        twilio_client.messages.create(
                        body=message_resp,
                        from_=sms_number,
                        to=phone_number)
                        update_user_history(phone_number, 'Response', message_resp)

                    elif incoming_msg == '?user':
                        user_details = get_user_message_allocation(phone_number)
                        usr_name = user_details['name']
                        usr_email = user_details['email']
                        usr_age = user_details['age']
                        usr_agree = user_details['agree']
                        usr_msg_count = user_details['msg_count']
                        usr_msg_allocation = user_details['msg_allocation']
                        message_resp = f"Name: {usr_name}\n Email: {usr_email}\n Age: {usr_age}\n Agree to ToS: {usr_agree}\n Messages sent this month: {usr_msg_count}\n Monthly MSG Allocation {usr_msg_allocation}"
                        resp.message(message_resp)
                        update_user_history(phone_number,'Response', message_resp)
                    
                    elif incoming_msg == '?user_update':
                        update_user(phone_number, 'stage', 'user_update')
                        update_user(phone_number, 'stage_process_time_stamp', time.time())
                        message_resp = "User Information update has been requested, please reply with 'update' to continue"
                        resp.message(message_resp)
                        update_user_history(phone_number, 'Response', message_resp)
                         
                    else:
                        check_message_allocation = check_user_message_allocation(phone_number) 
                        if check_message_allocation == True:
                            incoming_msg = incoming_msg.strip()
                            if len(incoming_msg) > 1:
                                check_cmd = incoming_msg[0]
                                if check_cmd == '!':
                                    image_cmd = incoming_msg[:6]
                                    image_prompt = incoming_msg[6:]
                                    image_prompt = image_prompt.strip()
                                    
                                    google_cmd = incoming_msg[:2]
                                    search_query = incoming_msg[2:]
                                    print(f"this is google_cmd {google_cmd}")
                                    print(f"this is search_query {search_query}")
                                    search_query = search_query.strip()
                                    if image_cmd == '!image':
                                        #Dalle API request
                                        resp.message('Generating image, this will take a moment...')
                                        image_url = ch.imageGen(image_prompt)
                                        message_resp = f"Here is your image link **note this link will only last 1 hour {image_url}"
                                        resp.message(message_resp)
                                        update_user_history(phone_number, 'Response', message_resp)
                                        increment_msgCount(phone_number)
                                    elif google_cmd == '!g':
                                        initial_resp = 'I am not familiar with that topic, here is the top Google search result:'
                                        
                                        twilio_client.messages.create(
                                        body=initial_resp,
                                        from_=sms_number,
                                        to=phone_number)

                                        print(f'google search: {search_query}')
                                        search_results = google_search(search_query)
                                        # result = google_search(search_query)
                                        result = next(search_results)
                                        # for result in search_results:
                                        print(result)

                                        twilio_client.messages.create(
                                        body=result,
                                        from_=sms_number,
                                        to=phone_number)

                                        update_user_history(phone_number, 'Response', result)
                                        increment_msgCount(phone_number)

                                else:
                                    print('made it to the gpt response')
                                    initial_response = 'gathering those details \U0001F50D \U0001F4DD \U0001F4CB now...' 
                                    twilio_client.messages.create(
                                        body=initial_response,
                                        from_=sms_number,
                                        to=phone_number)

                                    chat_log = session.get(chat_log_name)

                                    answer, chat_log = ch.askgpt(incoming_msg, chat_log)
                                    session[chat_log_name] = chat_log
                            
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
                                            from_=sms_number,
                                            to=phone_number
                                            )
                                        print(f'this is chunk {chunk}')
                                    update_user_history(phone_number, 'Response', answer)
                                    increment_msgCount(phone_number)
                        else:
                            allocation_number = get_user_message_allocation(phone_number)
                            current_date = datetime.now()
                            # Get the first day of the next month
                            next_month = current_date.replace(day=28) + timedelta(days=4)
                            last_day = next_month - timedelta(days=next_month.day)

                            # Calculate the remaining days in the current month
                            remaining_days = (last_day - current_date).days + 1
                            message_resp = f"You have reached your monthly message limit of {allocation_number['msg_allocation']}, your message allocation will reset in {remaining_days} days."
                            resp.message(message_resp)
                            update_user_history(phone_number, 'Response', message_resp)
                else: 
                    message_resp = "Please respond with 'agree'. By continuing to send messages to this service, you are agreeing to Our Terms of Service. https://beta.convowithgpt.com/terms-of-service/ and Privacy Policy https://beta.convowithgpt.com/privacy-policy/"
                    resp.message(message_resp)
                    update_user(phone_number, 'agree')           
            else:
                resp.message("We are currently only accepting users age 18 years and older.")
                update_user(phone_number, 'incomplete')

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
