#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Flag
from bs4 import BeautifulSoup, UnicodeDammit
import argparse
from typing import NamedTuple
import os
import sys
import time
import pyautogui
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
    brl_rate = None
    usd_rate = None
    brl_rate_last = None
    usd_rate_last = None

    def __init__(self, user: User):
        self.user = user

        self.updatePageData()
        self.btc_start = self.btc_last = self.btc_balance
        self.rp_start = self.rp_last = self.rp_balance
        self.bonus_start = self.bonus_last = self.bonus
        self.rolls = self.user.total_rolls

        if(not user.id):
            self.user = User(self.user_id, self.user_email,
                             user.cookie, user.total_rolls)

        self.updateBTCprice()
        autoBTC.brl_rate_last = autoBTC.brl_rate
        autoBTC.usd_rate_last = autoBTC.usd_rate

    def updatePageData(self):

        session = requests.Session()
        response = session.get('https://freebitco.in', headers={
            "Cookie": self.user.cookie,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        })
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        self.user_id = soup.select_one('span.left:nth-child(2)').text
        self.user_email = soup.select_one(
            '#edit_profile_form_email').attrs['value']

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
        autoBTC.brl_rate = j['bpi']['BRL']['rate_float']
        autoBTC.usd_rate = j['bpi']['USD']['rate_float']

    def printScreen(self, output=None, clear=True):
        global outputList
        update_time = datetime.now()
        user_info_row = [[' User: ' + self.user.id,
                          'Updated: ' + datetime.now().strftime('%H:%M:%S %d-%m-%y')]]
        btc_info_row = [  # ['asd']]
            [f'BTC price: R$ {colorChange(autoBTC.brl_rate, autoBTC.brl_rate_last, "{:,.2f}")} $ {colorChange(autoBTC.usd_rate, autoBTC.usd_rate_last, "{:,.2f}")}']]

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
                outputList + [[output]])[6-height:]  # +(WS*(50-len(output)))

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
    def printScreenStatic(output=None, clear=True, overhide=False, fetch_rates=False):
        global outputList

        if(fetch_rates):
            j = json.loads(requests.get(
                'https://api.coindesk.com/v1/bpi/currentprice/BRL.json').text)
            autoBTC.brl_rate = j['bpi']['BRL']['rate_float']
            autoBTC.usd_rate = j['bpi']['USD']['rate_float']

        if(output):
            if(overhide):
                outputList[-1] = [output]
            else:
                outputList = (
                    outputList + [[output]])[-height:]  # +(WS*(50-len(output)))

        s = tabulate.tabulate(
            [
                [NAME], [WS],
                [f'BTC price: R$ {autoBTC.brl_rate} $ {autoBTC.usd_rate}'],
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


data = SavedData(None, None, None)
width = 80
height = 15
WS = '⠀'
NAME = WS*((width-7)//2)+stylize('autoBTC',
                                 [colored.fore.GREEN, colored.style.BOLD])+WS*((width-7)//2)
DATA_FILE = 'data.json'
outputList = [[WS*width]]*height
load_time = 10

class action:
    CONFIG = 'config'
    RUN = 'run'
    REPORT = 'report'
    AUTO = 'auto'
    MANUAL = 'manual'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='autoBTC.py',
        description="""Script to automate rolls for FreeBitco.in """)

    command_parser = parser.add_subparsers(title="command", help='action to perform')

    config = command_parser.add_parser('config',
                                       help="Set click positions for CAPTCHA checkbox and ROLL button")
    config.add_argument(
        'action', action='store_const', const=action.CONFIG)

    run = command_parser.add_parser('run',
                                    help="Run script with current configurations")
    run.add_argument('action', action='store_const', const=action.RUN)
    mode_parcer = run.add_subparsers(title='mode')
    mode_parcer.add_parser('auto', help='Fully automated').add_argument(
        'mode', action='store_const', const=action.AUTO)
    mode_parcer.add_parser('manual', help='Semi automated, user clicks capachas and buttons').add_argument(
        'mode', action='store_const', const=action.MANUAL)

    report_parser = command_parser.add_parser('report',
                                              help="Show a report from saved data")
    report_parser.add_argument(
        'action', action='store_const', const=action.REPORT)
    # if len(sys.argv) == 1:
    #     parser.print_usage(sys.stderr)
    #     sys.exit(1)
    args = parser.parse_args()
    if(not hasattr(args, 'action')):
        args.action = action.RUN
    print(args)

    autoBTC.printScreenStatic(clear=False, fetch_rates=True)

    if(os.path.isfile(DATA_FILE)):
        loadData()
        autoBTC.printScreenStatic(f'\'{DATA_FILE}\' file loaded')

    else:
        autoBTC.printScreenStatic('Saved data file not found')
        captcha_position = None
        roll_position = None
        load_time = 10
        logs = {}
        saveData()
        autoBTC.printScreenStatic(f'\'{DATA_FILE}\' file created')
    # u = User(cookie=cookie)
    # print(u)
    # btc = autoBTC(u)
    # btc.printScreen('waiting 10 seconds')
    # time.sleep(10)
    # btc.updatePageData()
    # btc.updateBTCprice()
    # btc.printScreen('update again')
    # print(btc.user)
    try:
        if args.action==action.RUN:
            if(not hasattr(args, 'mode')):
                args.mode = action.AUTO
            

        
        elif args.action==action.CONFIG:
            autoBTC.printScreenStatic('Setting click positions')
            autoBTC.printScreenStatic(WS)

            for i in range(load_time*10, 0, -1):
                current = pyautogui.position()
                autoBTC.printScreenStatic('Mouse over CAPTCHA checkbox position and wait %.1f seconds (%d, %d)'
                    %(i/10, current.x, current.y), overhide=True)
                time.sleep(0.1)
            captcha_position = pyautogui.position()
            autoBTC.printScreenStatic('CAPTCHA position set at (%d, %d)'%captcha_position, overhide=True)
            autoBTC.printScreenStatic(WS)
            
            for i in range(load_time*10, 0, -1):
                current = pyautogui.position()
                autoBTC.printScreenStatic('Mouse over ROLL button position and wait %.1f seconds (%d, %d)'
                    %(i/10, current.x, current.y), overhide=True)
                time.sleep(0.1)
            roll_position = pyautogui.position()
            autoBTC.printScreenStatic('ROLL position set at (%d, %d)'%roll_position, ' '*20, overhide=True)

            data = SavedData(roll_position, captcha_position, data.accounts)
            saveData()
            autoBTC.printScreenStatic('Settings saved')
        elif args.action==action.REPORT:
            pass
        
    except KeyboardInterrupt:
        autoBTC.printScreenStatic('\nScript ended by user!')
