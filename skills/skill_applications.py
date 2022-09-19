import psutil

from skills import RegisterSkill
import winapps
import pyautogui
import pyperclip as pc
from windows_tools.installed_software import get_installed_software
from os import system


def LaunchApplication(phrase, match):
    print(match[0][1])
    pyautogui.hotkey('win', 's')
    pc.copy(match[0][1])
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press("enter")

def CloseApplication(phrase, match):
    system(f'taskkill /F /FI "WindowTitle eq {match[0][1]}" /T')


RegisterSkill(LaunchApplication, r"^(open|launch)[\s]+(.+)")

RegisterSkill(CloseApplication, r"^(close|exit)[\s]+(.+)")

