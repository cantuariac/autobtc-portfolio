
#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-

import pytesseract
from pynput import keyboard, mouse

from PIL import ImageGrab, ImageOps

first_press = True
mouse_ctrl = mouse.Controller()

def read(box):
  img = ImageGrab.grab(bbox=box)
  img.show()
  
  text = pytesseract.image_to_string(img)
  print(text, type(text))

def on_press(key):
  pass

def on_release(key):
    # print(key, dir(key))
    if key == keyboard.Key.f8:
      if first_press:
        left, upper = mouse_ctrl.position
        first_press = False
        print('First point (%d, %d)'%(left, upper))
      else:
        right, botton = mouse_ctrl.position
        first_press = True
        print('Second point (%d, %d)'%(right, botton))
        read((left, upper, right, botton))
    elif key == keyboard.Key.esc:
        # Stop listener
        return False

if __name__ == '__main__':

  # with keyboard.Listener(
  #       on_press=on_press,
  #       on_release=on_release) as listener:
  #   listener.join()

  balance_box = (1760, 100, 1850, 120)
  img = ImageGrab.grab(bbox=balance_box)
  # img.show()
  img = ImageOps.invert(img)
  text = pytesseract.image_to_string(img)
  print(text)
  balance = float(text)

  btcwin_box = (1237, 710, 1330, 728)
  img = ImageGrab.grab(bbox=btcwin_box)
  img = ImageOps.grayscale(img)
  # img = img.quantize(2)
  # img.show()
  # img = ImageOps.invert(img)
  text = pytesseract.image_to_string(img)
  print(text)
  btcwin = float(text)

  rpwin_box = (1570, 710, 1604, 728)
  img = ImageGrab.grab(bbox=rpwin_box)
  img = ImageOps.grayscale(img)
  img = ImageOps.autocontrast(img)
  img.show()
  # img = ImageOps.invert(img)
  text = pytesseract.image_to_string(img)
  print(len(text))
  rpwin = int(str(text))



  print(balance, btcwin, rpwin)