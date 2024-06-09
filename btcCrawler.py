#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from typing import NamedTuple
from dataclasses import dataclass
import os
import time
import pyautogui
import subprocess
import json
import requests
from datetime import datetime
from random import random
from colored import stylize
from colored import fore, back, style, stylize, bg, fg
import colored
import tabulate

from mytypes import *
from logger import *

tabulate.PRESERVE_WHITESPACE = True

width = 91
height = 15
WS = '⠀'
NAME = WS*((width-7)//2)+stylize('autoBTC',
                                 [colored.Fore.GREEN, colored.Style.BOLD])+WS*((width-7)//2)
LOAD_TIME = 10
outputList = [[WS]]*height


def coloredTag(txt, color): return fg(color)+'▕'+style.RESET+style.BOLD + \
    fore.WHITE+bg(color)+txt+style.RESET+fg(color)+'▎'+style.RESET


def colorChange(value, base=0, format='{:+}'):
    if value > base:
        return stylize(format.format(value), colored.Fore.GREEN)
    elif value < base:
        return stylize(format.format(value), colored.Fore.RED)
    else:
        return format.format(value)


class BTCBot():
    """[summary]

    Raises:
        PageNotOpenException: [description]
        GameNotReady: [description]
        GameFailException: [description]

    Returns:
        [type]: [description]
    """

    label_row = ['', ' Current', '   Month',
                 '    Week', '     Day', '  Session', '    Last']

    def __init__(self, acc: Account, logger: Logger, setting: Setting):
        self.account = acc
        self.setting = setting
        self.logger = logger

        # self.btc_last_change = self.bonus_last_change = 0.0
        # self.rp_last_change = 0
        # self.last_roll_timestamp = datetime.now()

        self.updatePageData()
        # self.logger.updateState(self.current_state)

        # self.btc_start = self.btc_last = self.btc_balance
        # self.rp_start = self.rp_last = self.rp_balance
        # self.bonus_start = self.bonus_last = self.bonus
        self.rolls = self.account.total_rolls

        if(not acc.id):
            # self.account = Account(self.account_id, self.account_email,
            #                         acc.cookie, acc.total_rolls)
            self.account.id = self.account_id
            self.account.email = self.account_email
        
    def updatePageData(self):
        """Fetch data from user from html and update attributes
        """

        session = requests.Session()
        response = session.get('https://freebitco.in', headers={
            "Cookie": self.account.cookie,
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
        })
        update_timestamp = datetime.now()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        self.account_id = soup.select_one('span.left:nth-child(2)').text
        self.account_email = soup.select_one(
            '#edit_profile_form_email').attrs['value']

        self.active_rp_bonus = soup.select("span.free_play_bonus_box_span_large")
        # print(active_bonus)
        # if len(active_bonus) == 4:
        #     l = active_bonus[0].text.split(' ')
        #     if(l[-1] == "points"):
        #         self.active_rp_bonus = f'+{l[0]}rp'
        #     s = soup.select_one("div#bonus_container_free_points").text
        #     self.bonus_countdown = int(s[s.rfind(',')+1:s.rfind(')})')])
        # else:
        self.bonus_countdown = 0
        # self.active_rp_bonus = None
        self.promotion = soup.select_one(
            '.free_play_bonus_box_span_large').text

        btc_balance_str = soup.select_one('#balance_small').text
        btc_balance = float(btc_balance_str)
        satoshi_balance = int(btc_balance_str.replace('.', ''))
        rp_balance = int(soup.select_one(
            '.user_reward_points').text.replace(',', ''))
        bonus = float(soup.select_one('#fp_bonus_req_completed').text)

        self.current_state = State(
            update_timestamp.isoformat(), btc_balance, rp_balance, bonus)

        # if(fetch_rates):
        #     BTCBot.updateBTCprice()

        # return

    # def setAccount(self, account: Account):

    #     self.account = account
    #     self.updatePageData()
    #     self.btc_start = self.btc_last = self.btc_balance
    #     self.rp_start = self.rp_last = self.rp_balance
    #     self.bonus_start = self.bonus_last = self.bonus
    #     self.rolls = self.account.total_rolls

    #     if(not account.id):
    #         self.account = Account(self.account_id, self.account_email,
    #                                account.cookie, account.total_rolls)

    # def logChange(self):
    #     self.btc_last_change = self.btc_balance - self.btc_last
    #     self.rp_last_change = self.rp_balance - self.rp_last
    #     self.bonus_last_change = self.bonus - self.bonus_last

    #     log = False
    #     if(self.btc_last_change != 0):
    #         self.btc_last = self.btc_balance
    #         log = True
    #     if(self.rp_last_change != 0):
    #         self.rp_last = self.rp_balance
    #         log = True
    #     if(self.bonus_last_change != 0):
    #         self.bonus_last = self.bonus
    #         log = True

    #     if(log):
    #         return Log(datetime.now().isoformat(), self.btc_balance, self.btc_last_change, self.rp_balance,
    #                    self.rp_last_change, self.bonus, self.bonus_last_change)
    #     else:
    #         return None

    def increaseAccountRoll(self):
        self.rolls += 1
        return(Account(self.account.id, self.account.email, self.account.cookie, self.rolls))

    # @staticmethod

    # @staticmethod

    def focusPage(self):

        if(not BTCBot.isPageOpened()):
            return False
            os.system('firefox --new-window https://freebitco.in &')
            printScreen('Waiting for browser to open', self)
            while(not btcCrawler.isPageOpened()):
                time.sleep(1)
        else:
            os.system('wmctrl -a FreeBitco.in')

        time.sleep(0.5)
        printScreen('freebitco.in page is ready', self)
        return True

    def wait(self, seconds, what_for=''):
        if(not seconds):
            return
        printScreen(WS, self)
        if(seconds > 60):
            printScreen(
                f'Waiting {seconds//60+1} minutes {what_for}', self, overhide=True)
            time.sleep(seconds % 60)
            seconds -= (seconds % 60)

        while(seconds > 60):
            printScreen(
                f'Waiting {seconds//60+1} minutes {what_for}', self, overhide=True)
            time.sleep(60)
            seconds -= 60

        while(seconds):
            printScreen(
                f'Waiting {seconds} seconds {what_for}', self, overhide=True)
            time.sleep(1)
            print('\r', end='')
            seconds -= 1
        printScreen(f'Ready {what_for}')

    def waitOrSkip(self, seconds=LOAD_TIME, what_for: str = 'something', forever=False):
        seconds *= (1+random())
        if(forever):
            printScreen(f'Waiting for {what_for}', self)
        else:
            printScreen(f'Waiting {int(seconds)} seconds for {what_for}', self)
        while(seconds > 0 or forever):
            time.sleep(1)
            seconds -= 1
            if(forever):
                printScreen(
                    f'Waiting for {what_for}', self, overhide=True)
            else:
                printScreen(
                    f'Waiting {int(seconds)} seconds for {what_for}', self, overhide=True)
            if(BTCBot.checkRollTime()):
                return True
        return False

    def rollSequence(self, mode='auto'):

        if(not self.focusPage()):
            raise PageNotOpenException

        pyautogui.press('f5')
        if(mode == 'manual'):
            skiped = self.waitOrSkip(what_for="user to roll", forever=True)
        else:  # mode == 'auto'
            skiped = self.waitOrSkip(LOAD_TIME, "page to load")

        if(skiped):
            printScreen('Click done by user', self)
        else:
            pyautogui.press('end')
            printScreen(
                'Attempting to click on CAPTCHA at (%d, %d)' % tuple(self.setting.captcha_position), self)
            pyautogui.moveTo(self.setting.captcha_position)
            time.sleep(random())
            pyautogui.click()

            skiped = self.waitOrSkip(LOAD_TIME, "captcha to solve")

            if(skiped):
                printScreen('Click done by user', self)
            else:
                pyautogui.press('end')
                printScreen('Attempting to click on roll at (%d, %d)' %
                            tuple(self.setting.roll_position), self)
                pyautogui.moveTo(self.setting.roll_position)
                time.sleep(random())
                pyautogui.click()

        # time.sleep(LOAD_TIME)

        if(skiped or self.waitOrSkip(LOAD_TIME, 'game to roll')):
            self.updatePageData()
            # log = self.logChange()
            # change = self.logger.updateState(self.current_state)
            pyautogui.keyDown('altleft')
            pyautogui.press('tab')
            pyautogui.keyUp('altleft')

            if (not self.logger.didStateChange(self.current_state)):
                raise GameNotReady
        else:
            raise GameFailException

    # @staticmethod
    # def updateBTCprice():
    #     j = json.loads(requests.get(
    #         'https://api.coindesk.com/v1/bpi/currentprice/BRL.json', timeout=5).text)
    #     BTCBot.brl_rate = j['bpi']['BRL']['rate_float']
    #     BTCBot.usd_rate = j['bpi']['USD']['rate_float']

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


brl_rate = usd_rate = 0


def updateBTCprice():
    global brl_rate, brl_rate_last, usd_rate, usd_rate_last
    j = json.loads(requests.get(
        'https://api.coindesk.com/v1/bpi/currentprice/BRL.json', timeout=5).text)
    brl_rate_last = brl_rate
    usd_rate_last = usd_rate
    brl_rate = j['bpi']['BRL']['rate_float']
    usd_rate = j['bpi']['USD']['rate_float']


updateBTCprice()


def printScreen(output=None, btcbot: BTCBot = None, clear=True, overhide=False):
    global outputList

    btc_info_row = [  # ['asd']]
        [f'BTC price', f'R$ {colorChange(brl_rate, brl_rate_last, "{:,.2f}")}', f' $ {colorChange(usd_rate, usd_rate_last, "{:,.2f}")}']]

    if(btcbot):
        account_info_row = [['Account', btcbot.account.email,
                             'Last updated', datetime.fromisoformat(btcbot.current_state.timestamp).strftime('%H:%M:%S %d-%m-%y')]]

        tags_row = [WS]  # [[coloredTag(tag, 'green') for tag in tags]]
        # btc_session_change = btcbot.btc_balance - btcbot.btc_start
        # rp_session_change = btcbot.rp_balance - btcbot.rp_start
        # bonus_session_change = btcbot.bonus - btcbot.bonus_start
        rolls_session = btcbot.account.total_rolls - btcbot.rolls

        btc_row = ['BTC', '%.8f' % btcbot.current_state.btc,
                   colorChange(btcbot.logger.month_change.btc_change,
                               format='{:+.8f}'),
                   colorChange(btcbot.logger.week_change.btc_change,
                               format='{:+.8f}'),
                   colorChange(btcbot.logger.day_change.btc_change,
                               format='{:+.8f}'),
                   colorChange(
                       btcbot.logger.session_change.btc_change, format='{:+.8f}'),
                   colorChange(btcbot.logger.last_change.btc_change, format='{:+.8f}')]

        rp_row = ['RP', btcbot.current_state.rp,
                  colorChange(btcbot.logger.month_change.rp_change),
                  colorChange(btcbot.logger.week_change.rp_change),
                  colorChange(btcbot.logger.day_change.rp_change),
                  colorChange(btcbot.logger.session_change.rp_change),
                  colorChange(btcbot.logger.last_change.rp_change)]  # ,
        # stylize(f'{btcbot.active_rp_bonus} for {btcbot.bonus_countdown//60//60}h', colored.Fore.GREEN) if btcbot.active_rp_bonus else '']

        bonus_row = [
            'Bônus%',
            '%.2f%%' % btcbot.current_state.bonus,
            colorChange(btcbot.logger.month_change.bonus_change,
                        format='{:+.2f}%'),
            colorChange(btcbot.logger.week_change.bonus_change,
                        format='{:+.2f}%'),
            colorChange(btcbot.logger.day_change.bonus_change,
                        format='{:+.2f}%'),
            colorChange(btcbot.logger.session_change.bonus_change,
                        format='{:+.2f}%'),
            colorChange(btcbot.logger.last_change.bonus_change,
                        format='{:+.2f}%')
        ]

        rolls_row = [
            'Logs',
            len(btcbot.logger.logs),
            # btcbot.account.total_rolls,
            btcbot.logger.month_log_count,
            btcbot.logger.week_log_count,
            btcbot.logger.day_log_count,
            colorChange(rolls_session, format='{:+d}')
        ]

        info_detail = [
            BTCBot.label_row,
            btc_row,
            rp_row,
            bonus_row,
            rolls_row,
        ]
    else:
        account_info_row = [WS]
        tags_row = [WS]
        info_detail = [WS]*5

    if(output != None):
        if(len(output) > width):
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
        # [tabulate.tabulate(tags_row, tablefmt='plain')],
        [tabulate.tabulate(info_detail, tablefmt='presto',
                           colalign=("right",))],
        [tabulate.tabulate(outputList[6:],
                           tablefmt='plain')]],
        tablefmt='fancy_grid')
    if(clear):
        print(f'\033[{height+8}A', end='')
    print(s)
