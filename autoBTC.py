#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from typing import NamedTuple
import os
import sys
import time
# import pyautogui
import subprocess
import json
import requests
from datetime import datetime
from random import random
from colored import stylize
import colored
from collections import namedtuple
from dataclasses import dataclass
from requests.sessions import session
# from tabulate import tabulate
import tabulate

tabulate.PRESERVE_WHITESPACE = True

from bs4 import BeautifulSoup, UnicodeDammit


class SavedData(NamedTuple):
    posRoll: tuple
    accounts: dict


Account = namedtuple(
    'Account', ['id', 'current_balance', 'current_rp_balance', 'logs'])
# Log = namedtuple('Log', ['timestamp', 'rp_balance', 'btc_balance', 'rp_gained', 'btc_gained'])


class Log(NamedTuple):
    timestamp: str
    rp_balance: int
    btc_balance: int
    rp_gained: int
    btc_gained: int

def coloredValue(value, format='{:+}'):
    if value > 0:
        return stylize(format.format(value), colored.fore.GREEN)
    elif value < 0:
        return stylize(format.format(value), colored.fore.RED)
    else:
        return format.format(value)

# class teste(NamedTuple):
#     value: int
#     log: Log


# l = Log(*[1, 2, 3, 4, 5])

# t = teste(1, l)

# print(t)
# print(dir(t))

payload = {

}

h = {
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    # "Accept": "text/html",
    # "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "__cfduid=df018db9b079168ae9361f82fec5bc2bb1620266270; btc_address=1CJ4vvSJefSpSb3v1k5xnxtEySBD1sBtGU; password=363acd1f069ecf92f61efb54be8072a1eeda3adab881cfc3577ca2661556ee06; have_account=1; login_auth=PcZ0ZH11rmArIQ152kKpwsjf; cookieconsent_dismissed=yes; last_play=1620437896; csrf_token=6i3P7X9eccgO",
    "Host": "freebitco.in",
    # "TE": "Trailers",
    # "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
}


c = {
    "__cfduid": "df018db9b079168ae9361f82fec5bc2bb1620266270",
    "btc_address": "1CJ4vvSJefSpSb3v1k5xnxtEySBD1sBtGU",
    "cookieconsent_dismissed": "yes",
    "csrf_token": "kzV6O2m3xrwu",
    "have_account": "1",
    # "last_play": "1620437896",
    "login_auth": "PcZ0ZH11rmArIQ152kKpwsjf",
    "password": "363acd1f069ecf92f61efb54be8072a1eeda3adab881cfc3577ca2661556ee06"
}

h2={
    "Cookie": "__cfduid=d6d66739ea723b7e7b31e65579f1c23451620345821; have_account=1; login_auth=IpisF3uQjMNRglupS5YgxboO; cookieconsent_dismissed=yes; last_play=1621782731; csrf_token=2ijwVeB3kVxL; btc_address=19bJKkqJdhwKE11UJDkRkNkkvqDrXQArx; password=d87603930f1f4c00426a29ea75923bbf0819161134ac3bb2a82f6829af566fdd",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
}

def coloredValue(value, format='{:+}'):
    if value > 0:
        return stylize(format.format(value), colored.fore.GREEN)
    elif value < 0:
        return stylize(format.format(value), colored.fore.RED)
    else:
        return format.format(value)

def render(clear=False):
    if(clear):
        print('\033[11A')
    
    print(tabulate.tabulate([
        [tabulate.tabulate(user_info , tablefmt='presto')],
        [tabulate.tabulate(table, tablefmt='presto')],
        [output]], tablefmt='fancy_grid'))


# session = requests.Session()
# response = session.get('https://freebitco.in', headers=h2)

# f = open('page', 'w')
# f.write(response.text)
# f.close()
f = open('page')
text = f.read()
f.close()


btc_start = 0.00001489
rp_start = 4570
bonus_start = 33.52

btc_last = 0.00001500
rp_last = 4577
bonus_last = 30.23

soup = BeautifulSoup(text, 'html.parser')

btc_balance_str = soup.select_one('#balance_small').text
btc_balance = float(btc_balance_str)
satoshi_balance = int(btc_balance_str.replace('.', ''))
rp_balance = int(soup.select_one('.user_reward_points').text.replace(',', ''))
user_id = soup.select_one('span.left:nth-child(2)').text
promotion = soup.select_one('.free_play_bonus_box_span_large').text
bonus_percentage = float(soup.select_one('#fp_bonus_req_completed').text)

btc_session_change = btc_balance - btc_start
rp_session_change = rp_balance - rp_start
bonus_session_change = bonus_percentage - bonus_start

btc_last_change = btc_balance - btc_last
rp_last_change = rp_balance - rp_last
bonus_last_change = bonus_percentage - bonus_last



user_info =[['User', user_id]]

label = ['', 'BTC', 'RP', u'Bônus']
balance = ['Current balance', btc_balance_str, rp_balance, '{:.2f}'.format(bonus_percentage)]
session_change = ['Session change', coloredValue(btc_session_change, '{:+.8f}'), coloredValue(rp_session_change), coloredValue(bonus_session_change, '{:+.2f}%')]
last_change = ['Last change', coloredValue(btc_last_change, '{:+.8f}'), coloredValue(rp_last_change), coloredValue(bonus_last_change, '{:+.2f}%')]


table=[
    label,
    balance,
    session_change,
    last_change,
]

output = 'Game roll successful at 12:12:11, -2 satoshi and 18 RP earned'
output = ' '*50

render()
output = 'change'
output = output+(' '*(50-len(output)))
time.sleep(5)
render(True)

