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

def userInput():
    global command
    while True:
        command = input('> ')
        if(command=='q'):
            break
        


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
        'settings': {res: (settings[res]._asdict()) for res in settings},
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
    settings = {
        res: Setting(res, tuple(settings[res]['roll_position']), tuple(
            settings[res]['captcha_position']))
        # res:Setting(tuple(settings[res][0]), tuple(settings[res][1]))
        for res in settings}
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
    resolution = subprocess.getoutput(
        'xrandr | grep current').split(',')[1][9:]

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

            consecutive_errors = 0
            while(True):
                try:
                    btc.updatePageData()#fetch_rates=True)
                    btc.wait(btcCrawler.checkRollTime(),
                             'for next roll')

                    btc.updatePageData()#fetch_rates=True)
                    log = btc.logChange()
                    if (log):
                        if btc.account.id in logs:
                            logs[btc.account.id].append(log)
                        else:
                            logs[btc.account.id] = [log]
                        saveLogs()
                        btc.printScreen('Unknown change logged')
                    log = btc.rollSequence(args.mode)
                except PageNotOpenException:
                    btc.printScreen(
                        stylize('Page not opened', colored.fore.RED))
                    btc.printScreen('Waiting for user to open page')
                    time.sleep(LOAD_TIME)
                    consecutive_errors += 1
                    btc.printScreen('Reloading page and trying again')
                except GameNotReady:
                    btc.printScreen(
                        stylize('Game not ready', colored.fore.RED))
                    consecutive_errors += 1
                except GameFailException:
                    btc.printScreen(
                        stylize('Game roll failed', colored.fore.RED))
                    consecutive_errors += 1
                    btc.printScreen('Reloading page and trying again')
                except Exception as error:
                    btc.printScreen(
                        stylize(f'Unknown error:{error}', colored.fore.RED))
                    print(error.with_traceback())
                    raise ExitException
                else:
                    btc.printScreen(stylize('Game roll successful at ' + datetime.fromisoformat(
                        log.timestamp).strftime('%H:%M:%S'), colored.fore.GREEN))

                    accounts[args.user_index - 1] = btc.increaseAccountRoll()
                    if btc.account.id in logs:
                        logs[btc.account.id].append(log)
                    else:
                        logs[btc.account.id] = [log]
                    saveData()
                    saveLogs()
                    btc.printScreen('Roll logged')
                    consecutive_errors = 0

                if(consecutive_errors > 10):
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

            btc.printScreen(
                f'Setting click positions for {resolution} resolution')
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
                            roll_position, overhide=True)

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

            # fst_today = datetime.today().isoformat()
            # t = threading.Thread(target=userInput)
            # while True:
            #     btc.wait(5, 'something')
            #     if(command):
            #         btc.printScreen()
            #         btc.printScreen('command is '+command)
            #         command=None
            # logs2 = {}
            # for acc in logs:
            #     logs2[acc] = [ChangeLog(l.timestamp, l.btc_balance, l.rp_balance, l.bonus, l.btc_gained, l.rp_gained, l.bonus_loss) for l in logs[acc]]

            # accounts2 = [Account2( *acc) for acc in accounts]
            
            # fd = open(DATA_FILE, 'w')
            # json.dump({
            #     'settings': {res: (settings[res]._asdict()) for res in settings},
            #     'accounts': [acc.__dict__ for acc in accounts2],
            # }, fd, indent=2)
            # fd.close()
            # s = json.dumps(logs2, indent=2)
            # s = s.replace('\n      ', ' ')
            # s = s.replace('\n    ],', ' ],')
            # s = s.replace('\n    ]', ' ]')
            # fd = open(LOGS_FILE, 'w')
            # fd.write(s)
            # fd.close()
            # for k in logs:
            #     print(logs[k][-1])
            # for acc in accounts:
            #     print(acc)
            # for r in settings:
            #     print(settings[r])
            # saveData()
            # saveLogs()
            # last = State(*logs2[-1][:4])
            # logger = Logger(accounts[1], logs2, last)

            # logger.current_change()
            # print(logs2[-1])
            # logger.updateState(State(datetime.now().isoformat(), last.btc+0.00000006, last.rp+100, last.bonus-0.01))
            # print(logs2[-1])
            # logger.current_change()

            # print(logger.last_state)
            # print("today:",logger.day_start_state-logger.last_state)
            # print('this week:',logger.week_start_state-logger.last_state)
            # print('this month:', logger.month_start_state-logger.last_state)

    except ExitException as e:
        btc.printScreen(f'Script ended {e}')
    except KeyboardInterrupt:
        btc.printScreen('Script ended by user!')
