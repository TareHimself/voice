import platform
from core.decorators import Skill
import pyautogui
import pyperclip as pc
from os import system
from core.assistant import SkillEvent
from core.logger import log

from plugins.base.text_to_speech import text_to_speech


@Skill(["skill_app_open"], r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def launch_application(e: SkillEvent, args: list):
    if platform.system().lower() == 'darwin':
        system('open -a {}.app'.format(args[0]))
    else:
        pyautogui.hotkey('win', 's')
        pc.copy(args[0])
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press("enter")

    await e.context.handle_response('Launching {}.'.format(args[0]))


@Skill(["skill_app_close"], r"(?:(?:close|open|quit|launch|exit)\s?)?(.*)")
async def close_application(e: SkillEvent, args: list):
    system('taskkill /F /FI "WindowTitle eq {}" /T'.format(args[0]))

    await e.context.handle_response('Closed {}.'.format(args[0]))
