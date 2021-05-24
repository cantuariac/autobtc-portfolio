#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-


import os
import sys
import time
import pyautogui

# ReCaptcha #  X:  573 Y:  616 RGB: (255, 255, 255)
# Roll #       X:  665 Y:  706 RGB: ( 51, 140, 229)

captchaPos = (573, 616)
rollPos = (665, 706)

if len(sys.argv)>1:
	wait = int(sys.argv[1])
	for i in range(wait, 0, -1):
		print('Starting in', i, 'minutes\t\t', end='')
		sys.stdout.flush()
		time.sleep(60)
		print('\r', end='')
	print()

try:
	while True:
		
		if os.system('wmctrl -a FreeBitco.in'):						#check if it's open
			os.system('firefox --new-window https://freebitco.in &')
			print('Opening browser...\t\t')
			while os.system('wmctrl -a FreeBitco.in'):
				time.sleep(2)
			time.sleep(5)
		else:
			pyautogui.press('f5')
			print('Reloading page...\t\t')
			time.sleep(10)


		pyautogui.press('end')
		print('Looking for captcha')
		while True:
			try:
				captchaPos = pyautogui.locateCenterOnScreen('unsolved.png')
			except TypeError:
				time.sleep(1)
				continue
			break
		
		print('Unsolved captcha found at', captchaPos)
		pyautogui.moveTo(captchaPos)
		pyautogui.click()
		print('Captcha clicked')
		
		while not (pyautogui.locateOnScreen('solved.png')):
			time.sleep(2)
		print('Captcha solved')

		rollPos = pyautogui.locateCenterOnScreen('roll.png')
		print('Roll button found at', rollPos)
		pyautogui.moveTo(rollPos)
		pyautogui.click()
		print('Roll clicked')
		
		while not (pyautogui.locateOnScreen('close.png')):
			time.sleep(1)
		print('Game rolled on %s\n'%(time.asctime()))
		

		time.sleep(2)
		pyautogui.keyDown('altleft'); pyautogui.press('tab'); pyautogui.keyUp('altleft')

		time.sleep(5)
		print('Waiting for next roll...')
		for i in range(60, 0, -1):
			print(i, 'minutes remaining\t\t', end='')
			sys.stdout.flush()
			time.sleep(60)
			print('\r', end='')
		print()


except KeyboardInterrupt:
	print ('\nScript ended by user!')
