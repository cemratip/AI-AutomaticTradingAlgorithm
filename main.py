from skimage import metrics
import matplotlib.pyplot as plt
import numpy as np
import cv2
import sys
import requests
import urllib.request as ur
from PIL import Image, ImageDraw
import random
import bravado
import bitmex
import lxml
import html5lib
import requests
import ccxt
from bitmex import bitmex
from bitmex_websocket import BitMEXWebsocket
from bs4 import BeautifulSoup
import time
import re
import json
import math
import time
import keyboard
from pynput.keyboard import Key, Listener


def getdata():
    global open, close, high, low
    recenttrades = ("https://testnet.bitmex.com/api/v1/trade/bucketed?binSize={}&partial=true&symbol={}&count={}&reverse=true").format('1m', 'XBTUSD', '1')
    r = requests.get(recenttrades)
    soup = BeautifulSoup(r.text, 'html.parser')
    response = ur.urlopen(recenttrades)
    data = json.loads(response.read())
    open = data[0]["open"]
    close = data[0]["close"]
    high = data[0]["high"]
    low = data[0]["low"]
    return open, close, high, low

def compare_images(imageA, imageB):
    global s
    s = metrics.structural_similarity(imageA, imageB)
    return s

def drawcandle():
    im = Image.new('RGB', (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    draw.line((0, openlevel, 100, openlevel), (0, 0, 0), 2)
    draw.line((0, closelevel, 100, closelevel), (0, 0, 0), 2)
    im.save('compare.png')

pair = str(input("Enter pair: ")).upper()

timeframeselect = str(input('''
Please select timeframe to trade in:
1. 1 minute
2. 5 minute
3. 1 hour
4. 1 day

'''))

if timeframeselect == '1':
    timeframe = '1m'
elif timeframeselect == '2':
    timeframe = '5m'
elif timeframeselect == '3':
    timeframe = '1h'
elif timeframeselect == '4':
    timeframe = '1d'

apikey = ""
secretapikey = ""
period = 14
percentage = 5
mult = 0
history = []
break_program = False


#login

def login():
    global ws
    global client
    global apikey
    global secretapikey
    global pair

    choice = str(input('''
Login:
1. Enter Login Details
2. Remember Previous Login Details
3. Exit

'''))
    if choice == '1':
        apikey = str(input("Enter your API Key: "))
        secretapikey = str(input("Enter your Secret API Key: "))
        ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=pair, api_key=apikey, api_secret=secretapikey)
        client = bitmex(test=True, api_key=apikey, api_secret=secretapikey)
        print('Login Successful \n')

        mainmenu()

    elif choice == '2':
        apikey = '1Bk8AeOWOjO2DCUjFSOFQK11'
        secretapikey = 'crGr--X10duyKqUKKtfgfS5E0FrgsF2jz439eSrHjlkVMgS3'
        connect()
        mainmenu()

    elif choice == '3':
        exit()


def connect():
    global ws
    global client
    print("\nConnecting to BitMex servers...")
    ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=pair, api_key=apikey, api_secret=secretapikey)
    client = bitmex(test=True, api_key=apikey, api_secret=secretapikey)
    print("Connection Established \n")


#logout

def logout():
    global logout
    logout = requests.get('https://testnet.bitmex.com/api/v1/user/logout')
    print('\nLogout Successful \n')
    login()


# main menu

def mainmenu():
    global break_program
    choice  = input('''
Main Menu:
1. Start Bot
2. View Balance
3. View Trading History
4. Capital Proportion
5. Logout
   
''')
    if choice == '1':
       break_program = False
       startbot()
    elif choice == '2':
       printviewbalance()
    elif choice == '3':
       viewtradinghistory()
    elif choice == '4':
       capitalproportion()
    elif choice == '5':
       logout()
       login()


def capitalproportion():
    percentage = 5
    print(('Capital proportion set to {}%.').format(percentage))
    choice = input('''Would you like to change this proportion?
1. Yes
2. No
''')
    if choice == '1':
        percentage = float(input('Enter % of capital to allocate per trade: '))
    elif choice == '2':
        mainmenu()



