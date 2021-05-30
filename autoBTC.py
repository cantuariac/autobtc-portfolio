#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Flag
from bs4 import BeautifulSoup, UnicodeDammit
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
import threading

tabulate.PRESERVE_WHITESPACE = True


class SavedData(NamedTuple):
    roll_position: tuple
    captcha_position: tuple
    accounts: dict


class User(NamedTuple):
    id: str = None
    email: str = None
    cookie: str = None
    total_rolls: int = 0


class Log(NamedTuple):
    timestamp: str
    rp_balance: int
    btc_balance: int
    rp_gained: int
    btc_gained: int
    bonus: float
    bonus_loss: float


cookie2 = "__cfduid=df018db9b079168ae9361f82fec5bc2bb1620266270; btc_address=1CJ4vvSJefSpSb3v1k5xnxtEySBD1sBtGU; password=363acd1f069ecf92f61efb54be8072a1eeda3adab881cfc3577ca2661556ee06; have_account=1; login_auth=PcZ0ZH11rmArIQ152kKpwsjf; cookieconsent_dismissed=yes; last_play=1620437896; csrf_token=6i3P7X9eccgO"

cookie = "__cfduid=d6d66739ea723b7e7b31e65579f1c23451620345821; have_account=1; login_auth=IpisF3uQjMNRglupS5YgxboO; cookieconsent_dismissed=yes; last_play=1621782731; csrf_token=2ijwVeB3kVxL; btc_address=19bJKkqJdhwKE11UJDkRkNkkvqDrXQArx; password=d87603930f1f4c00426a29ea75923bbf0819161134ac3bb2a82f6829af566fdd"


def colorChange(value, base=0, format='{:+}'):
    if value > base:
        return stylize(format.format(value), colored.fore.GREEN)
    elif value < base:
        return stylize(format.format(value), colored.fore.RED)
    else:
        return format.format(value)


class autoBTC():

    label_row = ['', ' Current', '  Session', '    Last']

    def __init__(self, user: User):
        self.user = user

        self.updatePageData()
        self.btc_start = self.btc_last = self.btc_balance
        self.rp_start = self.rp_last = self.rp_balance
        self.bonus_start = self.bonus_last = self.bonus
        self.rolls = self.user.total_rolls

        if(not user.id):
            self.user = User(self.user_id, self.user_email, user.cookie, user.total_rolls)

        self.updateBTCprice()
        self.brl_rate_last = self.brl_rate
        self.usd_rate_last = self.usd_rate

    def updatePageData(self):

        session = requests.Session()
        response = session.get('https://freebitco.in', headers={
            "Cookie": self.user.cookie,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        })
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        self.user_id = soup.select_one('span.left:nth-child(2)').text
        self.user_email = soup.select_one('#edit_profile_form_email').attrs['value']

        btc_balance_str = soup.select_one('#balance_small').text
        self.btc_balance = float(btc_balance_str)
        self.satoshi_balance = int(btc_balance_str.replace('.', ''))
        self.rp_balance = int(soup.select_one(
            '.user_reward_points').text.replace(',', ''))
        self.bonus = float(soup.select_one('#fp_bonus_req_completed').text)

        self.promotion = soup.select_one(
            '.free_play_bonus_box_span_large').text

    def updateBTCprice(self):
        j = json.loads(requests.get(
            'https://api.coindesk.com/v1/bpi/currentprice/BRL.json').text)
        self.brl_rate = j['bpi']['BRL']['rate_float']
        self.usd_rate = j['bpi']['USD']['rate_float']

    def printScreen(self, output=None, clear=True):
        global outputList
        update_time = datetime.now()
        user_info_row = [[' User: ' + self.user.id,
                          'Updated: ' + datetime.now().strftime('%H:%M:%S %d-%m-%y')]]
        btc_info_row = [  # ['asd']]
            [f'BTC price: R$ {colorChange(self.brl_rate, self.brl_rate_last, "{:,.2f}")} $ {colorChange(self.usd_rate, self.usd_rate_last, "{:,.2f}")}']]

        btc_session_change = self.btc_balance - self.btc_start
        rp_session_change = self.rp_balance - self.rp_start
        bonus_session_change = self.bonus - self.bonus_start
        rolls_session = self.rolls - self.user.total_rolls

        btc_last_change = self.btc_balance - self.btc_last
        rp_last_change = self.rp_balance - self.rp_last
        bonus_last_change = self.bonus - self.bonus_last

        btc_row = ['BTC', '%.8f' % self.btc_balance, colorChange(
            btc_session_change, format='{:+.8f}'), colorChange(btc_last_change, format='{:+.8f}')]

        rp_row = ['RP', self.rp_balance, colorChange(
            rp_session_change), colorChange(rp_last_change)]

        bonus_row = ['Bônus%', '%.2f%%' % self.bonus, colorChange(
            bonus_session_change, format='{:+.2f}%'), colorChange(bonus_last_change, format='{:+.2f}%')]

        rolls_row = ['Rolls', self.rolls, colorChange(
            rolls_session, format='{:+d}')]

        info = [
            autoBTC.label_row,
            btc_row,
            rp_row,
            bonus_row,
            rolls_row,
        ]


        if(output):
            outputList = (
                outputList + [[output+(WS*(50-len(output)))]])[6-height:]

        s = tabulate.tabulate([
                [NAME],
                [tabulate.tabulate(btc_info_row, tablefmt='presto')],
                [tabulate.tabulate(user_info_row, tablefmt='presto')],
                [tabulate.tabulate(info, tablefmt='presto',
                                colalign=("right",))],
                [tabulate.tabulate(outputList,
                                tablefmt='plain')]],
                            tablefmt='fancy_grid')
        if(clear):
            print(f'\033[{height+8}A', end='')
        print(s)

    @staticmethod
    def printInitialScreen(output=None, clear=True):
        global outputList

        j = json.loads(requests.get(
            'https://api.coindesk.com/v1/bpi/currentprice/BRL.json').text)
        brl_rate = j['bpi']['BRL']['rate_float']
        usd_rate = j['bpi']['USD']['rate_float']

        if(output):
            outputList = (
                outputList + [[output+(WS*(50-len(output)))]])[-height:]

        s = tabulate.tabulate(
            [
                [NAME], [WS],
                [f'BTC price: R$ {brl_rate} $ {usd_rate}'],
                [tabulate.tabulate(outputList,
                                   tablefmt='plain')]
            ], tablefmt='fancy_grid')
        if(clear):
            print(f'\033[{height+8}A', end='')
        print(s)


