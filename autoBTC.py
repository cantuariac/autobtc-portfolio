#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-

import argparse
import os
import sys
import time
import pyautogui
import subprocess
import json
from datetime import datetime
from random import random
from colored import stylize
import colored
from collections import namedtuple
from dataclasses import dataclass

from bs4 import BeautifulSoup

fore = colored.fore()

SavedData = namedtuple('SavedData', ['captcha_position', 'roll_position', 'load_time', 'logs'])
# Log = namedtuple('Log', ['timestamp', 'rp_balance', 'btc_balance', 'rp_gained', 'btc_gained'])

@dataclass
class Log:
    timestamp : str
    rp_balance : int
    btc_balance : int
    rp_gained : int
    btc_gained : int

def isPageOpened():
    return subprocess.getoutput('wmctrl -lp | grep FreeBitco.in') != ''

def focusOrOpenPage():

    if(not isPageOpened()):
        os.system('firefox --new-window https://freebitco.in &')
        print('Waiting for browser to open')
        while(not isPageOpened()):
            time.sleep(1)
        time.sleep(load_time)
    else:
        os.system('wmctrl -a FreeBitco.in')
        time.sleep(1)
        pyautogui.press('f5')
        print('Waiting for page to load')
        time.sleep(load_time)
    
    print('freebitco.in page is ready')

def checkRollTime():
    output = subprocess.getoutput('wmctrl -lp | grep FreeBitco.in').split()
    if not output:
        return

    # win_code = output[0]
    # pid = int(output[2])
    if output[4] == 'FreeBitco.in':
        return 0
    else:
        roll_time = datetime.strptime(output[4], '%Mm:%Ss')
        return roll_time.minute * 60 + roll_time.second

def parsePage():
    focusOrOpenPage()
    
    pyautogui.hotkey('ctrl', 'u')
    time.sleep(0.5)

    pyautogui.press('f5')
    time.sleep(5)
    
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)

    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)

    pyautogui.hotkey('ctrl', 'w')
    time.sleep(0.5)

    # pyautogui.hotkey('alt', 'tab')

    html = subprocess.getoutput('xclip -o')
    soup = BeautifulSoup(html, 'html.parser')
    balance = round(float(soup.select_one('#balance_small').text)*100000000)
    RP = int(soup.select_one('.user_reward_points').text.replace(',', ''))
    user_id = soup.select_one('span.left:nth-child(2)').text

    return user_id, RP, balance

captcha_position = None
roll_position = None
load_time = 10
logs = {}

def saveData():
    fd = open('saved_data.json', 'w')
    json.dump(SavedData(captcha_position, roll_position, load_time, logs)._asdict(), fd, indent=2)
    fd.close()

