import platform
from core.skills import Skill
import pyautogui
import pyperclip as pc
from os import system


@Skill("skill_app_open")
async def LaunchApplication(phrase, entities):
    print(entities)
    if platform.system().lower() == 'darwin':
        system('open -a {}.app'.format(entities['app']))
    else:
        pyautogui.hotkey('win', 's')
        pc.copy(entities['app'])
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")


@Skill("skill_app_close")
async def CloseApplication(phrase, entities):
    system('taskkill /F /FI "WindowTitle eq {}" /T'.format(entities['app']))
