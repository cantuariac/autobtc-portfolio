#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from typing import NamedTuple
import os
import sys
import time
from matplotlib.pyplot import plot
from numpy import fromstring
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
    settings = [Setting(sett['resolution'], tuple(sett['roll_position']), tuple(
        sett['captcha_position'])) for sett in settings]
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
DATA_FILE = 'data.json'
logs = {}
LOGS_FILE = 'logs.json'

command = None


class action:
    CONFIG = 'config'
    RUN = 'run'
    REPORT = 'report'
    USERS = 'users'
    TEST = 'test'
    AUTO = 'auto'
    MANUAL = 'manual'
    CSV = 'csv'
    PLOTB = 'plotb'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='autoBTC.py',
        description="""Script to automate rolls for FreeBitco.in """)

    command_parser = parser.add_subparsers(
        title="command")  # , help='action to perform')

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
    parser.add_argument('-i', '--user-index', action='store', type=int, default=1,
                        help='Select user by index')
    parser.add_argument('-b', '--bonus-stop', action='store_true',
                        help='Script waits for user input if there is no bonus active for the account')

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
    # report.add_argument('-i', '--user-index', action='store', type=int, default=1,
    #                  help='Select user by index')

    type_report = report.add_subparsers(title='type')
    type_report.add_parser('csv').add_argument(
        'type', action='store_const', const='csv')
    type_report.add_parser(action.PLOTB).add_argument(
        'type', action='store_const', const=action.PLOTB)

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
        # args.user_index = 1
    printScreen(str(args))
    tags = []
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
            tags.append(setting.resolution)

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
            tags.append(args.mode)

            printScreen(
                f"Running on {args.mode} mode, {resolution} resolution for user {btcbot.account.email}")
            # printScreen("User(id={id}, email={email}, total_rolls={total_rolls} loaded".format(**btc.user._asdict()))
            # printScreen(f'{btc.user} loaded')

            btcbot.updatePageData()  # fetch_rates=True)
            if (logger.updateState(btcbot.current_state)):
                saveLogs()
                printScreen('Unknown change logged', btcbot, tags)

            consecutive_errors = 0
            while(True):
                try:

                    # tags2 = tags + [btcbot.active_rp_bonus] if btcbot.active_rp_bonus else []
                    tags2 = []

                    btcbot.wait(BTCBot.checkRollTime(),
                                'for next roll')
                    # if(btcbot.active_rp_bonus):
                    # tags2 = tags + [btcbot.active_rp_bonus] if btcbot.active_rp_bonus else []
                    # print(tags2, '\n')
                    btcbot.updatePageData()  # fetch_rates=True)
                    if (logger.updateState(btcbot.current_state)):
                        saveLogs()
                        printScreen('Unknown change logged', btcbot)

                    if(args.bonus_stop):
                        if(not btcbot.active_rp_bonus):

                            if(not btcbot.focusPage()):
                                raise PageNotOpenException
                            printScreen("Script paused", btcbot)
                            printScreen(
                                "No active bonus, press Enter to continue", btcbot)
                            input()
                            print('\033[1A', end='')

                    btcbot.rollSequence(args.mode)
                except PageNotOpenException:
                    printScreen(
                        stylize('Page not opened', colored.fore.RED), btcbot)
                    printScreen('Waiting for user to open page', btcbot)
                    time.sleep(LOAD_TIME)
                    consecutive_errors += 0.2
                    printScreen('Reloading page and trying again', btcbot)
                except GameNotReady:
                    printScreen(
                        stylize('Game not ready', colored.fore.RED), btcbot)
                    # consecutive_errors += 1
                except GameFailException:
                    printScreen(
                        stylize('Game roll failed', colored.fore.RED), btcbot)
                    consecutive_errors += 1
                    printScreen('Reloading page and trying again')
                except Exception as error:
                    printScreen(
                        stylize(f'Unknown error:{error}', colored.fore.RED), btcbot)
                    consecutive_errors += 1
                    printScreen('Reloading page and trying again')
                    # print(error.with_traceback())
                    # raise ExitException
                else:
                    printScreen(stylize('Game roll successful at ' + datetime.fromisoformat(
                        btcbot.current_state.timestamp).strftime('%H:%M:%S'), colored.fore.GREEN), btcbot)

                    logger.updateState(btcbot.current_state)
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
            if(sett_i != None):
                printScreen(f'Updating setting {settings[sett_i].resolution}')
                settings[sett_i] = Setting(
                    resolution, roll_position, captcha_position)
            else:
                printScreen(f'New setting {resolution}')
                settings.append(
                    Setting(resolution, roll_position, captcha_position))
            saveData()
            printScreen(f'Settings saved {resolution}')

        elif args.action == action.USERS:
            if(args.cookie):
                # btc.setAccount(Account(cookie=args.cookie))
                # btcbot = BTCBot()
                acc = Account(cookie=args.cookie)
                accounts.append(acc)
                if not acc.id in logs:
                    logs[acc.id] = [
                        State(datetime.today().isoformat(), 0.0, 0, 1.0)]
                saveData()
                saveLogs()
                printScreen(f"{acc} created")
            if accounts:
                printScreen("Saved user accounts:")
                for idx, user in enumerate(accounts):
                    printScreen(f"{idx+1} - {user}")
            else:
                printScreen("No user accounts saved")

        elif args.action == action.REPORT:

            # print(args)
            printScreen("Generating log report")
            setting = next(
                (s for s in settings if s.resolution == resolution), None)
            acc = accounts[args.user_index-1]
            # print(accounts[args.user_index-1])
            if not acc.id in logs:
                logs[acc.id] = [
                    State(datetime.today().isoformat(), 0.0, 0, 1.0)]
            if(args.type=='csv'):
                f = open(f'logs{acc.id}.csv', 'w')
                for log in logs[acc.id]:
                    f.write('%s, %.8f, %d, %.2f, %.8f, %d, %.2f\n'%log)
                printScreen(f"Report saved on \'logs{acc.id}.csv\'")
                f.close()
            if(args.type==action().PLOTB):
                import numpy as np
                import matplotlib.pyplot as plt
                timestamps = [datetime.fromisoformat(l[0]) for l in logs[acc.id]]
                values = [l[1] for l in logs[acc.id]]
                # print(data)
                plt.plot(timestamps, values)
                plt.gcf().autofmt_xdate()
                plt.show()
            else:
                logger = Logger(acc, logs[acc.id])
                btcbot = BTCBot(acc, logger, setting)
                printScreen("Report loaded", btcbot)
        elif args.action == action.TEST:
            printScreen('Running test sequence')

            setting = next(
                (s for s in settings if s.resolution == resolution), None)
            acc = accounts[0]
            # print(accounts[args.user_index-1])
            if not acc.id in logs:
                logs[acc.id] = [
                    State(datetime.today().isoformat(), 0.0, 0, 1.0)]
            logger = Logger(acc, logs[acc.id])
            btcbot = BTCBot(acc, logger, setting)
            print(btcbot.active_rp_bonus, btcbot.bonus_countdown)

    except ExitException as e:
        printScreen(f'Script ended {e}')
    except KeyboardInterrupt:
        printScreen('Script ended by user!')
