from core.skills import Skill
import webbrowser


@Skill("skill_web_search")
async def SearchWeb(phrase, entities):
    new = 2  # not really necessary, may be default on most modern browsers
    final_url = "https://www.google.com/search?q={}".format(entities['web_search'])
    webbrowser.open(final_url, new=new)

    
