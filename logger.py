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
import colored
import tabulate

from btcCrawler import *

class Logger():

    def __init__(self, acc: Account, logs: list, last_state: State = None):
        self.logs = logs
        self.account = acc

        today = datetime.today().date().isoformat()
        week = datetime.today().strftime('%Y-%U')
        month = datetime.today().strftime('%Y-%m')

        fst_today = fst_week = fst_month = len(self.logs)-1

        for i in range(len(logs)-1, -1, -1):
            log_date = datetime.fromisoformat(logs[i].timestamp)
            if(log_date.isoformat() > today):
                fst_today = i
            if(log_date.strftime('%Y-%U') == week):
                fst_week = i
            if(log_date.strftime('%Y-%m') == month):
                fst_month = i

        self.session_start_state = self.last_state = last_state
        self.day_start_state = State(*self.logs[fst_today][:4])
        self.week_start_state = State(*self.logs[fst_week][:4])
        self.month_start_state = State(*self.logs[fst_month][:4])

    def updateState(self, state: State):
        if ((self.last_state.btc != state.btc) |
            (self.last_state.rp != state.rp) |
            (self.last_state.bonus != state.bonus)):
            log = self.last_state - state
            self.last_state = state
            self.logs.append(log)
            return log
        else:
            return None

    def current_change(self):
        print("today:\t\t", self.day_start_state-self.last_state)
        print("this session:\t", self.session_start_state-self.last_state)
        print('this week:\t', self.week_start_state-self.last_state)
        print('this month:\t', self.month_start_state-self.last_state)