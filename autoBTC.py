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

from mytypes import *
from logger import *
from btcCrawler import *

tabulate.PRESERVE_WHITESPACE = True


def userInput():
    global command
    while True:
        command = input('> ')
        if(command == 'q'):
            break


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Account):
            return obj.__dict__
        return json.JSONEncoder.default(obj)


class ExitException(Exception):
    pass


def saveData():
    global settings, accounts
    # accounts = [acc._asdict() for acc in accounts]
    # settings = {res:(settings[res]._asdict()) for res in settings}

    fd = open(DATA_FILE, 'w')
    json.dump({
        'settings': [s._asdict() for s in settings],
        'accounts': [acc.__dict__ for acc in accounts],
    }, fd, indent=2)
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


def loadData():
    global settings, accounts
    fd = open(DATA_FILE)
    settings, accounts = json.load(fd).values()
    accounts = [Account(**acc) for acc in accounts]
    settings = [Setting(sett['resolution'], tuple(sett['roll_position']), tuple(sett['captcha_position'])) for sett in settings]
    fd.close()


def loadLogs():
    global logs
    fd = open(LOGS_FILE)
    logs = json.load(fd)
    for id in logs:
        logs[id] = [ChangeLog(*log) for log in logs[id]]
    fd.close()


accounts = {}
settings = {}
DATA_FILE = 'data2.json'
logs = {}
LOGS_FILE = 'logs2.json'

