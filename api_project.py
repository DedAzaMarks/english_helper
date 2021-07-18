# -*- coding: utf-8 -*-
"""API_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TVwsRoyPf8NsKXzg1G5GCORZAhaTtu_c
"""

# бот-помощник в изучении англ языка
# испульзует несколько ресурсов https://rapidapi.com/dpventures/api/wordsapi
# найти API который советует книжки
# найти миленький API (чтобы немного переключиться) аля факты о котиках

# bot token 1761023031:AAF61sXqktr3ar_GYAx_QvWb6pkKd3bin6I

import csv
import requests
import time
from datetime import datetime
import json
import re

# проверка на латиницу


def has_lat(text):
    return bool(re.search('[a-zA-Z]', text))

# проверка на кириллицу


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

# переводчик


def translate(text):
    url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"

    if has_lat(text):
        payload = '{' + f"\n    \"q\": \"{text}\",\n    \"source\": \"en\",\n    \"target\": \"ru\"\n" + '}'
        headers = {
            'content-type': "application/json",
            'x-rapidapi-key': "ea3574af1bmshd6b2a23b074dce5p175996jsne02d16b158f9",
            'x-rapidapi-host': "deep-translate1.p.rapidapi.com"}
        response = requests.request("POST", url, data=payload, headers=headers)

    elif has_cyrillic(text):
        payload = '{' + f"\n    \"q\": \"{text}\",\n    \"source\": \"ru\",\n    \"target\": \"en\"\n" + '}'
        payload = payload.encode()
        headers = {
            'content-type': "application/json",
            'x-rapidapi-key': "ea3574af1bmshd6b2a23b074dce5p175996jsne02d16b158f9",
            'x-rapidapi-host': "deep-translate1.p.rapidapi.com"}
        response = requests.request("POST", url, data=payload, headers=headers)

    else:
        return 'не понимаю :('

    return json.loads(response.text)['data']['translations']['translatedText']


def WordsApi(word, command):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/{command}"
    headers = {
        'x-rapidapi-key': "d741b11b5fmshf10705b3e8ace6ap107f2ajsnbf7ea2a640f6",
        'x-rapidapi-host': "wordsapiv1.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers)
    if command == 'definitions':
        answer = 'definition: ' + json.loads(
            response.text)['definitions'][0]['definition'] + '; ' + 'part Of Speech: ' + json.loads(
            response.text)['definitions'][0]['partOfSpeech']
    else:
        answer = ", ".join(json.loads(response.text)[command])
    return answer


API_link = 'https://api.telegram.org/bot1761023031:AAF61sXqktr3ar_GYAx_QvWb6pkKd3bin6I'
updates = requests.get(API_link + '/getUpdates?offset=-1').json()

commands = [
    '/translate',
    '/synonyms',
    '/antonyms',
    '/definitions',
    '/examples']

state = 'translate'

help_message = '''/help - показать это сообщение
/translate - перевести текст
/synonyms - примеры синонимов к слову
/antonyms - примеры антонимов к слову
/definitions - оперделение слова
/examples - пример использования
'''

err_message = 'Что-то пошло не так'


def get_updates():
    result = requests.get(f'{API_link}/getUpdates').json()
    return result['result']


def send_message(chat_id, text):
    requests.get(f'{API_link}/sendMessage?chat_id={chat_id}&text={text}')


def process(chat_id, message):
    res = ''
    if state == '/translate':
        res = translate(message)
        send_message(chat_id, res)
    else:
        s = ''
        for mes in message.lower().replace(',', '').split():
            word = WordsApi(mes, state[1::])
            res += ' ' + word
            send_message(
                chat_id,
                word if word != '' else 'Для слова ' +
                mes +
                ' нет такой опции')
    return res, datetime.now().time()


def check_message(update_id, chat_id, message):
    global state, help_message, err_message

    f = open('data_chatbot.csv', 'a')
    data = []
    if message == '/help':
        send_message(chat_id, help_message)
        return
    if message[0] == '/':
        if message in commands:
            state = message
        else:
            send_message(chat_id, 'Нет такой команды')
    else:
        data = [update_id, message, state, message, datetime.now().time()]
        bot_reult = process(chat_id, message)
        data.append(bot_reult[0])
        data.append(bot_reult[1])

    with f as file:
        wr = csv.writer(file, quoting=csv.QUOTE_ALL)
        if data:
            wr.writerow(data)
    f.close()


def run():
    global err_message
    # Присваиваем ID последнего отправленного сообщения боту
    update_id = get_updates()[-1]['update_id']
    while True:
        time.sleep(2)
        messages = get_updates()  # Получаем обновления
        for message in messages:
            # Если в обновлении есть ID больше чем ID последнего сообщения,
            # значит пришло новое сообщение
            if update_id < message['update_id']:
                # Присваиваем ID последнего отправленного сообщения боту
                update_id = message['update_id']
                # Отвечаем тому кто прислал сообщение боту
                chat_id = message['message']['chat']['id']
                try:
                    check_message(update_id, chat_id, message['message']['text'])

                except KeyError:
                    send_message(chat_id, err_message)
                    pass


if __name__ == '__main__':
    run()

# идеи по "анализу данных"
# 1) добавлять все запросы в pandas таблицу, под конец дня отправлять разработчику (то есть тебе по твоему id) статистику запросов
# сколько запросов на русском, сколько на английском, сколько всего, какие кнопки чаще всего использовались (это типа покажет работу с pandas),
# датой и разницей в этих показателях с вчерашним днем
#
#
#
#
