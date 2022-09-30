from skills import Skill
import webbrowser

from utils import TextToSpeech, EndCommand


@Skill("skill_web_search")
def SearchWeb(phrase, keywords):
    TextToSpeech("Any Information you Want To Add?")
    new = 2  # not really necessary, may be default on most modern browsers
    final_url = "https://www.google.com/search?q=" + keywords[0]
    webbrowser.open(final_url, new=new)
    EndCommand()