def saveData():
    fd = open(DATA_FILE, 'w')
    json.dump(data._asdict(), fd)
    fd.close()


def loadData():
    global data
    fd = open(DATA_FILE)
    data = SavedData(**json.load(fd))
    fd.close()

NAME = stylize('autoBTC', [colored.fore.GREEN, colored.style.BOLD])
DATA_FILE = 'data.json'
data = SavedData((0, 0), (0, 0), {})
width = 50
height = 10
WS = '⠀'
outputList = [[WS*width]]*height


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='autoBTC.py',
        description="""Script to automate rolls for FreeBitco.in """)

    subparser = parser.add_subparsers(title="commands")

    class action:
        CONFIG = 1
        RUN = 2
        REPORT = 3

    config_parser = subparser.add_parser('config',
                                         help="Set click positions for CAPTCHA checkbox and ROLL button")
    config_parser.add_argument(
        'action', action='store_const', const=action.CONFIG)

    run_parser = subparser.add_parser('run',
                                      help="Run script with current configurations")
    run_parser.add_argument('action', action='store_const', const=action.RUN)

    report_parser = subparser.add_parser('report',
                                         help="Show a report from saved data")
    report_parser.add_argument(
        'action', action='store_const', const=action.REPORT)
    if len(sys.argv) == 1:
        parser.print_usage(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    autoBTC.printInitialScreen(clear=False)
    
    if(os.path.isfile(DATA_FILE)):
        loadData()
        autoBTC.printInitialScreen(f'\'{DATA_FILE}\' file loaded')

    else:
        autoBTC.printInitialScreen('Saved data file not found')
        captcha_position = None
        roll_position = None
        load_time = 10
        logs = {}
        saveData()
        autoBTC.printInitialScreen(f'\'{DATA_FILE}\' file created')
    u = User(cookie=cookie)
    # print(u)
    btc = autoBTC(u)
    btc.printScreen('waiting 10 seconds')
    # time.sleep(10)
    # btc.updatePageData()
    # btc.updateBTCprice()
    # btc.printScreen('update again')
    print(btc.user)
