#!/usr/bin/python3
# -*- coding: utf-8 -*-

def boxit(text: str):
    out = ' '+'\N{Combining Overline}\N{Combining Low Line}'
    out = out + ' '+'\N{Combining Overline}\N{Combining Low Line}'
    for c in text[:]:
        out = out + c + '\N{Combining Overline}\N{Combining Low Line}'
    return out[:]


def tags():
    import tabulate

    from colored import fore, back, style, stylize, bg, fg

    coloredTag = lambda txt, color : fg(color)+'▕'+style.RESET+style.BOLD+fore.WHITE+bg(color)+txt+style.RESET+fg(color)+'▎'+style.RESET

    print(tabulate.tabulate([[
                          coloredTag('auto', 'green'), 
                          coloredTag('bonus', 'red')
                          ]]))#, tablefmt='fancy_grid'))

    print(fore.RED+'▕'+style.RESET+style.BOLD+back.RED+'auto'+style.RESET+fore.RED+'▎'+style.RESET)


import os
import json
from pprint import pprint
from mytypes import *

accounts = {}
settings = {}
DATA_FILE = 'data.json'
logs = {}
LOGS_FILE = 'logs.json'

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

def weektag(date : datetime.date):
    return f"{date.year}-{date.isocalendar()[1]}"

def report():
    
    if(os.path.isfile(DATA_FILE)):
        loadData()
        print(f'Data file loaded')
    else:
        print('Saved data file not found')
        saveData()
        print(f'Data file created')

    if(os.path.isfile(LOGS_FILE)):
        loadLogs()
        print(f'Logs file loaded')
    else:
        print('Logs file not found')
        saveLogs()
        print(f'Logs file created')

    logs2:list = logs[accounts[2].id]
    
    daily = {}
    fst_day_state = State(*logs2[0][:4])
    day = datetime.fromisoformat(logs2[0].timestamp).date()

    weekly = {}
    fst_week_state = fst_day_state
    week = weektag(day)

    monthly = {}
    fst_month_state = fst_day_state
    month = day

    for log in logs2[1:]:
        log_date = datetime.fromisoformat(log.timestamp).date()

        if day != log_date:
            daily[day] = State(*log[:4]) - fst_day_state
            fst_day_state = State(*log[:4])
            day = log_date
        
            if weektag(log_date) != week:
                weekly[week] = State(*log[:4]) - fst_week_state
                fst_week_state = State(*log[:4])
                week = weektag(log_date)
            
            if log_date.month != month.month or log_date.year != month.year:
                monthly[month] = State(*log[:4]) - fst_month_state
                fst_month_state = State(*log[:4])
                month = log_date
    
    if day not in daily:
        daily[day] = State(*log[:4]) - fst_day_state
    if week not in weekly:
        weekly[week] = State(*log[:4]) - fst_week_state
    if month not in monthly:
        monthly[month] = State(*log[:4]) - fst_month_state
    
    print("Daily Changelogs:")
    for log in daily.values():
        print(log)
    
    print("Weekly Changelogs:")
    for week, log in weekly.items():
        print(week, log)

    print("Monthly Changelogs:")
    for month, log in monthly.items():
        print(month, log)


if __name__ == '__main__':
    report()