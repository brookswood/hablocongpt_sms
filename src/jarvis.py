startlog1 = "You are J.A.R.V.I.S., the AI assistant from the Iron Man series created by Tony Stark."
jarvis_log = f"{startlog1}"

class jarvis:
    chat_log = [
        {"role":"system", "content": jarvis_log}
    ]

    signup_new = "It looks like you are new around here!  I'm J.A.R.V.I.S., your friendly and helpful A.I. assistant. Please respond with your name"

    signup_complete = "Registration complete! Thank you for providing your information and using J.A.R.V.I.S.  For additional instructions on how to use this sevice you can visit this link https://beta.convowithgpt.com/j-a-r-v-i-s/ ask me a question and I'll do my best to get you an answer.  I am in beta right now and may not always respond from time to time.  Be sure to send the message \U0001F4AC of 'Hi'.  This will get my attention \U0001FAE1 so I can answer your questions.  MSG&Data rates may apply.  Reply HELP for help, STOP to cancel."

    questions = 'For detailed instructions on how to use me visit https://beta.convowithgpt.com/j-a-r-v-i-s/.  You can also send me a message as ?user to see your account details.  If you want to edit your user details send me a message of ?user_update'