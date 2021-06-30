#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
from bs4 import BeautifulSoup
from typing import NamedTuple
from dataclasses import dataclass


class GameFailException(Exception):
    pass


class PageNotOpenException(Exception):
    pass


class GameNotReady(Exception):
    pass


# class Account(NamedTuple):
#     id: str = None
#     email: str = None
#     cookie: str = None
#     total_rolls: int = 0

#     def __str__(self) -> str:
#         return f'Account(id={self.id}, email={self.email}, total_rolls={self.total_rolls})'

@dataclass
class Account():
    id: str = None
    email: str = None
    cookie: str = None
    total_rolls: int = 0

    def __str__(self) -> str:
        return f'Account(id={self.id}, email={self.email}, total_rolls={self.total_rolls})'

class Setting(NamedTuple):
    resolution: str
    roll_position: tuple
    captcha_position: tuple

    def __str__(self) -> str:
        return f'Setting(resolution={self.resolution}, roll_position={self.roll_position}, captcha_position={self.captcha_position})'


class ChangeLog(NamedTuple):
    timestamp: str
    btc: float
    rp: int
    bonus: float
    btc_change: float
    rp_change: int
    bonus_change: float

    def __str__(self) -> str:
        return 'ChangeLog(timestamp={date}, btc={1:.8f}, rp={2}, bonus={3:.2f}, btc_change={4:.8f}, rp_change={5}, bonus_change={6:.2f})'.format(*self, date=datetime.fromisoformat(self.timestamp).strftime("%H:%m:%M %d-%b-%Y"))


class State(NamedTuple):
    timestamp: str
    btc: float
    rp: int
    bonus: float
class State(NamedTuple):
    timestamp: str
    btc: float
    rp: int
    bonus: float

    def __str__(self) -> str:
        return 'State(timestamp={date}, btc={1:.8f}, rp={2}, bonus={3:.2f}'.format(*self, date=datetime.fromisoformat(self.timestamp).strftime("%H:%m:%M %d-%b-%Y"))

    def __sub__(self, other: State) -> ChangeLog:
        if self.timestamp > other.timestamp:
            return ChangeLog(self.timestamp, self.btc, self.rp, self.bonus, self.btc-other.btc, self.rp-other.rp, self.bonus-other.bonus)
        else:
            return ChangeLog(other.timestamp, other.btc, other.rp, other.bonus, other.btc-self.btc, other.rp-self.rp, other.bonus-self.bonus)


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