def startbot():
    global break_program
    def on_press(key):
        global break_program
        if key == Key.shift:
            break_program = True
            mainmenu()

    with Listener(on_press=on_press) as listener:
        while break_program == False:
            global period
            global timeframe
            global pair
            determine()

        listener.join()



def determine():
    global sellcounter, buycounter, mult, openlevel, closelevel, candlecolour
    candlecolour = ''
    getdata()
    time.sleep(10) #to prevent request overload
    if high == low:
        determine()
    else:
        openlevel = ((open-low)/(high-low))*100
        closelevel = ((close-low)/(high-low))*100
        if open < close:
            candlecolour = 'green'
        elif open > close:
            candlecolour = 'red'
        drawcandle()

    original = cv2.imread("builtin.png")
    contrast = cv2.imread("compare.png")

    # convert the images to grayscale
    original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)

    compare_images(original, contrast)
    if s > 0.7 and candlecolour == 'green':
        mult = 1
        placeorder()
    elif s > 0.7 and candlecolour == 'red':
        mult = -1
        placeorder()


def startbot():
    global capitalproportion
    global percentage
    global period
    global timeframe
    global pair

    break_program = False
    def on_press(key):
        global break_program
        if key == Key.shift:
            break_program = True
            mainmenu()
    with Listener(on_press=on_press) as listener:
        while break_program == False:
            global capitalproportion
            global percentage
            global period
            global timeframe
            global pair

            print("\nBot Running\n")
            print("Press Shift to Stop Bot\n")

            capitalproportion = (percentage/100) * (returnviewbalance()*marketprice())
            determine()

            time.sleep(1)
        listener.join()



def printviewbalance():
    global balance
    #ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=pair, api_key=apikey, api_secret=secretapikey)
    funds = dict(ws.funds())
    balance = float(funds['amount'] / 100000000)
    print('\nAvailable Balance: ', balance/100000000, 'BTC')
    choice = str(input("\n3. Back\n"))
    if choice == '3':
        mainmenu()

def returnviewbalance():
    global returnbalance
    #ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=pair, api_key=apikey, api_secret=secretapikey)
    returnfunds = dict(ws.funds())
    returnbalance = float(returnfunds['amount'] / 100000000)
    return returnbalance



# view trading history

def viewtradinghistory():
    if len(history) == 0 or None:
        print("No Order History Available")
        goback = str(input("\n3. Back\n"))
        if goback == '3':
            mainmenu()
    else:
        choice = str(input('''
Display Orders By:
1. Newest Trades First
2. Oldest Trades First
3. Back

'''))
        if choice == '1':
            for x in history[::-1]:
                print(x)
            newback = str(input("\n3. Back\n"))
            if newback == '3':
                mainmenu()

        elif choice == '2':
            for x in history:
                print(x)
            oldback = str(input("\n3. Back\n"))
            if oldback == '3':
                mainmenu()

        elif choice == '3':
            mainmenu()



# get market price

def marketprice():
    data = dict(ws.get_instrument())
    marketprice = data['lastPrice']
    return marketprice



# place order

def placeorder():
    global mult, order, buydatamsg, selldatamsg, history, ws, client
    price = marketprice()
    logtime = time.ctime(time.time())
    order = client.Order.Order_new(symbol=pair, orderQty=capitalproportion*mult, price=price).result()
    if capitalproportion*mult > 0:
        buymsg = 'Buy Order Executed'
        print(buymsg)
        buydatamsg = ('{}: Bought {} contract(s) of {} at {}').format(str(logtime), str(capitalproportion), pair, str(price))
        history.append(buydatamsg)
        print(buydatamsg)
    elif capitalproportion*mult < 0:
        sellmsg = 'Sell Order Executed'
        print(sellmsg)
        selldatamsg = ('{}: Sold {} contract(s) of {} at {}').format(str(logtime), str(capitalproportion), pair, str(price))
        history.append(selldatamsg)
        print(selldatamsg)

    time.sleep(60) #waits 1 minute to prevent overload of requests
    determine()

login()
