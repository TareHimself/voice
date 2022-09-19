from skills import RegisterSkill
import webbrowser


def SearchWeb(phrase, match):
    print(match)
    new = 2  # not really necessary, may be default on most modern browsers
    final_url = "https://www.google.com/search?q=" + match[0][1]
    webbrowser.open(final_url, new=new)


RegisterSkill(SearchWeb, r"^(search for|look up|google)[\s]+(.+)")
