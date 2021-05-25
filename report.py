#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import datetime
from collections import namedtuple
from dataclasses import dataclass

import requests
import argh
from tabulate import tabulate

from autoBTC import isPageOpened, SavedData, Log

@dataclass
class Row:
    satoshi : int
    rp : int
    games : int

def main(operation : '(all | bydate)',format : '(table | raw)', last=5):
    '''
    
    '''

    fd = open('saved_data.json')
    captcha_position, roll_position, load_time, logs = SavedData(**json.load(fd))
    fd.close()
    for user in logs:
        logs[user] = [Log(*l) for l in logs[user]]
    print('\'saved_data.json\' file loaded')

    j=json.loads(requests.get('https://api.coindesk.com/v1/bpi/currentprice/BRL.json').text)
    brl_rate = j['bpi']['BRL']['rate_float']
    usd_rate = j['bpi']['USD']['rate_float']

    if operation == 'bydate':
        for user in logs:
            print('User:',user)
            daily = {}
            weekly = {}
            monthly = {}
            total = Row(0, 0, 0)

            for log in logs[user]:
                day = datetime.datetime.fromisoformat(log.timestamp).date()
                if day in daily:
                    daily[day].satoshi += log.btc_gained
                    daily[day].rp += log.rp_gained
                    daily[day].games += 1
                else:
                    daily[day] = Row(log.btc_gained, log.rp_gained, 1)
                
                week = day.strftime('%U-%Y')
                if week in weekly:
                    weekly[week].satoshi += log.btc_gained
                    weekly[week].rp += log.rp_gained
                    weekly[week].games += 1
                else:
                    weekly[week] = Row(log.btc_gained, log.rp_gained, 1)
                
                month = day.strftime('%b-%Y')
                if month in monthly:
                    monthly[month].satoshi += log.btc_gained
                    monthly[month].rp += log.rp_gained
                    monthly[month].games += 1
                else:
                    monthly[month] = Row(log.btc_gained, log.rp_gained, 1)
                
                total.satoshi += log.btc_gained
                total.rp += log.rp_gained
                total.games += 1

            print(tabulate([[' ', 'BTC price', 'Balance'],
                            ['BTC', 1, '₿ %.8f'%(logs[user][-1].btc_balance/100000000)],
                            ['RP', 100000000, logs[user][-1].rp_balance],
                            ['BRL', 'R$ %.2f'%brl_rate, 'R$ %.2f'%(logs[user][-1].btc_balance*brl_rate/100000000)],
                            ['USD', '$ %.2f'%usd_rate, '$ %.2f'%(logs[user][-1].btc_balance*usd_rate/100000000)]],
                            tablefmt='fancy_grid'))

            print('\nEarnings:')
            if format == 'table':
                f = 'fancy_grid'
            elif format == 'raw':
                f = 'simple'
            else:
                raise argh.CommandError(format)
            print(tabulate([(d, t.satoshi, '%.2f'%(t.satoshi*brl_rate/100000000), t.rp, t.games) for d,t in list(daily.items())[-last:]],
                    headers=['daily', 'BTC gained', 'BRL', 'RP gained', 'rolls'], tablefmt=f))
            print(tabulate([(d+'⠀⠀⠀', t.satoshi, '%.2f'%(t.satoshi*brl_rate/100000000), t.rp, t.games) for d,t in weekly.items()],
                    headers=['weekly', 'BTC gained', 'BRL', 'RP gained', 'rolls'], tablefmt=f))
            print(tabulate( [(d+'⠀⠀', t.satoshi, '%.2f'%(t.satoshi*brl_rate/100000000), t.rp, t.games) for d,t in monthly.items()] + 
                            [('Total', total.satoshi, '%.2f'%(total.satoshi*brl_rate/100000000), total.rp, total.games)],
                    headers=['monthly', 'BTC gained', 'BRL', 'RP gained', 'rolls'], tablefmt=f))
    elif operation == 'all':
        for user in logs:
            print('User:',user)

            if format == 'raw':
                print(*logs[user][0].__dict__, sep=', ')
                for log in logs[user][-last:]:
                    print(*log.__dict__.values(), sep=', ')
                    # log = Log()
                    # print(datetime.datetime.fromisoformat(log.timestamp), log.rp_balance, log)
            elif format == 'table':
                # print(type(logs[user][-last:]), logs[user][-last:])
                print(tabulate([log.__dict__.values() for log in logs[user][-last:]],
                    headers=logs[user][0].__dict__, tablefmt='fancy_grid'))
            else:
                raise argh.CommandError(format)
    else:
        raise argh.CommandError(operation)

if __name__ == '__main__':
    argh.dispatch_command(main)
    # parser = argh.ArghParser()
