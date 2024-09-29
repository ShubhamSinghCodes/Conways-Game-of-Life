#!/usr/bin/env python3
import json
import os
import sys
import tkinter
import zlib
from ctypes import windll, Structure, c_long, byref
from functools import reduce
from random import *
from time import sleep as wait

import clipboard
import numpy as np
import pygame
from pygame.locals import *

###### INTERACTIVE DISPLAY #######
import time
import ctypes
from os import system, name
import keyboard
from colorama import Fore, Style
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


def render():
    global menu, pos, torender
    if torender:
        clear()
        print(f"{Style.RESET_ALL}Navigate with arrow keys (up and down arrows to move, right arrow to select.)")
        print(menu["head"])
        for ind, action in enumerate(menu["contents"]):
            if ind == pos:
                print(f"{Fore.BLUE} ->{action}{Fore.RESET}")
            else:
                print(f" ->{action}")


#### INIT #######
global states, temp, h, w, bor, sur, cache, filepath, usecache, save
filepath = ""
save = False
try:
    droppedFile = sys.argv[1]
except IndexError:
    droppedFile = ""
if droppedFile:
    with open(droppedFile, encoding='utf-8') as file:
        f = file.readlines()
        temp = "".join([item.strip() for item in f]).replace("O", "1").replace(".", "0")
        h = len(f)
        w = len(f[0])
else:
    menu = {"head": "Enter filepath:", "contents": ["",*[name for name in os.listdir("seeds/") if name.endswith(".txt")]]}
    pos = 0
    torender = True
    while torender:
        render()
        k = keyboard.read_key()
        if k == "down":
            pos += 1
            pos %= len(menu["contents"])
        elif k == "up":
            pos -= 1
            pos %= len(menu["contents"])
        if k == "right":
            filepath = menu["contents"][pos]
            clear()
            torender = False
        time.sleep(0.1)
    if filepath:
        usecache = not input("Use cache? :").lower().startswith("n")
        filepath = "seeds/" + filepath
        with open(filepath, encoding='utf-8') as file:
            f = file.readlines()
            f = "".join([line for line in f if not line.startswith('!')]).replace("$", "\n").split("\n")
            temp = [
                item.strip().replace("o", "1").replace(".", "0").replace("O", "1").replace(".", "0").replace("o",
                                                                                                             "1").replace(
                    "*", "1").replace(".", "0") for item in f]
            h = len(temp)
            w = max([len(s) for s in temp])

            def pad(it, wid):
                return str(it) + ('0' * (wid - len(str(it))))

            temp = [pad(s, w) for s in temp]
        try:
            if usecache:
                with open(filepath + ".cgolcache", "rb") as cachefile:
                    cache = json.loads(zlib.decompress(cachefile.read()))
            else:
                cache = dict()

        except FileNotFoundError:
            cache = dict()
    else:
        temp = input("Enter a seed: ")
        usecache = not input("Use cache? :").lower().startswith("n")
        h = input("Enter hight: ")
        w = input("Enter width: ")
        h = 100 if h == "" else int(h)
        w = 100 if w == "" else int(w)
        cache = dict()


### INIT over ##########


class Square(pygame.sprite.Sprite):
    def __init__(self, y, x, size):
        super(Square, self).__init__()
        self.surf = pygame.Surface((size, size))
        self.rect = self.surf.get_rect()
        screen.blit(self.surf, (x, y))
        self.x = x
        self.y = y
        self.col = 0

    def set(self, col):
        if self.col != col:
            self.col = col
            self.surf.fill((255 * col, 255 * col, 255 * col))
            screen.blit(self.surf, (self.x, self.y))


def randomize(seed=(" " * h * w)):
    global data
    try:
        data = [[int(seed[ri][rj]) for rj in range(w)] for ri in range(h)]
    except (IndexError, ValueError):
        data = [[int(randint(0, 1)) for _ in range(w)] for _ in range(h)]


def display():
    def savecache():
        global filepath, usecache, save
        if filepath and usecache and save:
            try:
                with open(filepath + ".cgolcache", "wb") as cachefile:
                    cachefile.write(zlib.compress(bytes(str(json.dumps(cache)).encode())))
            except FileNotFoundError:
                with open(filepath + ".cgolcache", "x"):
                    pass
                with open(filepath + ".cgolcache", "wb") as cachefile:
                    cachefile.write(zlib.compress(bytes(str(json.dumps(cache)).encode())))
        quit()

    def copystate():
        states = "\n".join(["".join([str(x) for x in y]) for y in data]).replace('0', '.').replace('1', 'O')
        clipboard.copy(states)

    [[displaydata[i][j].set(int(px)) for j, px in enumerate(py)] for i, py in enumerate(data)]
    events = pygame.event.get()
    [savecache() for event in events if event.type == QUIT]
    [copystate() for event in events if event.type == MOUSEBUTTONDOWN and event.button == BUTTON_RIGHT]
    pygame.display.update()


def runall():
    global usecache, cache, data, save
    states = "".join(["".join([str(x) for x in y]) for y in data])
    try:
        if usecache:
            data = cache[states]
        else:
            raise Exception
    except:
        def change(data):
            neighbors = sum(np.roll(np.roll(data, i, axis=0), j, axis=1) for i in [-1, 0, 1] for j in [-1, 0, 1] if not (i == 0 and j == 0))

            def changeitem(Y, X): return np.logical_or(np.logical_and(X.astype('bool'), (Y == 2)), (Y == 3)).astype('int32')

            return changeitem(neighbors, np.array(data)).tolist()

        data = change(data)
        cache[states] = data
        save = True


def initdisplay():
    global screen, displaydata, w, h
    pygame.init()
    displaydata = []

    def get_display_size():
        root = tkinter.Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        height = root.winfo_screenheight()
        width = root.winfo_screenwidth()
        root.destroy()
        return height, width

    sh, sw = get_display_size()
    sh -= 100
    sizeone = sw / w
    sizetwo = sh / h
    finalsize = min(sizetwo, sizeone)
    screen = pygame.display.set_mode((int(finalsize * w), int(finalsize * h)))
    displaydata = [[Square(finalsize * i, j * finalsize, finalsize + 1) for j, px in enumerate(py)] for i, py in
                   enumerate(data)]

    class RECT(Structure):
        _fields_ = [
            ('left', c_long),
            ('top', c_long),
            ('right', c_long),
            ('bottom', c_long),
        ]

        def width(self):  return self.right - self.left

        def height(self): return self.bottom - self.top

    SetWindowPos = windll.user32.SetWindowPos
    GetWindowRect = windll.user32.GetWindowRect
    rc = RECT()
    GetWindowRect(pygame.display.get_wm_info()['window'], byref(rc))
    SetWindowPos(pygame.display.get_wm_info()['window'], -1, rc.left, rc.top, 0, 0, 0x0001)
    del rc
    print("Init over")


if temp == "":
    randomize()
else:
    randomize(temp)
store = list(str(val) for row in data for val in row)
getval = lambda d: list(str(val) for row in d for val in row)
wt = input("enter wait time: ")
wt = float(wt) if wt != "" else 0
initdisplay()
while True:
    display()
    runall()
    wait(wt)