command = None


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
    # btc = BTCBot()
    resolution = subprocess.getoutput(
        'xrandr | grep current').split(',')[1][9:]

    printScreen(clear=False)

    # print(args)

    if(os.path.isfile(DATA_FILE)):
        loadData()
        printScreen(f'Data file loaded')
    else:
        printScreen('Saved data file not found')
        saveData()
        printScreen(f'Data file created')

    if(os.path.isfile(LOGS_FILE)):
        loadLogs()
        printScreen(f'Logs file loaded')
    else:
        printScreen('Logs file not found')
        saveLogs()
        printScreen(f'Logs file created')

    if(not hasattr(args, 'action')):
        printScreen("Starting with default command 'run'")
        args.action = action.RUN
    try:
        if args.action == action.RUN:
            if(not settings):
                printScreen(
                    stylize('Click positions not configured', colored.fore.RED))
                raise ExitException
            
            setting = next(
                (s for s in settings if s.resolution == resolution), None)
            if(not setting):
                printScreen(
                    stylize('Click positions not configured for resolution '+resolution, colored.fore.RED))
                raise ExitException

            if(not accounts):
                printScreen(
                    stylize('No accounts saved', colored.fore.RED))
                raise ExitException

            # btc.setting = settings[resolution]
            acc = accounts[args.user_index-1]
            # print(accounts[args.user_index-1])
            if not acc.id in logs:
                logs[acc.id] = [
                    State(datetime.today().isoformat(), 0.0, 0, 1.0)]
            logger = Logger(acc, logs[acc.id])
            btcbot = BTCBot(acc, logger, setting)
            # btc.setAccount(accounts[args.user_index-1])

            if(not hasattr(args, 'mode')):
                args.mode = action.AUTO

            printScreen(
                f"Running on {args.mode} mode, {resolution} resolution for user {btcbot.account.email}")
            # printScreen("User(id={id}, email={email}, total_rolls={total_rolls} loaded".format(**btc.user._asdict()))
            # printScreen(f'{btc.user} loaded')

            consecutive_errors = 0
            while(True):
                try:
                    btcbot.updatePageData()  # fetch_rates=True)
                    btcbot.wait(BTCBot.checkRollTime(),
                                'for next roll')

                    btcbot.updatePageData()  # fetch_rates=True)
                    if (logger.updateState(btcbot.current_state)):
                        saveLogs()
                        printScreen('Unknown change logged', btcbot)

                    log = btcbot.rollSequence(args.mode)
                except PageNotOpenException:
                    printScreen(
                        stylize('Page not opened', colored.fore.RED), btcbot)
                    printScreen('Waiting for user to open page', btcbot)
                    time.sleep(LOAD_TIME)
                    consecutive_errors += 1
                    printScreen('Reloading page and trying again', btcbot)
                except GameNotReady:
                    printScreen(
                        stylize('Game not ready', colored.fore.RED), btcbot)
                    consecutive_errors += 1
                except GameFailException:
                    printScreen(
                        stylize('Game roll failed', colored.fore.RED), btcbot)
                    consecutive_errors += 1
                    printScreen('Reloading page and trying again')
                except Exception as error:
                    printScreen(
                        stylize(f'Unknown error:{error}', colored.fore.RED), btcbot)
                    print(error.with_traceback())
                    raise ExitException
                else:
                    printScreen(stylize('Game roll successful at ' + datetime.fromisoformat(
                        btcbot.current_state.timestamp).strftime('%H:%M:%S'), colored.fore.GREEN), btcbot)

                    # accounts[args.user_index - 1] = btc.increaseAccountRoll()
                    btcbot.account.total_rolls += 1
                    # if btc.account.id in logs:
                    #     logs[btc.account.id].append(log)
                    # else:
                    #     logs[btc.account.id] = [log]
                    saveData()
                    saveLogs()
                    printScreen('Roll logged', btcbot)
                    consecutive_errors = 0

                if(consecutive_errors > 10):
                    printScreen(stylize(
                        'Ending script, failed too many times', colored.fore.RED), btcbot)
                    raise ExitException

        elif args.action == action.CONFIG:
            if(args.list):
                if settings:
                    printScreen("Saved user settings:")
                    for sett in settings:
                        printScreen(f"{sett}")
                else:
                    printScreen("No settings saved")
                raise ExitException

            printScreen(
                f'Setting click positions for {resolution} resolution')
            printScreen(WS)

            for i in range(LOAD_TIME*10, 0, -1):
                current = pyautogui.position()
                printScreen('Mouse over CAPTCHA checkbox position and wait %.1f seconds (%d, %d)'
                            % (i/10, current.x, current.y), overhide=True)
                time.sleep(0.1)
            captcha_position = pyautogui.position()
            printScreen('CAPTCHA position set at (%d, %d)' %
                        captcha_position, overhide=True)
            printScreen(WS)

            for i in range(LOAD_TIME*10, 0, -1):
                current = pyautogui.position()
                printScreen('Mouse over ROLL button position and wait %.1f seconds (%d, %d)'
                            % (i/10, current.x, current.y), overhide=True)
                time.sleep(0.1)
            roll_position = pyautogui.position()
            printScreen('ROLL position set at (%d, %d)' %
                        roll_position, overhide=True)

            sett_i = next((i for i, s in enumerate(settings)
                           if s.resolution == resolution), None)
            if(sett_i):
                settings[sett_i] = Setting(
                    resolution, roll_position, captcha_position)
            else:
                settings.append(
                    Setting(resolution, roll_position, captcha_position))
            saveData()
            printScreen('Settings saved')

        elif args.action == action.USERS:
            if(args.cookie):
                # btc.setAccount(Account(cookie=args.cookie))
                # btcbot = BTCBot()
                acc = Account(cookie=args.cookie)
                accounts.append(acc)
                saveData()
                printScreen(f"{acc} created")
            if accounts:
                printScreen("Saved user accounts:")
                for idx, user in enumerate(accounts):
                    printScreen(f"{idx+1} - {user}")
            else:
                printScreen("No user accounts saved")

        elif args.action == action.REPORT:
            for u in logs:
                for log in logs[u][-5:]:
                    print(log)
        elif args.action == action.TEST:
            printScreen('Running test sequence')

            # fd = open('data.json')
            # settings2, accounts2 = json.load(fd).values()
            # accounts2 = [Account(**acc) for acc in accounts2]
            # settings2 = [Setting(res, tuple(settings2[res]['roll_position']), tuple(settings2[res]['captcha_position']))
            #              for res in settings2]
            # fd.close()
            for s in settings:
                print(s)
            for a in accounts:
                print(a)
            saveData()
            # print(next(s for s in settings2 if s.resolution == 'as', ))
            # print(json.dumps(settings, indent=1))
            # print(json.dumps(accounts2, indent=1, cls=CustomEncoder))

            # fd = open('logs.json')
            # logs2 = json.load(fd)
            # for id in logs2:
            #     for log in logs2[id]:
            #         logs[id].append(ChangeLog(log[0], log[1], log[3], log[5], log[2], log[4], log[6]))
            # fd.close()
            # saveLogs()

    except ExitException as e:
        printScreen(f'Script ended {e}')
    except KeyboardInterrupt:
        printScreen('Script ended by user!')
