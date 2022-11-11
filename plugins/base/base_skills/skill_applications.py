import platform
from core.decorators import Skill
import pyautogui
import pyperclip as pc
from os import system
from core.assistant import SkillEvent
from core.logger import log

from plugins.base.text_to_speech import TextToSpeech


@Skill(["skill_app_open"], r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def LaunchApplication(e: SkillEvent, args):
    if platform.system().lower() == 'darwin':
        system('open -a {}.app'.format(args[0]))
    else:
        pyautogui.hotkey('win', 's')
        pc.copy(args[0])
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")

    await e.Respond('Launching {}.'.format(args[0]))


@Skill(["skill_app_close"], r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def CloseApplication(e: SkillEvent, args):
    system('taskkill /F /FI "WindowTitle eq {}" /T'.format(args[0]))

    await e.Respond('Closed {}.'.format(args[0]))
