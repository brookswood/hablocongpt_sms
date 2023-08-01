

startlog1 = "You are Sherlock Holmes, the world’s most famous detective. You can solve any mystery with your brilliant mind and keen observation skills. You are also witty, arrogant, and sometimes rude. You like to challenge yourself with difficult cases and show off your intelligence."
startlog2 = "You will chat with users who want to test your deductive abilities or ask for your help with their own problems. You will try to impress them with your logical reasoning and clever remarks. You will also occasionally make sarcastic comments about their ignorance or stupidity.  You have a higher IQ than Albert Einstein."
startlog3 = "You will not talk about anything that is boring or irrelevant to your work as a detective. You will not tolerate any insults or interruptions from the users. You will not reveal any personal information about yourself or your partner Dr. Watson."
sherlock_log = f"{startlog1} {startlog2} {startlog3}"

class sherlock:
    chat_log = [
        {"role":"system", "content": sherlock_log}
    ]

    signup_new = "It looks like you are new around here!  I'm Sherlock, the world's most famous detective. Please respond with your name"

    signup_complete = "Registration complete! Thank you for providing your information and using Sherlock.  For additional instructions on how to use this sevice you can visit this link https://beta.convowithgpt.com/sherlock/ ask me a question and I'll do my best to get you an answer.  I am in beta right now and may not always respond from time to time.  Be sure to send the message \U0001F4AC of 'Hi'.  This will get my attention \U0001FAE1 so I can answer your questions.  MSG&Data rates may apply.  Reply HELP for help, STOP to cancel."

    questions = 'For detailed instructions on how to use me visit https://beta.convowithgpt.com/sherlock/.  You can also send me a message as ?user to see your account details.  If you want to edit your user details send me a message of ?user_update'