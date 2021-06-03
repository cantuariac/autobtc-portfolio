#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from typing import NamedTuple
import os
import sys
import time
import pyautogui
import json
from datetime import datetime
from random import random
from colored import stylize
import colored
# from tabulate import tabulate
import tabulate
import threading

from btcCrawler import *

tabulate.PRESERVE_WHITESPACE = True


cookie2 = "__cfduid=df018db9b079168ae9361f82fec5bc2bb1620266270; btc_address=1CJ4vvSJefSpSb3v1k5xnxtEySBD1sBtGU; password=363acd1f069ecf92f61efb54be8072a1eeda3adab881cfc3577ca2661556ee06; have_account=1; login_auth=PcZ0ZH11rmArIQ152kKpwsjf; cookieconsent_dismissed=yes; last_play=1622671419; fbtc_session=hDvF63BWOwt59Q8hsEeovVfk; fbtc_userid=25043400; free_play_sound=1; csrf_token=nMyrr5NbZnfn"

cookie = "__cfduid=d6d66739ea723b7e7b31e65579f1c23451620345821; have_account=1; login_auth=IpisF3uQjMNRglupS5YgxboO; cookieconsent_dismissed=yes; last_play=1621782731; csrf_token=2ijwVeB3kVxL; btc_address=19bJKkqJdhwKE11UJDkRkNkkvqDrXQArx; password=d87603930f1f4c00426a29ea75923bbf0819161134ac3bb2a82f6829af566fdd"


def saveData(data):
    # global data
    # data = SavedData(roll_position, captcha_position, data.accounts)
    fd = open(DATA_FILE, 'w')
    json.dump(data._asdict(), fd)
    fd.close()


def loadData():
    global data
    fd = open(DATA_FILE)
    roll, captcha, accounts = json.load(fd).values()
    data = SavedData(tuple(roll), tuple(captcha), accounts)
    fd.close()


data = SavedData(None, None, None)
DATA_FILE = 'data.json'


class action:
    CONFIG = 'config'
    RUN = 'run'
    REPORT = 'report'
    TEST = 'test'
    AUTO = 'auto'
    MANUAL = 'manual'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='autoBTC.py',
        description="""Script to automate rolls for FreeBitco.in """)

    command_parser = parser.add_subparsers(
        title="command", help='action to perform')

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

    test_parser = command_parser.add_parser('test',
                                            help="test script")
    test_parser.add_argument(
        'action', action='store_const', const=action.TEST)

    args = parser.parse_args()
    btc = btcCrawler()

    btc.printScreen(clear=False, fetch_rates=True)

    if(not hasattr(args, 'action')):
        btc.printScreen("Starting with default command 'run'")
        args.action = action.RUN
    # print(args)

    if(os.path.isfile(DATA_FILE)):
        loadData()
        btc.printScreen(f'Data file loaded')

    else:
        btc.printScreen('Saved data file not found')
        saveData()
        btc.printScreen(f'Data file created')

    btcCrawler.data = data

    try:
        if args.action == action.RUN:
            if(not hasattr(args, 'mode')):
                args.mode = action.AUTO

            btc.setUser(User(cookie=cookie2))
            btc.printScreen("btc rates updated", fetch_rates=True)

            while(True):
                btc.wait(btcCrawler.checkRollTime(),
                                'for next roll')
                btc.updatePageData()
                game = btc.rollSequence(args.mode)
                if(game):
                    roll_timestamp = datetime.now()
                    btc.updatePageData()
                    btc.printScreen(stylize(
                        'Game roll successful at ' + roll_timestamp.strftime('%H:%M:%S')), colored.fore.GREEN)
                    btc.printScreen(btc.logChange(roll_timestamp))

                    # print()
                else:
                    btc.printScreen(
                        stylize('Game roll failed', colored.fore.RED))
                    btc.printScreen('Reloading page and trying again')

        elif args.action == action.CONFIG:
            btc.printScreen('Setting click positions')
            btc.printScreen(WS)

            for i in range(LOAD_TIME*10, 0, -1):
                current = pyautogui.position()
                btc.printScreen('Mouse over CAPTCHA checkbox position and wait %.1f seconds (%d, %d)'
                                % (i/10, current.x, current.y), overhide=True)
                time.sleep(0.1)
            captcha_position = pyautogui.position()
            btc.printScreen('CAPTCHA position set at (%d, %d)' %
                            captcha_position, overhide=True)
            btc.printScreen(WS)

            for i in range(LOAD_TIME*10, 0, -1):
                current = pyautogui.position()
                btc.printScreen('Mouse over ROLL button position and wait %.1f seconds (%d, %d)'
                                % (i/10, current.x, current.y), overhide=True)
                time.sleep(0.1)
            roll_position = pyautogui.position()
            btc.printScreen('ROLL position set at (%d, %d)' %
                            roll_position, ' '*20, overhide=True)

            saveData(SavedData(roll_position, captcha_position, data.accounts))
            btc.printScreen('Settings saved')
        elif args.action == action.REPORT:
            pass
        elif args.action == action.TEST:
            # btc.printScreen(fetch_rates=True)
            btc.setUser(User(cookie=cookie))
            btc.printScreen("btc rates updated", fetch_rates=True)
            # btc.wait(200, 'for teste')
            # btc.printScreen("btc rates updated", fetch_rates=True)
            btc.printScreen(f'roll time: {btcCrawler.checkRollTime()}')
            # btc.focusOrOpenPage()

    except KeyboardInterrupt:
        btc.printScreen('\nScript ended by user!')
