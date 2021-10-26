#!/bin/python

import requests
import json
import argparse
from pycoingecko import CoinGeckoAPI
from bs4 import BeautifulSoup

from flask import Flask
from flask_apscheduler import APScheduler
from flask import request


class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)

scheduler = APScheduler()
cg = CoinGeckoAPI()

btx = 0

MAX_REQUEST = 50

banned_coin = []
coin_objs = {}

class Coin():

    def __init__(self, name, rate=0):
        self._rate = rate
        self.name = name

    @property
    def rate(self):
        if self.name == 'bitcoin':
            return "{:.2f}".format(float(self._rate)).replace('.00', '')
        if self.name == 'ncr' or self.name == 'dogecoin' or self.name == 'cardano':
            return "{:.4f}".format(float(self._rate))
        return self._rate

    @rate.setter
    def rate(self, value):
        self._rate = value

def coins_update(name):
    global coin_objs
    coin = coin_objs[name]
    if name in banned_coin:
        scheduler.remove_job(name)
        return
    if name == 'ncr':
        url = 'https://www.neosvr-api.com/api/globalvars/NCR_CONVERSION'
        data = requests.get(url)
        if data:
            try:
                data_json = data.json()
                if 'value' in data_json:
                    coin.rate = data_json['value']
            except json.JSONDecodeError:
                pass
    else:
        rate = cg.get_price(ids=coin.name, vs_currencies='usd')
        if rate:
            coin.rate = rate[coin.name]['usd']
        else:
            banned_coin.append(name)

def get_interval(nb_jobs):
    request_available = MAX_REQUEST / nb_jobs
    seconds_interval = (60 / request_available) + 1
    return seconds_interval

@app.route('/price')
def price():
    coins = request.args.get('coins')
    if not coins:
        return ''
    if ',' in coins:
        coins = request.args.get('coins').split(',')
    global coin_objs
    for coin in coins:
        if coin in banned_coin:
            continue
        if coin not in coin_objs:
            if len(coin_objs) == 0:
                seconds_interval = get_interval(1)
            else:
                seconds_interval = get_interval(len(coin_objs))
            seconds_interval += 1
            scheduler.add_job(func=coins_update, trigger='interval', id=coin, seconds=seconds_interval,  max_instances=20, args=[coin])
            coin_objs[coin] = Coin(coin)
    if len(coin_objs) > MAX_REQUEST:
        seconds_interval = get_interval(len(coin_objs))
        for job in scheduler.get_jobs():
            seconds_interval += 1
            job.reschedule(trigger='interval', seconds=seconds_interval)
    data = ''
    for coin in coins:
        if coin in coin_objs:
            coin = coin_objs[coin]
            data += str(coin.rate) + ','

    return data.rstrip(',')

@app.route('/')
def home():
    html = """
    <p>A simple api to make parsing easier on NeosVR of cryptocurrencies values.</p>
    <p>Check the source code: <a href='https://github.com/brodokk/coins2txt'>https://github.com/brodokk/coins2txt</a></p>
    """
    return html
if __name__ == '__main__':

    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)
