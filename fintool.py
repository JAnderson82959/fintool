import sys
import os
from tempfile import TemporaryDirectory, tempdir
import tkinter as tk
import requests
import datetime
import time
from bs4 import BeautifulSoup

def updateTillClose():
    global tillClose, marketClosed
    now = datetime.datetime.utcnow()
    tty = 19 - now.hour
    if now.hour >= 19 or now.hour <= 12 or (now.hour <= 12 and now.minute < 30):
        tillClose = "market closed"
        marketClosed = True
    elif tty == 1:
        tillClose = f"market closes in 1 hour"
        marketClosed = False
    else:
        tillClose = f"market closes in {tty} hours"
        marketClosed = False

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
TSLA = "TSLA"
wn = tk.Tk()
stocknum = 0
notifnum = 0
labels = []
stocks = []
notifed = []
notifs = []
textvars = []
updateTillClose() 
wn.title(f"stock thing ({tillClose})")
wn.geometry("900x600")
sesh = requests.Session()

def notify(stk: str, dir: bool):
    global notifs, notifnum
    notif = tk.Label(wn, text = " ", font = "Helvetica 15")
    notif.grid(column = 1, row = notifnum)
    os.system("afplay /System/Library/Sounds/Submarine.aiff")
    if dir == True:
        notif.config(text=f"{stk} has moved upward by 5% since market open! [{datetime.datetime.now()}]")
    else:
        notif.config(text=f"{stk} has moved downward by 5% since market open! [{datetime.datetime.now()}]")
    notifs.append(notif)
    notifnum += 1

def clearNotifs():
    global notifs, notifnum
    for notif in notifs:
        notif.destroy()
    notifnum = 0

def getPrice(ticker: str) -> str:
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    page = sesh.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'})
    proc = BeautifulSoup(page.text, "html.parser")
    class_ = "My(6px) Pos(r) smartphone_Mt(6px) W(100%)"
    return proc.find("div", class_ = class_).find("fin-streamer").text

def getChange(ticker: str) -> str:
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    page = sesh.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'})
    proc = BeautifulSoup(page.text, "html.parser")
    class_ = "My(6px) Pos(r) smartphone_Mt(6px) W(100%)"
    return proc.find("div", class_ = class_).find("span").text

def submitaddstk():
    global E1
    global inpu
    stk = E1.get()
    inpu.grab_release()
    inpu.destroy()
    addstk(stk)

def addstk(stk: str):
    if requests.get(f"https://finance.yahoo.com/quote/{stk}/").status_code == 404:
        global errorWin
        errorWin = tk.Toplevel(master= wn)
        errorWin.title("Do better.")
        tk.Label(errorWin, text = "Invalid Ticker, buddy.", font="Helvetica 15").pack()
        tk.Button(errorWin, text = "Okay. I'm really sorry.", command = lambda : errorWin.destroy()).pack()
        return 0
    global stocknum, stocks, textvars
    addstkbutton.grid(column = 0, row = 1 + stocknum)
    newtext = tk.StringVar()
    newtext.set(f"{stk} = {getPrice(stk)} ({getChange(stk)})")
    textvars.append(newtext)
    newlabel = tk.Label(textvariable= textvars[stocknum], font='Helvetica 15').grid(column = 0, row = stocknum)
    labels.append(newlabel)
    stocks.append(stk)
    stocknum += 1
    mem = open("memory.txt", 'w')
    tomp = ""
    for stock in stocks:
        tomp += f"{stock} "
    blah = str.encode(tomp)
    mem.write(tomp)

def addstkclick():
    global inpu
    stk = "temp"
    inpu = tk.Toplevel(master= wn)
    inpu.grab_current()
    inpu.focus_force()
    global E1
    E1 = tk.Entry(inpu, bd = 10)
    E1.pack()
    submit = tk.Button(inpu, text = "Submit", command = submitaddstk).pack()

def checkMovement(ticker: str):
    global notifed
    if marketClosed == True:
        notifed = []
        return 0
    for note in notifed:
        if note == ticker:
            return 0
    percent = 100*(float(getChange(ticker)) / (float(getPrice(ticker)) - float(getChange(ticker))))
    if percent > 5:
        notify(ticker, 1)
        notifed.append(ticker)
        return 0
    if percent < -5:
        notify(ticker, 0)
        notifed.append(ticker)
        return 0

def refresh():
    global textvars, stocks, marketClosed
    if marketClosed == True:
        wn.after(10000, refresh)
        return 0
    counter = 0
    for text in textvars:
        text.set(f"{stocks[counter]} = {getPrice(stocks[counter])} ({getChange(stocks[counter])})")
        print(getPrice(stocks[counter]))
        counter += 1
    updateTillClose()
    for stock in stocks:
        checkMovement(stock)
    wn.after(10000, refresh)

addstkbutton = tk.Button(wn, text = "Add Stock", command = addstkclick, font='Helvetica 15')
addstkbutton.grid(column = 0, row = 1)
clearNotifButton = tk.Button(wn, text = "Clear Notifications", command = clearNotifs, font = "Helvetica 15")
clearNotifButton.grid(column = 2, row = 0)
mem = open("memory.txt", "r")
decMem = mem.read()
for stock in decMem.split():
    addstk(stock)
wn.after(10000, refresh)

wn.mainloop()
