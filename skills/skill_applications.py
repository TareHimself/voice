import platform
from skills import Skill
import pyautogui
import pyperclip as pc
from os import system

from utils import EndCommand


@Skill("skill_app_open")
def LaunchApplication(phrase, keywords):
    if platform.system().lower() == 'darwin':
        system('open -a {}.app'.format(keywords[0]))
    else:
        pyautogui.hotkey('win', 's')
        pc.copy(keywords[0])
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")

    EndCommand()


@Skill("skill_app_close")
def CloseApplication(phrase, keywords):
    system(f'taskkill /F /FI "WindowTitle eq {keywords[0]}" /T')
    EndCommand()
