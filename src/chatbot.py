import os
from dotenv import load_dotenv
import openai
import hablar
from sherlock import sherlock
from jarvis import jarvis
from john import john
import time

load_dotenv()
openai.api_key = os.environ.get('OPENAI_KEY')
completion = openai.ChatCompletion()
imGen = openai.Image()

start_chat_log = [
    {"role": "system", "content": "You are a helpful assistant."},
]

start_jarvis_chat_log = jarvis.chat_log
start_hablar_chat_log = hablar.hablar.chat_log
start_sherlock_chat_log = sherlock.chat_log
start_hablar_translate_chat_log = hablar.hablarTranslate.chat_translate_log
start_john1_chat_log = john.chat_log

def askgpt(question, chat_log=None):
    
    if chat_log is None:
        chat_log = start_jarvis_chat_log
    chat_log = chat_log + [{'role': 'user', 'content': question}]
    
    try:
        response = completion.create(model='gpt-3.5-turbo', messages=chat_log)
    except:
        time.sleep(0.1)
        try: 
            response = completion.create(model='gpt-3.5-turbo', messages=chat_log)
        except:
            time.sleep(0.1)
            try:
                response = completion.create(model='gpt-3.5-turbo', messages=chat_log)  
            except:
                answer = 'Wow! \U0001F632\U0001F64B\U0001F3C3\U0001F4BC Due to high demand I am busy, can you ask your question again in 5 seconds?'
            else:
                answer = response.choices[0]['message']['content']
                chat_log = chat_log + [{'role': 'assistant', 'content': answer}]
        else:
            answer = response.choices[0]['message']['content']
            chat_log = chat_log + [{'role': 'assistant', 'content': answer}]
    else:
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

def askhablartranslate(question, hablar_translate_chat_log=None):
    if hablar_translate_chat_log is None:
        hablar_translate_chat_log = start_hablar_translate_chat_log
    hablar_translate_chat_log = hablar_translate_chat_log + [{'role': 'user', 'content': question}]
    response = completion.create(model='gpt-3.5-turbo', messages=hablar_translate_chat_log)
    answer = response.choices[0]['message']['content']
    hablar_translate_chat_log = hablar_translate_chat_log + [{'role': 'assistant', 'content': answer}]
    # print(f'this is chatlog {hablar_chat_log}')
    return answer, hablar_translate_chat_log

def asksherlock(question, sherlock_chat_log=None):
    if sherlock_chat_log is None:
        sherlock_chat_log = start_sherlock_chat_log
    sherlock_chat_log = sherlock_chat_log + [{'role': 'user', 'content': question}]
    response = completion.create(model='gpt-3.5-turbo', messages=sherlock_chat_log)
    answer = response.choices[0]['message']['content']
    sherlock_chat_log = sherlock_chat_log + [{'role': 'assistant', 'content': answer}]
    return answer, sherlock_chat_log

def askjohn(question, john1_chat_log=None):
    if john1_chat_log is None:
        john1_chat_log = start_john1_chat_log
    john1_chat_log = john1_chat_log + [{'role': 'user', 'content': question}]
    response = completion.create(model='gpt-3.5-turbo', messages=john1_chat_log)
    answer = response.choices[0]['message']['content']
    john1_chat_log = john1_chat_log + [{'role': 'assistant', 'content': answer}]
    return answer, john1_chat_log

def imageGen(image_prompt):
    response = imGen.create(prompt=image_prompt,n=1,size="1024x1024")
    return (response["data"][0]["url"])