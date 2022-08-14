#!/usr/bin/env python

import logging
from  os import environ
from flask import Flask, request, jsonify
import requests as rq
import pathlib
import json
from randomcoordinatesinradius import random_coordinates
import asyncio
import sqlite3

#variables
WEBHOOK_URL=""
WBHOOK_PORT=

path = pathlib.Path(__file__).parent.resolve()
token_env='token_randLocBot'
if token_env in environ:
    token=str(environ[token_env])
else: exit('token is None')
tgUrl = lambda method: f"https://api.telegram.org/bot{token}/{method}"
app = Flask(__name__)
WEBHOOK_URL=""

#database
db = sqlite3.connect('randLocBot.db')
cursor = db.cursor()



async def processMessage(message):
    if 'location' in message:
        cursor.execute(f"SELECT distance FROM user_data WHERE id = {message['chat']['id']}")
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO user_data VALUES (?, ?)", (message['chat']['id'], 1000))
            db.commit()
            distance = 1000
        else:
            distance = cursor.fetchone()
        longitude, latitude = random_coordinates([message['location']['longitude'], message['location']['latitude']], distance)
        answer={'chat_id':message['chat']['id'], 'latitude':latitude, 'longitude':longitude}
        rpost = rq.post(tgUrl('sendLocation'), json=answer)
    if 'text' in message:
        try:
            distance = int(message['text'])
            cursor.execute(f"SELECT distance FROM user_data WHERE id = {message['chat']['id']}")
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO user_data VALUES (?, ?)", (message['chat']['id'], distance))
                db.commit()
            answer = {'chat_id':message['chat']['id'], 'text' : f"New distance is {distance}"}
            rpost = rq.post(tgUrl('sendMessage'), json=answer)
        except Exception as e:
            answer = {'chat_id':message['chat']['id'], 'text' : f"Send me integer to set distance"}
            rpost = rq.post(tgUrl('sendMessage'), json=answer)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        logging.debug('PostMethod')
        r = request.get_json()
        asyncio.run(processMessage(r['message']))
        return jsonify(r)
    return('<b>This Page Is Not For You :{</b>')

#boot
def main():
    logging.basicConfig(filename=f'{path}/bot.log', encoding='utf-8', level=logging.WARNING, format='%(asctime)s %(levelname)s: %(message)s')
    cursor.execute("CREATE TABLE IF NOT EXISTS user_data(id INT8, distance INT8)")
    db.commit()
    rget = rq.get(tgUrl('deleteWebhook'))
    rget = rq.get(tgUrl('setWebhook'), json={'url':f'https://{WEBHOOK_URL}'})
    from waitress import serve
    serve(app, host="localhost", port=WBHOOK_PORT)

if __name__ == '__main__':
    main()
