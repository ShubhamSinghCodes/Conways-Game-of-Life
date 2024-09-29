#!/usr/bin/env python3
from ctypes import windll, Structure, c_long, byref
import pygame
import sys
from pygame.locals import *
import tkinter
import json
import zlib
import keyboard


def init():
    global states, temp, h, w, cache, filepath
    filepath = ""
    try:
        filepath = sys.argv[1]
        filepath = filepath.split('\\')[-1].split('.')[0]
    except:
        filepath = input("Enter filepath: ")
    if filepath:
        with open(filepath + ".txt", encoding='utf-8') as file:
            f = file.readlines()
            f = "".join([line for line in f if not line.startswith('!')]).replace("$", "\n").split("\n")
            temp = [item.strip().replace("o", "1").replace(".", "0").replace("O", "1").replace(".", "0").replace("o",
                                                                                                                 "1").replace(
                "*", "1").replace(".", "0") for item in f]
            h = len(temp)
            w = max([len(s) for s in temp])

            def pad(it, wid):
                return str(it) + ('0' * (wid - len(str(it))))

            temp = [pad(s, w) for s in temp]
        try:
            with open(filepath + ".cgolcache", "rb") as cachefile:
                cache = json.loads(zlib.decompress(cachefile.read()))
        except:
            quit()
    else:
        quit()


init()
prevstates = []


class life:
    def __init__(self, x, y, s=" "):
        self.x = x
        self.y = y
        self.state = int(0 if s == " " else s)
        self.statec = self.state

    def disp(self):
        return self.state


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
        data = [[life(rj, ri, seed[ri][rj]) for rj in range(w)] for ri in range(h)]
    except IndexError:
        data = [[life(rj, ri) for rj in range(w)] for ri in range(h)]


def display():
    [[displaydata[i][j].set(px.disp()) for j, px in enumerate(py)] for i, py in enumerate(data)]
    [quit() for event in pygame.event.get() if event.type == QUIT]
    pygame.display.update()


def runall():
    global usecache, cache
    states = "".join(["".join([str(x.state) for x in y]) for y in data])

    def setstates(states):
        def setstate(x, state):
            x.state = state

        [[setstate(x, states[r][c]) for c, x in enumerate(y)] for r, y in enumerate(data)]

    setstates(cache[states])


def runallb():
    global usecache, cache, prevstates
    states = "".join(["".join([str(x.state) for x in y]) for y in data])

    def setstates(states):
        def setstate(x, state):
            x.state = state

        [[setstate(x, states[r][c]) for c, x in enumerate(y)] for r, y in enumerate(data)]

    try:
        setstates(prevstates.pop(-1))
    except IndexError:
        pass


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
store = list(str(val.state) for row in data for val in row)
getval = lambda d: list(str(val.state) for row in d for val in row)
initdisplay()


def rundispf():
    global prevstates
    display()
    runall()
    prevstates.append([[x.state for x in y] for y in data])


def rundispb():
    display()
    runallb()

keyboard.add_hotkey('right', rundispf)
keyboard.add_hotkey('left', rundispb)
rundispf()
while True:
    [quit() for event in pygame.event.get() if event.type == QUIT]
    pygame.display.update()
