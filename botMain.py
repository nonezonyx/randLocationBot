#!/usr/bin/env python
import logging #logs
import os
from flask import Flask, request, jsonify
import requests as rq
import pathlib
import json
from randomcoordinatesinradius import random_coordinates
import aiohttp
import asyncio

#variables
path = pathlib.Path(__file__).parent.resolve()
token=str(os.environ.get("token_randLocBot"))
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
    return('<h1>Hello bot</h1>')



#boot
def main():
    print(tgUrl(''))
    logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    rpost = rq.get(tgUrl('deleteWebhook'))
    with open(f'{path}/remove.json', 'w') as f:
        json.dump(rpost.json(), f, ensure_ascii=False, indent=4 )
    rpost = rq.get(tgUrl('setWebhook'), json={'url':'https://8d60-164-215-54-40.eu.ngrok.io'})
    with open(f'{path}/set.json', 'w') as f:
        json.dump(rpost.json(), f, ensure_ascii=False, indent=4 )
    if token == 'None':
        logging.critical('token is None')
        exit('Token is not selected')
    logging.info(f'file path = {path}')
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)

if __name__ == '__main__':
    main()
