startlog1 = "You are Robert Langdon, a professor of religious iconology and symbology at Harvard University"
startlog2 = "I will provide some topics or questions related to Christianity, Jesus, and faith, and it will be your job to explore these concepts in depth."
startlog3 = "This might involve researching various theological concepts and proposing Bible-based insights with practical applications and references from the bible."
john_log = f"{startlog1} {startlog2} {startlog3}"

class john:
    chat_log = [
        {"role":"system", "content": john_log}
    ]

    signup_new = "It looks like you are new around here!  I'm Robert Langdon, a professor of religious iconology and symbology at Harvard University Please respond with your name"

    signup_complete = "Registration complete! Thank you for providing your information and using our service.  For additional instructions on how to use this sevice you can visit this link https://beta.convowithgpt.com/john/ ask me a question and I'll do my best to get you an answer.  I am in beta right now and may not always respond from time to time.  Be sure to send the message \U0001F4AC of 'Hi'.  This will get my attention \U0001FAE1 so I can answer your questions.  MSG&Data rates may apply.  Reply HELP for help, STOP to cancel."

    questions = 'For detailed instructions on how to use me visit https://beta.convowithgpt.com/john/.  You can also send me a message as ?user to see your account details.  If you want to edit your user details send me a message of ?user_update'