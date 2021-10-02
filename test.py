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

    for log in logs[accounts[3].id][:10]:
        print(log)



if __name__ == '__main__':
    report()