import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')
completion = openai.ChatCompletion()

start_chat_log = [
    {"role": "system", "content": "You are a helpful assistant."},
]

def askgpt(question, chat_log=None):
    if chat_log is None:
        chat_log = start_chat_log
    chat_log = chat_log + [{'role': 'user', 'content': question}]
    response = completion.create(model='gpt-3.5-turbo', messages=chat_log)
    answer = response.choices[0]['message']['content']
    chat_log = chat_log + [{'role': 'assistant', 'content': answer}]
    return answer, chat_log