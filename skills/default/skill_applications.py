import platform
from core.skills import Skill
import pyautogui
import pyperclip as pc
from os import system


@Skill(["skill_app_open"],r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def LaunchApplication(phrase, args):
    
    if platform.system().lower() == 'darwin':
        system('open -a {}.app'.format(args[0]))
    else:
        pyautogui.hotkey('win', 's')
        pc.copy(args[0])
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")


@Skill(["skill_app_close"],r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def CloseApplication(phrase, args):
    system('taskkill /F /FI "WindowTitle eq {}" /T'.format(args[0]))
