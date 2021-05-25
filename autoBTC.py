#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-


import argparse
import os
import sys
import time
import pyautogui
import subprocess

captchaPos = (435, 599)
rollPos = (558, 693)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
				description="""Script to automate rolls for FreeBitco.in """)
					
	parser.add_argument( "-m", "--method", choices=['fixed','seek', 'seek_first', 'set_first'], default='fixed',
						help="Show")
	parser.add_argument( "-sd", "--start-delay", type=int, default=0,
						help="Delay in minutes before start the script")
	parser.add_argument( "-cd", "--captcha-delay", type=int, default=20,
						help="Delay in seconds before start the script")
									
	args = parser.parse_args()
	#print(args)
	
	try:
		if args.start_delay > 0:
			for i in range(args.start_delay, 0, -1):
				print('Starting in', i, 'minutes...', end='')
				sys.stdout.flush()
				time.sleep(60)
				print('\r', end='')
			print()
	
		while True:
			
			if os.system('wmctrl -a FreeBitco.in'):						#check if it's open
				os.system('firefox --new-window https://freebitco.in &')
				print('Opening browser...')
				while os.system('wmctrl -a FreeBitco.in'):
					time.sleep(2)
			else:
				print('Browser already opened')
			
			print('Waiting for page to load...')
			time.sleep(args.captcha_delay)

			output = subprocess.run('wmctrl -l | grep FreeBitco.in', shell=True,
									stdout=subprocess.PIPE).stdout.decode('utf-8')
			title = output.split()[3]
			
			if title == 'FreeBitco.in':						#if its ready to roll
				pyautogui.press('end')
				
				if args.method == 'fixed':
					
					print('Attempting to click on captcha at ', captchaPos)
					pyautogui.moveTo(captchaPos)
					time.sleep(1)
					pyautogui.click()
					print('Waiting for captcha to solve...')
					time.sleep(args.captcha_delay)
					
					print('Attempting to click on roll at', rollPos)
					pyautogui.moveTo(rollPos)
					time.sleep(1)
					pyautogui.click()
					print('Waiting for game to roll...')
					time.sleep(args.captcha_delay//2)
				
				elif (args.method == 'seek') or (args.method == 'seek_first'):
					print('Looking for captcha')
					for i in range(10):
						try:
							captchaPos = pyautogui.locateCenterOnScreen('unsolved.png')
						except TypeError:
							time.sleep(2)
						else:
							break
						
					if not captchaPos:
						print('Could not find captcha')
						pyautogui.press('f5')
						print('Reloading page...')
						continue
					
					print('Unsolved captcha found at', captchaPos)
			
					print('Attempting to click on captcha at ', captchaPos)
					pyautogui.moveTo(captchaPos)
					pyautogui.click()
					#print('Captcha clicked')
					print('Waiting for captcha to solve...')
					time.sleep(args.captcha_delay)
				
					for i in range(10):
						if pyautogui.locateOnScreen('solved.png'):
							break
						time.sleep(2)
					if not pyautogui.locateOnScreen('solved.png'):
						print('Could not find solved captcha')
						pyautogui.press('f5')
						print('Reloading page...')
						continue
				
					print('Captcha solved')

					print('Looking for roll button')
					try:
						rollPos = pyautogui.locateCenterOnScreen('roll.png')
					except TypeError:
						print('Could not find roll button')
						rollPos = (captchaPos[0]+120, captchaPos[1]+95)
						print('Roll button estimated at', rollPos)
					else:
						print('Roll button found at', rollPos)
					
					
					print('Attempting to click on roll at ', rollPos)
					pyautogui.moveTo(rollPos)
					pyautogui.click()
					#print('Roll clicked')
				
				elif args.method == 'set_first':
					
					print('Setting up Captcha position...')
					sys.stdout.flush()
					for i in range(10, 0, -1):
						current = pyautogui.position()
						print('Current position', current, '(%d sec)'%(i), end='')
						sys.stdout.flush()
						time.sleep(1)
						print('\r', end='')
					print()
					
					captchaPos = pyautogui.position()
					print('Captcha position set at', captchaPos)
					
					print('Setting up Roll position...')
					sys.stdout.flush()
					for i in range(10, 0, -1):
						current = pyautogui.position()
						print('Current position', current, '(%d sec)'%(i), end='')
						sys.stdout.flush()
						time.sleep(1)
						print('\r', end='')
					print()
					
					rollPos = pyautogui.position()
					print('Roll position set at', rollPos)
					
					
				time.sleep(args.captcha_delay)
				output = subprocess.run('wmctrl -l | grep FreeBitco.in', shell=True,
									stdout=subprocess.PIPE).stdout.decode('utf-8')
				title = output.split()[3]
				
				if (title != 'FreeBitco.in'):
					if (args.method == 'seek_first') or (args.method == 'set_first'):
						args.method = 'fixed'
					print('Game rolled on %s\n'%(time.asctime()))
					pyautogui.keyDown('altleft'); pyautogui.press('tab'); pyautogui.keyUp('altleft')
				else:
					print('Failed to roll game')
					pyautogui.press('f5')
					print('Reloading page...')
					
			
			else:															#not ready to roll
				wait = int(title.split('m')[0]) + 1
				print('Waiting for next roll...')
				for i in range(wait, 0, -1):
					print(i, 'minutes remaining ', end='')
					sys.stdout.flush()
					time.sleep(60)
					print('\r', end='')
				print()
				pyautogui.press('enter')
				time.sleep(2)
				pyautogui.press('enter')
				


	except KeyboardInterrupt:
		print ('\nScript ended by user!')
