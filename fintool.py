import os
import tkinter as tk
import requests
import datetime
from bs4 import BeautifulSoup


class Program:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    stockCount = 0
    notifCount = 0
    labels = []
    stocks = []
    notifedStocks = []
    notifs = []
    textVars = []
    session = requests.Session()
    tillClose, marketClosed, window, input, entry = None

    def updateTillClose(self):
        now = datetime.datetime.utcnow()
        tty = 19 - now.hour

        if now.hour >= 19 or now.hour <= 12 or (now.hour <= 12 and now.minute < 30):
            self.tillClose = "market closed"
            self.marketClosed = True

        elif tty == 1:
            self.tillClose = f"market closes in 1 hour"
            self.marketClosed = False

        else:
            self.tillClose = f"market closes in {tty} hours"
            self.marketClosed = False
            

    def notify(self, ticker: str, dir: bool):
        notif = tk.Label(self.window, text = " ", font = "Helvetica 15")
        notif.grid(column = 1, row = self.notifCount)
        os.system("afplay /System/Library/Sounds/Submarine.aiff")

        if dir == True:
            notif.config(text=f"{ticker} has moved upward by 5% since market open! [{datetime.datetime.now()}]")

        else:
            notif.config(text=f"{ticker} has moved downward by 5% since market open! [{datetime.datetime.now()}]")

        self.notifs.append(notif)
        self.notifCount += 1

    def clearNotifs(self):
        for notif in self.notifs:
            notif.destroy()

        self.notifCount = 0

    def getPrice(self, ticker: str) -> str:
        url = f"https://finance.yahoo.com/quote/{ticker}/"
        page = self.session.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'})
        proc = BeautifulSoup(page.text, "html.parser")
        class_ = "My(6px) Pos(r) smartphone_Mt(6px) W(100%)"
        return proc.find("div", class_ = class_).find("fin-streamer").text

    def getChange(self, ticker: str) -> str:
        url = f"https://finance.yahoo.com/quote/{ticker}/"
        page = self.session.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'})
        proc = BeautifulSoup(page.text, "html.parser")
        class_ = "My(6px) Pos(r) smartphone_Mt(6px) W(100%)"
        return proc.find("div", class_ = class_).find("span").text

    def submitAddStock(self):
        ticker = self.entry.get()
        self.input.grab_release()
        self.input.destroy()
        self.addStock(ticker)

    def addStock(self, ticker: str):
        if requests.get(f"https://finance.yahoo.com/quote/{ticker}/").status_code == 404:
            errorWindow = tk.Toplevel(master= self.window)
            errorWindow.title("Do better.")
            tk.Label(errorWindow, text = "Invalid Ticker, buddy.", font="Helvetica 15").pack()
            tk.Button(errorWindow, text = "Okay. I'm really sorry.", command = lambda : errorWindow.destroy()).pack()
            return 0
        
        self.addstkbutton.grid(column = 0, row = 1 + self.stockCount)
        newtext = tk.StringVar()
        newtext.set(f"{ticker} = {self.getPrice(ticker)} ({self.getChange(ticker)})")
        self.textVars.append(newtext)
        newlabel = tk.Label(textvariable= self.textVars[self.stockCount], font='Helvetica 15').grid(column = 0, row = self.stockCount)
        self.labels.append(newlabel)
        self.stocks.append(ticker)
        self.stockCount += 1
        mem = open("memory.txt", 'w')
        tomp = ""

        for stock in self.stocks:
            tomp += f"{stock} "

        self.blah = str.encode(tomp)
        mem.write(tomp)

    def addStockClick(self):
        input = tk.Toplevel(master= self.window)
        input.grab_current()
        input.focus_force()
        entry = tk.Entry(input, bd = 10)
        entry.pack()
        self.submit = tk.Button(input, text = "Submit", command = self.submitAddStock).pack()

    def checkMovement(self, ticker: str):
        if self.marketClosed == True:
            self.notifedStocks = []
            return 0
        
        for note in self.notifedStocks:
            if note == ticker:
                return 0
            
        percent = 100*(float(self.getChange(ticker)) / (float(self.getPrice(ticker)) - float(self.getChange(ticker))))

        if percent > 5:
            self.notify(ticker, 1)
            self.notifedStocks.append(ticker)
            return 0
        
        if percent < -5:
            self.notify(ticker, 0)
            self.notifedStocks.append(ticker)
            return 0

    def refresh(self):
        if self.marketClosed == True:
            self.window.after(10000, self.refresh)
            return 0
        
        counter = 0

        for text in self.textVars:
            text.set(f"{self.stocks[counter]} = {self.getPrice(self.stocks[counter])} ({self.getChange(self.stocks[counter])})")
            print(self.getPrice(self.stocks[counter]))
            counter += 1

        self.updateTillClose()

        for stock in self.stocks:
            self.checkMovement(stock)

        self.window.after(10000, self.refresh)

    def run(self):
        self.window = tk.Tk()
        self.window.title(f"stock thing ({self.tillClose})")
        self.window.geometry("900x600")
        self.updateTillClose(self)
        self.input = tk.Toplevel(master= self.window)
        self.entry = tk.Entry(input, bd = 10)

        addStockButton = tk.Button(self.window, text = "Add Stock", command = self.addStockClick, font='Helvetica 15')
        addStockButton.grid(column = 0, row = 1)
        clearNotifButton = tk.Button(self.window, text = "Clear Notifications", command = self.clearNotifs, font = "Helvetica 15")
        clearNotifButton.grid(column = 2, row = 0)
        mem = open("memory.txt", "r")
        decMem = mem.read()

        for stock in decMem.split():
            self.addStock(stock)

        self.window.after(10000, self.refresh)
        self.window.mainloop()

def main():
    program = Program()
    program.run()
    

if __name__ == "__main__":
    main()