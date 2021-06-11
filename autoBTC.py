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


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Log):
            return
        return super().default(obj)

class ExitException(Exception):
    pass

def saveData():
    global settings, accounts
    # accounts = [acc._asdict() for acc in accounts]
    # settings = {res:(settings[res]._asdict()) for res in settings}

    fd = open(DATA_FILE, 'w')
    json.dump({
        'settings': settings,
        'accounts': accounts,
    }, fd, indent=2)
    fd.close()

def loadData():
    global settings, accounts
    fd = open(DATA_FILE)
    settings, accounts = json.load(fd).values()
    accounts = [Account(*acc) for acc in accounts]
    settings = {
        res:Setting(tuple(settings[res]['roll_position']), tuple(settings[res]['captcha_position']))
         for res in settings }
    fd.close()

def saveLogs():
    global logs
    s = json.dumps(logs, indent=2)
    s = s.replace('\n      ', ' ')
    s = s.replace('\n    ],', ' ],')
    s = s.replace('\n    ]', ' ]')
    fd = open(LOGS_FILE, 'w')
    fd.write(s)
    fd.close()

def loadLogs():
    global logs
    fd = open(LOGS_FILE)
    logs = json.load(fd)
    for id in logs:
        logs[id] = [Log(*log) for log in logs[id]]
    fd.close()


accounts = {}
settings = {}
DATA_FILE = 'data.json'
logs = {}
LOGS_FILE = 'logs.json'


