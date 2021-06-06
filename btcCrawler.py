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

width = 80
height = 15
WS = '⠀'
NAME = WS*((width-7)//2)+stylize('autoBTC',
                                 [colored.fore.GREEN, colored.style.BOLD])+WS*((width-7)//2)
LOAD_TIME = 10
outputList = [[WS*width]]*height


class User(NamedTuple):
    id: str = None
    email: str = None
    cookie: str = None
    total_rolls: int = 0

    def __str__(self) -> str:
        return f'User(id={self.id}, email={self.email}, total_rolls={self.total_rolls})'


class SavedData(NamedTuple):
    roll_position: tuple
    captcha_position: tuple
    accounts: list


class Log(NamedTuple):
    timestamp: str
    btc_balance: float
    btc_gained: float
    rp_balance: int
    rp_gained: int
    bonus: float
    bonus_loss: float


def colorChange(value, base=0, format='{:+}'):
    if value > base:
        return stylize(format.format(value), colored.fore.GREEN)
    elif value < base:
        return stylize(format.format(value), colored.fore.RED)
    else:
        return format.format(value)


class btcCrawler():

    label_row = ['', ' Current', '  Session', '    Last']
    brl_rate = None
    usd_rate = None
    brl_rate_last = None
    usd_rate_last = None

    def __init__(self, user: User = None, saved_data: SavedData = None):
        self.user = user
        btcCrawler.data = saved_data
        self.btc_last_change = self.bonus_last_change = 0.0
        self.rp_last_change = 0
        self.last_roll_timestamp = datetime.now()

        if(self.user):
            self.updatePageData()
            self.btc_start = self.btc_last = self.btc_balance
            self.rp_start = self.rp_last = self.rp_balance
            self.bonus_start = self.bonus_last = self.bonus
            self.rolls = self.user.total_rolls

            if(not user.id):
                self.user = User(self.user_id, self.user_email,
                                 user.cookie, user.total_rolls)

        btcCrawler.updateBTCprice()
        btcCrawler.brl_rate_last = btcCrawler.brl_rate
        btcCrawler.usd_rate_last = btcCrawler.usd_rate

    def updatePageData(self, fetch_rates=False):

        session = requests.Session()
        response = session.get('https://freebitco.in', headers={
            "Cookie": self.user.cookie,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        })
        self.last_update_timestamp = datetime.now()
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
        
        if(fetch_rates):
            btcCrawler.updateBTCprice()

    def setUser(self, user: User):

        self.user = user
        self.updatePageData()
        self.btc_start = self.btc_last = self.btc_balance
        self.rp_start = self.rp_last = self.rp_balance
        self.bonus_start = self.bonus_last = self.bonus
        self.rolls = self.user.total_rolls

        if(not user.id):
            self.user = User(self.user_id, self.user_email,
                             user.cookie, user.total_rolls)

    def logChange(self):
        self.btc_last_change = self.btc_balance - self.btc_last
        self.rp_last_change = self.rp_balance - self.rp_last
        self.bonus_last_change = self.bonus - self.bonus_last

        log = False
        if(self.btc_last_change != 0):
            self.btc_last = self.btc_balance
            log = True
        if(self.rp_last_change != 0):
            self.rp_last = self.rp_balance
            log = True
        if(self.bonus_last_change != 0):
            self.bonus_last = self.bonus
            log = True

        if(log):
            return Log(self.last_roll_timestamp.isoformat(), self.btc_balance, self.btc_last_change, self.rp_balance,
                       self.rp_last_change, self.bonus, self.bonus_last_change)
        else:
            return None

    def increaseUserRoll(self):
        self.rolls += 1
        return(User(self.user.id, self.user.email, self.user.cookie, self.rolls))

    def printScreen(self, output=None, clear=True, overhide=False):
        global outputList

        btc_info_row = [  # ['asd']]
            [f'BTC price', f'R$ {colorChange(btcCrawler.brl_rate, btcCrawler.brl_rate_last, "{:,.2f}")}', f' $ {colorChange(btcCrawler.usd_rate, btcCrawler.usd_rate_last, "{:,.2f}")}']]

        if(self.user):
            user_info_row = [['User', self.user.email,
                              'Last updated', self.last_update_timestamp.strftime('%H:%M:%S %d-%m-%y')]]

            btc_session_change = self.btc_balance - self.btc_start
            rp_session_change = self.rp_balance - self.rp_start
            bonus_session_change = self.bonus - self.bonus_start
            rolls_session = self.rolls - self.user.total_rolls

            btc_row = ['BTC', '%.8f' % self.btc_balance, colorChange(
                btc_session_change, format='{:+.8f}'), colorChange(self.btc_last_change, format='{:+.8f}')]

            rp_row = ['RP', self.rp_balance, colorChange(
                rp_session_change), colorChange(self.rp_last_change)]

            bonus_row = ['Bônus%', '%.2f%%' % self.bonus, colorChange(
                bonus_session_change, format='{:+.2f}%'), colorChange(self.bonus_last_change, format='{:+.2f}%')]

            rolls_row = ['Rolls', self.rolls, colorChange(
                rolls_session, format='{:+d}')]

            info_detail = [
                btcCrawler.label_row,
                btc_row,
                rp_row,
                bonus_row,
                rolls_row,
            ]
        else:
            user_info_row = [WS]
            info_detail = [WS]*5

        if(output != None):
            if(overhide):
                outputList[-1] = [output]
            else:
                outputList = (
                    outputList + [[output]])[-height:]

        s = tabulate.tabulate([
            [NAME],
            [tabulate.tabulate(btc_info_row, tablefmt='presto')],
            [tabulate.tabulate(user_info_row, tablefmt='presto')],
            [tabulate.tabulate(info_detail, tablefmt='presto',
                               colalign=("right",))],
            [tabulate.tabulate(outputList[6:],
                               tablefmt='plain')]],
            tablefmt='fancy_grid')
        if(clear):
            print(f'\033[{height+8}A', end='')
        print(s)

    # @staticmethod
    def focusOrOpenPage(self):

        if(not btcCrawler.isPageOpened()):
            os.system('firefox --new-window https://freebitco.in &')
            self.printScreen('Waiting for browser to open')
            while(not btcCrawler.isPageOpened()):
                time.sleep(1)
        else:
            os.system('wmctrl -a FreeBitco.in')

        time.sleep(0.5)
        self.printScreen('freebitco.in page is ready')

    def wait(self, seconds, what_for=''):
        if(not seconds):
            return
        self.printScreen(WS)
        self.printScreen(
            f'Waiting {seconds//60+1} minutes {what_for}', overhide=True)
        time.sleep(seconds % 60)
        seconds -= (seconds % 60)

        while(seconds > 60):
            self.printScreen(
                f'Waiting {seconds//60+1} minutes {what_for}', overhide=True)
            time.sleep(60)
            seconds -= 60

        while(seconds):
            self.printScreen(
                f'Waiting {seconds//60+1} minutes {what_for}', overhide=True)
            time.sleep(1)
            print('\r', end='')
            seconds -= 1
        self.printScreen(f'Ready {what_for}')

    def waitOrSkip(self, seconds=LOAD_TIME, what_for: str = 'something', forever=False):
        seconds *= (1+random())
        if(forever):
            self.printScreen(f'Waiting for {what_for}')
        else:
            self.printScreen(f'Waiting {int(seconds)} seconds for {what_for}')
        while(seconds > 0 or forever):
            time.sleep(1)
            seconds -= 1
            if(forever):
                self.printScreen(
                    f'Waiting for {what_for}', overhide=True)
            else:
                self.printScreen(
                    f'Waiting {int(seconds)} seconds for {what_for}', overhide=True)
            if(btcCrawler.checkRollTime()):
                return True
        return False

    def rollSequence(self, mode='auto'):

        self.focusOrOpenPage()

        pyautogui.press('f5')
        if(mode == 'auto'):
            skiped = self.waitOrSkip(LOAD_TIME, "page to load")
        elif(mode == 'manual'):
            skiped = self.waitOrSkip(what_for="user to roll", forever=True)
        else:
            return False

        if(skiped):
            self.printScreen('Click done by user')
        else:
            pyautogui.press('end')
            self.printScreen(
                'Attempting to click on CAPTCHA at (%d, %d)' % tuple(btcCrawler.data.captcha_position))
            pyautogui.moveTo(btcCrawler.data.captcha_position)
            time.sleep(random())
            pyautogui.click()

            skiped = self.waitOrSkip(LOAD_TIME, "captcha to solve")

            if(skiped):
                self.printScreen('Click done by user')
            else:
                pyautogui.press('end')
                self.printScreen('Attempting to click on roll at (%d, %d)' %
                                tuple(btcCrawler.data.roll_position))
                pyautogui.moveTo(btcCrawler.data.roll_position)
                time.sleep(random())
                pyautogui.click()

        roll_timestamp = datetime.now()

        # time.sleep(LOAD_TIME)

        if(self.waitOrSkip(LOAD_TIME, 'game to roll')):
            self.updatePageData()
            log = self.logChange()
            if (log):
                self.last_roll_timestamp = roll_timestamp
                self.printScreen(stylize(
                    'Game roll successful at ' + roll_timestamp.strftime('%H:%M:%S'), colored.fore.GREEN))
            pyautogui.keyDown('altleft')
            pyautogui.press('tab')
            pyautogui.keyUp('altleft')
            return True, log
        else:
            self.printScreen(stylize(
                'Game roll failed', colored.fore.RED))
            return False, None

    @staticmethod
    def updateBTCprice():
        j = json.loads(requests.get(
            'https://api.coindesk.com/v1/bpi/currentprice/BRL.json').text)
        btcCrawler.brl_rate = j['bpi']['BRL']['rate_float']
        btcCrawler.usd_rate = j['bpi']['USD']['rate_float']

    @staticmethod
    def isPageOpened():
        return subprocess.getoutput('wmctrl -lp | grep FreeBitco.in') != ''

    @staticmethod
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
