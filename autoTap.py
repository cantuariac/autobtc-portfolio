#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-

import os
import sys
import time
import datetime
import pyautogui
import subprocess
import json
from random import randint, random


load_delay = 5
tap_delay = 1


def isPageOpened():
  return subprocess.getoutput('wmctrl -lp | grep Quack') != ''

def clickLoop(start_taps=100):
  t0 = datetime.datetime.now()
    
  taps = start_taps
  while(True):
    if(taps == 0):
      print(' '*55, end='\r')
      wait = 15*60+2
      while(wait):
        print('Waiting for more taps %d:%d'%(wait//60, wait%60), end='\r')
        time.sleep(1)
        wait -= 1
      taps=150
    if(isPageOpened()):
      # os.system('wmctrl -a Quack')
      time.sleep(0.1)
      tap_random = tap_position.x+randint(-10, 10), tap_position.y+randint(-10, 10)
      pyautogui.moveTo(tap_random, duration=0.1)
      time.sleep(0.1)
      pyautogui.click()
      taps -= 1
      ti = datetime.datetime.now()
      print('clicked at', tap_random, 'delay', (ti - t0), '%d taps left'%taps, end='\r')
      t0 = ti
      time.sleep(tap_delay * (1 + random()))
    else:
      print('Quack not opened')
      break

if __name__ == '__main__':
  print('Setting tap position')

  for i in range(load_delay*10, 0, -1):
    current = pyautogui.position()
    print('Mouse over Tap button position and wait %.1f seconds (%d, %d)'
        % (i/10, current.x, current.y), end='', flush=True)
    time.sleep(0.1)
    print('\r', end='')
  tap_position = pyautogui.position()
  print('Tap position set at (%d, %d)' % tap_position, ' '*40)

  
  try:
    if len(sys.argv)==2:
      start_taps = int(sys.argv[1])
    else:
      start_taps = 150
    clickLoop(start_taps)
  except KeyboardInterrupt:
    print()
