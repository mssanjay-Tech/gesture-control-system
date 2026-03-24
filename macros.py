import os
import ctypes
import time
import webbrowser

_last_trigger_time = 0

def cooldown(seconds=2):
    global _last_trigger_time
    now = time.time()
    if now - _last_trigger_time > seconds:
        _last_trigger_time = now
        return True
    return False

def open_browser():
    if cooldown():
        webbrowser.open("https://www.google.com")

def open_youtube():
    if cooldown():
        webbrowser.open("https://www.youtube.com")

def lock_screen():
    if cooldown():
        ctypes.windll.user32.LockWorkStation()

def open_instagram():
    if cooldown():
        webbrowser.open("https://www.instagram.com")

def open_notepad():
    if cooldown():
        os.system("notepad")

def open_vscode():
    if cooldown():
        os.startfile("C:\\Users\\mssan\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")