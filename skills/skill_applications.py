import platform
import subprocess

import psutil

from skills import RegisterSkill, skill
import pyautogui
import pyperclip as pc
from os import system

@skill(r"^(open|launch)[\s]+(.+)")
def LaunchApplication(phrase, match):
    if platform.system().lower() == 'darwin':
        system('open -a {}.app'.format(match[0][1]))
    else:
        pyautogui.hotkey('win', 's')
        pc.copy(match[0][1])
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")
@skill(r"^(close|exit)[\s]+(.+)")
def CloseApplication(phrase, match):
    system(f'taskkill /F /FI "WindowTitle eq {match[0][1]}" /T')

