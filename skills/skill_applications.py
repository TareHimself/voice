import psutil

from skills import RegisterSkill, skill
import pyautogui
import pyperclip as pc
from os import system

@skill(r"^(open|launch)[\s]+(.+)")
def LaunchApplication(phrase, match):
    print(match[0][1])
    pyautogui.hotkey('win', 's')
    pc.copy(match[0][1])
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press("enter")
@skill(r"^(close|exit)[\s]+(.+)")
def CloseApplication(phrase, match):
    system(f'taskkill /F /FI "WindowTitle eq {match[0][1]}" /T')

