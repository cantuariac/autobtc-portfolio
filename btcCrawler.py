#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from typing import NamedTuple
import os
import time
import pyautogui
import subprocess
import json
import requests
from datetime import datetime
from random import random
from colored import stylize
import colored
import tabulate

tabulate.PRESERVE_WHITESPACE = True

width = 80
height = 15
WS = '⠀'
NAME = WS*((width-7)//2)+stylize('autoBTC',
                                 [colored.fore.GREEN, colored.style.BOLD])+WS*((width-7)//2)
LOAD_TIME = 10
outputList = [[WS]]*height


class GameFailException(Exception):
    pass

class PageNotOpenException(Exception):
    pass

class GameNotReady(Exception):
    pass

class Account(NamedTuple):
    id: str = None
    email: str = None
    cookie: str = None
    total_rolls: int = 0

    def __str__(self) -> str:
        return f'Account(id={self.id}, email={self.email}, total_rolls={self.total_rolls})'


class Setting(NamedTuple):
    roll_position: tuple
    captcha_position: tuple
    def __str__(self) -> str:
        return f'(roll_position={self.roll_position}, captcha_position={self.captcha_position})'


class Log(NamedTuple):
    timestamp: str
    btc_balance: float
    btc_gained: float
    rp_balance: int
    rp_gained: int
    bonus: float
    bonus_loss: float

    def __str__(self) -> str:
        return 'Log({date}, {1:.8f}, {2:.8f}, {3}, {4}, {5:.2f}, {6:.2f})'.format(*self, date=datetime.fromisoformat(self.timestamp).strftime("%d-%b-%Y-%H:%m:%M"))
        # return 'Log({0}, {1:.8f}, {2:.8f}, {3}, {4}, {5:.2f}, {6:.2f})'.format(*self)


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

    def __init__(self, acc : Account = None, setting : Setting = None):
        self.account = acc
        self.setting = setting
        self.btc_last_change = self.bonus_last_change = 0.0
        self.rp_last_change = 0
        self.last_roll_timestamp = datetime.now()

        if(self.account):
            self.updatePageData()
            self.btc_start = self.btc_last = self.btc_balance
            self.rp_start = self.rp_last = self.rp_balance
            self.bonus_start = self.bonus_last = self.bonus
            self.rolls = self.account.total_rolls

            if(not acc.id):
                self.account = Account(self.account_id, self.account_email,
                                 acc.cookie, acc.total_rolls)

        btcCrawler.updateBTCprice()
        btcCrawler.brl_rate_last = btcCrawler.brl_rate
        btcCrawler.usd_rate_last = btcCrawler.usd_rate

    def updatePageData(self, fetch_rates=False):

        session = requests.Session()
        response = session.get('https://freebitco.in', headers={
            "Cookie": self.account.cookie,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        })
        self.last_update_timestamp = datetime.now()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        self.account_id = soup.select_one('span.left:nth-child(2)').text
        self.account_email = soup.select_one(
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

    def setAccount(self, account: Account):

        self.account = account
        self.updatePageData()
        self.btc_start = self.btc_last = self.btc_balance
        self.rp_start = self.rp_last = self.rp_balance
        self.bonus_start = self.bonus_last = self.bonus
        self.rolls = self.account.total_rolls

        if(not account.id):
            self.account = Account(self.account_id, self.account_email,
                             account.cookie, account.total_rolls)

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
            return Log(datetime.now().isoformat(), self.btc_balance, self.btc_last_change, self.rp_balance,
                       self.rp_last_change, self.bonus, self.bonus_last_change)
        else:
            return None

    def increaseAccountRoll(self):
        self.rolls += 1
        return(Account(self.account.id, self.account.email, self.account.cookie, self.rolls))

    def printScreen(self, output=None, clear=True, overhide=False):
        global outputList

        btc_info_row = [  # ['asd']]
            [f'BTC price', f'R$ {colorChange(btcCrawler.brl_rate, btcCrawler.brl_rate_last, "{:,.2f}")}', f' $ {colorChange(btcCrawler.usd_rate, btcCrawler.usd_rate_last, "{:,.2f}")}']]

        if(self.account):
            account_info_row = [['Account', self.account.email,
                              'Last updated', self.last_update_timestamp.strftime('%H:%M:%S %d-%m-%y')]]

            btc_session_change = self.btc_balance - self.btc_start
            rp_session_change = self.rp_balance - self.rp_start
            bonus_session_change = self.bonus - self.bonus_start
            rolls_session = self.rolls - self.account.total_rolls

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
            account_info_row = [WS]
            info_detail = [WS]*5

        if(output != None):
            if(len(output)>width):
                output = output[:width]
            if(overhide):
                outputList[-1] = [output]
            else:
                outputList = (
                    outputList + [[output]])[-height:]

        s = tabulate.tabulate([
            [NAME],
            [tabulate.tabulate(btc_info_row, tablefmt='presto')],
            [tabulate.tabulate(account_info_row, tablefmt='presto')],
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
            return False
            os.system('firefox --new-window https://freebitco.in &')
            self.printScreen('Waiting for browser to open')
            while(not btcCrawler.isPageOpened()):
                time.sleep(1)
        else:
            os.system('wmctrl -a FreeBitco.in')

        time.sleep(0.5)
        self.printScreen('freebitco.in page is ready')
        return True

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

        if(not self.focusOrOpenPage()):
            raise PageNotOpenException

        pyautogui.press('f5')
        if(mode == 'manual'):
            skiped = self.waitOrSkip(what_for="user to roll", forever=True)
        else:       #mode == 'auto'
            skiped = self.waitOrSkip(LOAD_TIME, "page to load")
        

        if(skiped):
            self.printScreen('Click done by user')
        else:
            pyautogui.press('end')
            self.printScreen(
                'Attempting to click on CAPTCHA at (%d, %d)' % tuple(self.setting.captcha_position))
            pyautogui.moveTo(self.setting.captcha_position)
            time.sleep(random())
            pyautogui.click()

            skiped = self.waitOrSkip(LOAD_TIME, "captcha to solve")

            if(skiped):
                self.printScreen('Click done by user')
            else:
                pyautogui.press('end')
                self.printScreen('Attempting to click on roll at (%d, %d)' %
                                tuple(self.setting.roll_position))
                pyautogui.moveTo(self.setting.roll_position)
                time.sleep(random())
                pyautogui.click()


        # time.sleep(LOAD_TIME)

        if(skiped or self.waitOrSkip(LOAD_TIME, 'game to roll')):
            self.updatePageData()
            log = self.logChange()
            pyautogui.keyDown('altleft')
            pyautogui.press('tab')
            pyautogui.keyUp('altleft')

            if (not log):
                raise GameNotReady
            return log
        else:
            raise GameFailException

    @staticmethod
    def updateBTCprice():
        j = json.loads(requests.get(
            'https://api.coindesk.com/v1/bpi/currentprice/BRL.json', timeout=5).text)
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
