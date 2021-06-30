import serial
from threading import Thread
import playsound
from pynput.keyboard import Key, Controller
import json
import os
import time


keyboard = Controller()


# ====== SETTINGS ======
com_port = "COM5"
cfg = "matrix.json"


try:
    s = serial.Serial(com_port)
except:
    print("Please configure COM port")
    exit()

try:
    file = open(cfg)
    matrix = json.loads(file.read())
    file.close()
except:
    print("Please configure actions with \"NVcoder Stream Deck actions configurator\"")
    exit()

def play_sound(path):
    playsound.playsound(path)

valid_keys = {
    "alt": Key.alt,
    "alt_l": Key.alt_l,
    "alt_r": Key.alt_r,
    "backspace": Key.backspace,
    "caps_lock": Key.caps_lock,
    "cmd": Key.cmd,
    "cmd_l": Key.cmd_l,
    "cmd_r": Key.cmd_r,
    "ctrl": Key.ctrl,
    "ctrl_l": Key.ctrl_l,
    "ctrl_r": Key.ctrl_r,
    "delete": Key.delete,
    "down": Key.down,
    "end": Key.end,
    "enter": Key.enter,
    "esc": Key.esc,
    "f1": Key.f1,
    "f2": Key.f2,
    "f3": Key.f3,
    "f4": Key.f4,
    "f5": Key.f5,
    "f6": Key.f6,
    "f7": Key.f7,
    "f8": Key.f8,
    "f9": Key.f9,
    "f10": Key.f10,
    "f11": Key.f11,
    "f12": Key.f12,
    "f13": Key.f13,
    "f14": Key.f14,
    "f15": Key.f15,
    "f16": Key.f16,
    "f17": Key.f17,
    "f18": Key.f18,
    "f19": Key.f19,
    "f20": Key.f20,
    "home": Key.home,
    "insert": Key.insert,
    "left": Key.left,
    "menu": Key.menu,
    "num_lock": Key.num_lock,
    "page_down": Key.page_down,
    "page_up": Key.page_up,
    "pause": Key.pause,
    "print_screen": Key.print_screen,
    "right": Key.right,
    "scroll_lock": Key.scroll_lock,
    "shift": Key.shift,
    "shift_l": Key.shift_l,
    "shift_r": Key.shift_r,
    "space": Key.space,
    "tab": Key.tab,
    "up": Key.up,
}

def press(key):
    keyboard.press(key)
    time.sleep(0.05)
    keyboard.release(key)

def key(key):
    if key[:1] == ";":
        Thread(target=press, kwargs={"key": valid_keys[key[1:]]})
    else:
        Thread(target=press, kwargs={"key": key})

def combo(combo):
    for key in combo:
        if key[:1] == ";":
            keyboard.press(valid_keys[key[1:]])
        else:
            keyboard.press(key)

    time.sleep(0.05)

    for key in combo:
        if key[:1] == ";":
            keyboard.release(valid_keys[key[1:]])
        else:
            keyboard.release(key)

def exec_cmd(cmd):
    os.system(cmd)

while True:
    res = s.read().decode('UTF-8')
    try:
        if res in matrix:
            if matrix[res]["call"] == "exec_cmd":
                cmd = matrix[res]["params"]["cmd"]
                Thread(target=exec_cmd, kwargs={"cmd": cmd}).start()
            elif matrix[res]["call"] == "playsound":
                path = matrix[res]["params"]["path"]
                Thread(target=play_sound, kwargs={"path": path}).start()
            elif matrix[res]["call"] == "press":
                key_ = matrix[res]["params"]["key"]
                key(key_)
            elif matrix[res]["call"] == "combo":
                seq = matrix[res]["params"]["combo"]
                combo_ = seq.split("|")
                combo(combo_)
            elif matrix[res]["call"] == "type":
                text = matrix[res]["params"]["text"]
                keyboard.type(text)
            elif matrix[res]["call"] == "exec_py":
                try:
                    code = matrix[res]["params"]["def"]
                    exec(code)
                except:
                    pass

    except Exception as e:
        print(f"Error: {e}")