class action:
    CONFIG = 'config'
    RUN = 'run'
    REPORT = 'report'
    USERS = 'users'
    TEST = 'test'
    AUTO = 'auto'
    MANUAL = 'manual'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='autoBTC.py',
        description="""Script to automate rolls for FreeBitco.in """)

    command_parser = parser.add_subparsers(
        title="command", help='action to perform')

    config = command_parser.add_parser(
        'config',
        help="Set click positions for CAPTCHA checkbox and ROLL button")
    config.add_argument(
        'action', action='store_const', const=action.CONFIG)
    config.add_argument('-l', '--list', action='store_true',
                     help='List saved settings')

    run = command_parser.add_parser(
        'run',
        help="Run script with current configurations")
    run.add_argument('action', action='store_const', const=action.RUN)
    run.add_argument('-i', '--user-index', action='store', type=int, default=1,
                     help='Select user by index')

    mode_run = run.add_subparsers(title='mode')
    mode_run.add_parser('auto', help='Fully automated').add_argument(
        'mode', action='store_const', const=action.AUTO)
    mode_run.add_parser('manual', help='Semi automated, user clicks capachas and buttons').add_argument(
        'mode', action='store_const', const=action.MANUAL)

    users = command_parser.add_parser(
        'users',
        help="List saved users")
    users.add_argument(
        'action', action='store_const', const=action.USERS)
    users.add_argument('-c', '--create-user', action='store', type=str, dest='cookie',
                       help='Create user from cookie string')

    report = command_parser.add_parser('report',
                                       help="Show a report from saved data")
    report.add_argument(
        'action', action='store_const', const=action.REPORT)

    test = command_parser.add_parser('test',
                                     help="test script")
    test.add_argument(
        'action', action='store_const', const=action.TEST)

    args = parser.parse_args()
    # print(args); exit()
    btc = btcCrawler()
    resolution = subprocess.getoutput('xrandr | grep current').split(',')[1][9:]

    btc.printScreen(clear=False)

    # print(args)

    if(os.path.isfile(DATA_FILE)):
        loadData()
        btc.printScreen(f'Data file loaded')
    else:
        btc.printScreen('Saved data file not found')
        saveData()
        btc.printScreen(f'Data file created')

    if(os.path.isfile(LOGS_FILE)):
        loadLogs()
        btc.printScreen(f'Logs file loaded')
    else:
        btc.printScreen('Logs file not found')
        saveLogs()
        btc.printScreen(f'Logs file created')

    if(not hasattr(args, 'action')):
        btc.printScreen("Starting with default command 'run'")
        args.action = action.RUN
    try:
        if args.action == action.RUN:
            if(not settings):
                btc.printScreen(
                    stylize('Click positions not configured', colored.fore.RED))
                raise ExitException
            
            if(not resolution in settings):
                btc.printScreen(
                    stylize('Click positions not configured for resolution '+resolution, colored.fore.RED))
                raise ExitException
            
            if(not accounts):
                btc.printScreen(
                    stylize('No accounts saved', colored.fore.RED))
                raise ExitException
            
            btc.setting = settings[resolution]
            # print(accounts[args.user_index-1])
            btc.setAccount(accounts[args.user_index-1])

            if(not hasattr(args, 'mode')):
                args.mode = action.AUTO
            
            btc.printScreen(
                f"Running on {args.mode} mode, {resolution} resolution for user {btc.account.email}")
            # btc.printScreen("User(id={id}, email={email}, total_rolls={total_rolls} loaded".format(**btc.user._asdict()))
            # btc.printScreen(f'{btc.user} loaded')

            errors = 0
            while(True):
                btc.updatePageData(fetch_rates=True)
                btc.wait(btcCrawler.checkRollTime(),
                         'for next roll')

                btc.updatePageData(fetch_rates=True)
                log = btc.logChange()
                if (log):
                    if btc.account.id in logs:
                        logs[btc.account.id].append(log)
                    else:
                        logs[btc.account.id] = [log]
                    saveLogs()
                    btc.printScreen('Unknown change logged')

                game, log = btc.rollSequence(args.mode)
                if(game):
                    if (log):
                        accounts[args.user_index - 1] = btc.increaseAccountRoll()
                        if btc.account.id in logs:
                            logs[btc.account.id].append(log)
                        else:
                            logs[btc.account.id] = [log]
                        saveData()
                        saveLogs()
                        btc.printScreen('Roll logged')
                        errors = 0
                    else:
                        btc.printScreen('Game not ready')
                    # print()
                else:
                    errors += 1
                    btc.printScreen('Reloading page and trying again')

                if(errors > 10):
                    btc.printScreen(stylize(
                        'Ending script, failed too many times', colored.fore.RED))
                    raise ExitException

        elif args.action == action.CONFIG:
            if(args.list):
                if settings:
                    btc.printScreen("Saved user settings:")
                    for res, sett in settings.items():
                        btc.printScreen(f"({res}) - {sett}")
                else:
                    btc.printScreen("No settings saved")
                raise ExitException
            
            btc.printScreen(f'Setting click positions for {resolution} resolution')
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
            
            settings[resolution] = Setting(roll_position, captcha_position)
            saveData()
            btc.printScreen('Settings saved')

        elif args.action == action.USERS:
            if(args.cookie):
                btc.setAccount(Account(cookie=args.cookie))
                accounts.append(btc.account)
                saveData()
                btc.printScreen(f"{btc.account} created")
            if accounts:
                btc.printScreen("Saved user accounts:")
                for idx, user in enumerate(accounts):
                    btc.printScreen(f"{idx+1} - {user}")
            else:
                btc.printScreen("No user accounts saved")

        elif args.action == action.REPORT:
            for u in logs:
                for log in logs[u]:
                    print(log)
        elif args.action == action.TEST:
            btc.printScreen('Running test sequence')
            print(accounts[1])
            print(type(accounts[1]))
            # logs['2'] = [Log(datetime.now().isoformat(),
            #                  0.00005643, random(), 34, 4, 0.5, 0.05)]
            # time.sleep(random())
            # logs['2'].append(Log(datetime.now().isoformat(),
            #                      0.00005643, random(), 34, 4, 0.5, 0.05))
            # s = json.dumps(logs, indent=2)
            # s = s.replace('\n      ', ' ')
            # s = s.replace('\n    ],', ' ],')
            # s = s.replace('\n    ]', ' ]')
            # print(s)
            # saveLogs()
    except ExitException as e:
        btc.printScreen(f'Script ended {e}')
    except KeyboardInterrupt:
        btc.printScreen('Script ended by user!')
