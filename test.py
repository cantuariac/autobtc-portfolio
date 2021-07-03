#!/usr/bin/python3
# -*- coding: utf-8 -*-

def boxit(text: str):
    out = ' '+'\N{Combining Overline}\N{Combining Low Line}'
    out = out + ' '+'\N{Combining Overline}\N{Combining Low Line}'
    for c in text[:]:
        out = out + c + '\N{Combining Overline}\N{Combining Low Line}'
    return out[:]


if __name__ == '__main__':
  import tabulate

  from colored import fore, back, style, stylize, bg, fg

  coloredTag = lambda txt, color : fg(color)+'▕'+style.RESET+style.BOLD+fore.WHITE+bg(color)+txt+style.RESET+fg(color)+'▎'+style.RESET

  print(tabulate.tabulate([[
                          coloredTag('auto', 'green'), 
                          coloredTag('bonus', 'red')
                          ]]))#, tablefmt='fancy_grid'))

print(fore.RED+'▕'+style.RESET+style.BOLD+back.RED+'auto'+style.RESET+fore.RED+'▎'+style.RESET)