def wait(seconds, what_for=''):
    print('Waiting %d minutes'%(seconds//60+1), what_for, ' ', flush=True, end='')
    time.sleep(seconds%60)
    print('\r', end='')
    seconds -= (seconds%60)
    while(seconds>60):
        print('Waiting %d minutes'%(seconds//60), what_for, ' ', flush=True, end='')
        time.sleep(60)
        print('\r', end='')
        seconds -= 60
    while(seconds):
        print('Waiting %d seconds'%(seconds%60), what_for, ' ', flush=True,  end='')
        time.sleep(1)
        print('\r', end='')
        seconds -= 1
    print('Ready', what_for, ' '*20)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                description="""Script to automate rolls for FreeBitco.in """)
    
    commandGroup = parser.add_argument_group('actions')
    commandGroup.add_argument('-l',"-logs",  action='store_true', dest='logs',
        help="Show logs and exit")
    commandGroup.add_argument('-s',"-set",  action='store_true', dest='set',
        help="Set click positions for CAPTCHA checkbox and ROLL button")
    commandGroup.add_argument('-r', "-run",  action='store_true', dest='run',
        help="Run script with current configurations")
                                    
    args = parser.parse_args()
    print(args)

    if(os.path.isfile('saved_data.json')):
        fd = open('saved_data.json')
        captcha_position, roll_position, load_time, logs = SavedData(**json.load(fd))
        fd.close()
        print('\'saved_data.json\' file loaded')

    else:
        print('Saved data file not found')
        # data = SavedData(None, None, 10, {})
        # fd = open('saved_data.json', 'w')
        # json.dump(SavedData(None, None, 10, {})._asdict(), fd, indent=2)
        # fd.close()
        captcha_position = None
        roll_position = None
        load_time = 10
        logs = {}
        saveData()
        print('\'saved_data.json\' file created')

    print()
    try:
        if(args.logs):
            for user in logs:
                print(user)
                for log in logs[user]:
                    pass
                    # timestamp, RP, balance = log
                    # log[0] = datetime.fromtimestamp(log[0]).isoformat()

            saveData()
            exit()
        
        # openOrFocusPage()

        print('Checking current balance')
        user, last_rp, last_balance = parsePage()
        pyautogui.keyDown('altleft'); pyautogui.press('tab'); pyautogui.keyUp('altleft')

        roll_wait = checkRollTime()
        if(roll_wait):
            wait(roll_wait, 'for next roll')
        
        if(args.set):
            focusOrOpenPage()

            print('Setting click positions')

            for i in range(load_time*10, 0, -1):
                current = pyautogui.position()
                print('Mouse over CAPTCHA checkbox position and wait %f seconds (%d, %d)'
                    %(i/10, current.x, current.y), end='', flush=True)
                time.sleep(0.1)
                print('\r', end='')
            captcha_position = pyautogui.position()
            print('CAPTCHA position set at (%d, %d)'%captcha_position, ' '*20)
            
            for i in range(load_time*10, 0, -1):
                current = pyautogui.position()
                print('Mouse over ROLL button position and wait %f seconds (%d, %d)'
                    %(i/10, current.x, current.y), end='', flush=True)
                time.sleep(0.1)
                print('\r', end='')
            roll_position = pyautogui.position()
            print('ROLL position set at (%d, %d)'%roll_position, ' '*20)

            # fd = open('saved_data.json', 'w')
            # json.dump(SavedData(captcha_position, roll_position, load_time, logs)._asdict(), fd, indent=2)
            # fd.close()
            saveData()
            print('Settings saved')

        # print('Starting roll loop')

        if(args.run):
            while(True):

                focusOrOpenPage()
                pyautogui.press('end')
                time.sleep(1)

                print('Attempting to click on CAPTCHA at', tuple(captcha_position))
                pyautogui.moveTo(captcha_position)
                time.sleep(random())
                pyautogui.click()
                print('Waiting for captcha to solve...')
                time.sleep(load_time*(1+random()))

                print('Attempting to click on roll at', tuple(roll_position))
                pyautogui.moveTo(roll_position)
                time.sleep(random())
                pyautogui.click()
                print('Waiting for game to roll...')
                roll_timestamp = datetime.now()
                time.sleep(load_time*(1+random()))

                roll_wait = checkRollTime()
                
                if(roll_wait):
                    user, rp, balance = parsePage()
                    print(stylize('Game roll successful at %s, %d satoshi and %d RP earned'%
                                (roll_timestamp.strftime('%H:%M:%S'), balance-last_balance, rp-last_rp),
                                fore.GREEN))
                    print('BTC balance: %d\tRP balance: %d'%(balance, rp))
                    #pyautogui.press('f5')
                    #time.sleep(load_time)
                    if user not in logs:
                        logs[user] = []
                    logs[user].append((roll_timestamp.isoformat(), rp, balance, rp-last_rp, balance-last_balance))
                    last_balance = balance
                    last_rp = rp
                    saveData()
                    print('Operation logged\n')

                    pyautogui.keyDown('altleft'); pyautogui.press('tab'); pyautogui.keyUp('altleft')
                    wait(checkRollTime(), 'for next roll')
                    # print()
                else:
                    print(stylize('Game roll failed', fore.RED))
                    print('Reloading page and trying again')
                    # pyautogui.press('f5')
                #print()
                
    
    except KeyboardInterrupt:
        print ('\nScript ended by user!')        
