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

@scheduler.task('interval', id='do_job_1', seconds=5, max_instances=20)
def coins_update():
    global coin_objs
    for name, coin in coin_objs.items():
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

@app.route('/price')
def price():
    coins = request.args.get('coins')
    if coins:
        coins = request.args.get('coins').split(',')
    global coin_objs
    update_needed = False
    for coin in coins:
        if coin not in coin_objs:
            update_needed = True
            coin_objs[coin] = Coin(coin)
    if update_needed:
        scheduler.run_job('do_job_1')
    data = ''
    for coin in coins:
        if coin in coin_objs:
            coin = coin_objs[coin]
            data += str(coin.rate) + ','

    return data.rstrip(',')

if __name__ == '__main__':

    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)
