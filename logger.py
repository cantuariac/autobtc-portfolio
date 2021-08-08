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

from mytypes import *


class Logger():

    def __init__(self, acc: Account, logs: list, state: State = None):
        self.logs = logs
        self.account = acc
        if(not state):
            state = State(*self.logs[-1][:4])

        self.init_day = datetime.today().date().isoformat()
        self.session_first_state = self.last_state = State(*self.logs[-1][:4])
        # self.last_change = ChangeLog(*self.last_state, 0,0,0)
        # self.session_change = ChangeLog(*self.last_state, 0,0,0)
        # self.day_change = ChangeLog(*self.last_state, 0,0,0)
        # self.week_change = ChangeLog(*self.last_state, 0,0,0)
        # self.month_change = ChangeLog(*self.last_state, 0,0,0)
        self.setStartStates()
        self.last_change = self.last_state - state
        self.session_change = self.session_first_state - state
        self.day_change = self.day_first_state - state
        self.week_change = self.week_first_state - state
        self.month_change = self.month_first_state - state
        self.updateState(state)

    def setStartStates(self):
        today = datetime.today().date().isoformat()
        week = datetime.today().strftime('%Y-%U')
        month = datetime.today().strftime('%Y-%m')

        fst_today = fst_week = fst_month = len(self.logs)-1

        for i in range(len(self.logs)-1, -1, -1):
            log_date = datetime.fromisoformat(self.logs[i].timestamp)
            if(log_date.isoformat() > today):
                fst_today = i
            if(log_date.strftime('%Y-%U') == week):
                fst_week = i
            if(log_date.strftime('%Y-%m') == month):
                fst_month = i

        self.day_first_state = State(*self.logs[fst_today][:4])
        self.week_first_state = State(*self.logs[fst_week][:4])
        self.month_first_state = State(*self.logs[fst_month][:4])

        n = len(self.logs)
        self.day_log_count = n-fst_today
        self.week_log_count = n-fst_week
        self.month_log_count = n-fst_month

    def didStateChange(self, state: State):
        return ((self.last_state.btc != state.btc) |
                (self.last_state.rp != state.rp) |
                (self.last_state.bonus != state.bonus))

    def updateState(self, state: State):
        if(datetime.today().date().isoformat() > self.init_day):
            self.setStartStates()
        if (self.didStateChange(state)):

            self.last_change = self.last_state - state
            self.session_change = self.session_first_state - state
            self.day_change = self.day_first_state - state
            self.week_change = self.week_first_state - state
            self.month_change = self.month_first_state - state

            self.day_log_count += 1
            self.week_log_count += 1
            self.month_log_count += 1

            self.last_state = state
            self.logs.append(self.last_change)
            return True
        else:
            return False

    def current_change(self):
        if(datetime.today().date().isoformat() > self.init_day):
            self.setStartStates()
        print("today:\t\t", self.day_first_state-self.last_state)
        print("this session:\t", self.session_first_state-self.last_state)
        print('this week:\t', self.week_first_state-self.last_state)
        print('this month:\t', self.month_first_state-self.last_state)
