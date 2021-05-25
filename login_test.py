#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import datetime
import requests

url = 'https://freebitco.in/'

data = {
    "__cfduid": "dcb5643d6bc0c7aa32b1af4d74db1e28b1613913239",
    "btc_address": "15qEMUGJLDGBnaax121j97HkuhHvxFuLx5",
    "cookieconsent_dismissed": "yes",
    "csrf_token": "GLLxxHwaWMIg",
    "free_play_sound": "0",
    "have_account": "1",
    "last_bonus": "1613934535777",
    "last_play": "1616194975",
    "login_auth": "ba2d413db29dcb74fcb20eb047896b72a596c7485dff608964a120020da8e367",
    "password": "c5fb1dc905a16340e51332f6ecb1ce361ba7bbf696336d5e91a619d146539236",
    "rp_hist_arr": "[318,198,198,198,198,198,198,212,240,240,244,244,248,248]"
}

session = requests.Session()

r = session.post(url, data=data)

print(r.cookies, r)