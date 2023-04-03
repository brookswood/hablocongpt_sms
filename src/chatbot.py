import os
from dotenv import load_dotenv
import openai
from hablar import hablar
from sherlock import sherlock

load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')
completion = openai.ChatCompletion()

start_chat_log = [
    {"role": "system", "content": "You are a helpful assistant."},
]

start_hablar_chat_log = hablar.chat_log
start_sherlock_chat_log = sherlock.chat_log


def askgpt(question, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    chat_log = chat_log + [{'role': 'user', 'content': question}]
    response = completion.create(model='gpt-3.5-turbo', messages=chat_log)
    answer = response.choices[0]['message']['content']
    chat_log = chat_log + [{'role': 'assistant', 'content': answer}]
    # print(f'this is chatlog {chat_log}')
    return answer, chat_log

def askhablar(question, hablar_chat_log=None):
    if hablar_chat_log is None:
        hablar_chat_log = start_hablar_chat_log
    hablar_chat_log = hablar_chat_log + [{'role': 'user', 'content': question}]
    response = completion.create(model='gpt-3.5-turbo', messages=hablar_chat_log)
    answer = response.choices[0]['message']['content']
    hablar_chat_log = hablar_chat_log + [{'role': 'assistant', 'content': answer}]
    # print(f'this is chatlog {hablar_chat_log}')
    return answer, hablar_chat_log

def asksherlock(question, sherlock_chat_log=None):
    if sherlock_chat_log is None:
        sherlock_chat_log = start_sherlock_chat_log
    sherlock_chat_log = sherlock_chat_log + [{'role': 'user', 'content': question}]
    response = completion.create(model='gpt-3.5-turbo', messages=sherlock_chat_log)
    answer = response.choices[0]['message']['content']
    sherlock_chat_log = sherlock_chat_log + [{'role': 'assistant', 'content': answer}]
    return answer, sherlock_chat_log