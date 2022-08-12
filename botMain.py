#!/usr/bin/env python

import logging
import os
from flask import Flask, request, jsonify
import requests as rq
import pathlib
import json
from randomcoordinatesinradius import random_coordinates

#variables
path = pathlib.Path(__file__).parent.resolve()
token_env='token_randLocBot'
if token_env in os.environ:
    token=str(os.environ[token_env])
else: exit('token is None')
tgUrl = lambda method: f"https://api.telegram.org/bot{token}/{method}"
app = Flask(__name__)

def processMessage(message):
    if 'location' in message:
        longitude, latitude = random_coordinates([message['location']['longitude'], message['location']['latitude']], getDist(message['chat']['id']))
        answer={'chat_id':message['chat']['id'], 'latitude':latitude, 'longitude':longitude}
        rpost = rq.post(tgUrl('sendLocation'), json=answer)
    if 'text' in message:
        if '/setdistance' in message['text']:
            if os.path.exists(f'{path}/data.json'):
                with open(f'{path}/data.json', 'r') as f:
                    data = json.load(f)
            else:
                data={}
            try:
                data[str(message['chat']['id'])] = float(message['text'].replace('/setdistance', '').replace(' ',''))
                rpost = rq.post(tgUrl('sendMessage'), json={'chat_id':message['chat']['id'], 'text': f"Current distance = <b>{float(message['text'].replace('/setdistance', '').replace(' ',''))}</b> meters.",'parse_mode':'HTML'})
            except Exception as e:
                logging.critical(e)
                rpost = rq.post(tgUrl('sendMessage'), json={'chat_id':message['chat']['id'], 'text': "<i>command is incorrect.</i>\nTry '/setdistance %distance%'\n%distance% is any number of meters.",'parse_mode':'HTML'})
                return 'ERROR'
            with open(f'{path}/data.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=4 )
        elif '/start' in message['text'] or '/help' in message['text']:
            rpost = rq.post(tgUrl('sendMessage'), json={'chat_id':message['chat']['id'], 'text': "send me location and i'll send you random place nearby.\nUse '/setdistance' comand to to set max distans of location.",'parse_mode':'HTML'})
        elif '/distance' in message['text']:
            rpost = rq.post(tgUrl('sendMessage'), json={'chat_id':message['chat']['id'], 'text': f"Current distance = <b>{getDist(message['chat']['id'])}</b> meters.",'parse_mode':'HTML'})

def getDist(chat_id):
    if os.path.exists(f'{path}/data.json'):
        with open(f'{path}/data.json', 'r') as f:
            data = json.load(f)
    else:
        data={}
    return float(data[str(chat_id)]) if str(chat_id) in data else 1000

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        logging.info(r)
        processMessage(r['message'])
        return jsonify(r)
    return('<b>This Page Is Not For You :{</b>')

#boot
def main():
    logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    rget = rq.get(tgUrl('deleteWebhook'))
    rget = rq.get(tgUrl('setWebhook'), json={'url':f'https://nonezonyx.ru/bots/serving/randLocationBot'})
    from waitress import serve
    serve(app, host="localhost", port=48654)

if __name__ == '__main__':
    main()
