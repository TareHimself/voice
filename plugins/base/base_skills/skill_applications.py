import platform
from core.decorators import Skill
import pyautogui
import pyperclip as pc
from os import system

from plugins.base.text_to_speech import TextToSpeech


@Skill(["skill_app_open"], r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def LaunchApplication(e, args):

    if platform.system().lower() == 'darwin':
        system('open -a {}.app'.format(args[0]))
    else:
        pyautogui.hotkey('win', 's')
        pc.copy(args[0])
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")

    TextToSpeech('Launching {}.'.format(args[0]))


@Skill(["skill_app_close"], r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def CloseApplication(e, args):
    system('taskkill /F /FI "WindowTitle eq {}" /T'.format(args[0]))
    TextToSpeech('Closed {}.'.format(args[0]))
