from core.decorators import Skill
import webbrowser


@Skill(["skill_web_search"], r"(?:(?:google|look up|search)\s?)?(.*)")
async def SearchWeb(e, args):
    new = 2  # not really necessary, may be default on most modern browsers
    final_url = "https://www.google.com/search?q={}".format(args[0])
    webbrowser.open(final_url, new=new)
