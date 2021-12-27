from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup as bs

def get_clean_name(name,sport):
    """
    Get a translation of team or player name based on a Google search of that name
    :param name: word to search on Google
    :return: tuple (english_name,player/team)
    """
    options = Options()
    options.headless = False
    options.incognito = True
    browser = Firefox(options=options)

    name = name.replace(" ",'+')
    browser.get(f'https://www.google.com/search?q={name}+{sport}')

    soup = bs(browser.page_source, features="lxml")

    browser.close()
    entry = soup.find("span", class_ = 'tsp-ht') # class for player
    if entry == None:
        try:
            entry = soup.find("div", class_ = 'ofy7ae') # class for team
            return entry.text, "team"
        except:
            try:        # wikipedia search
                entry = soup.find("h2", class_ = 'kno-ecr-pt')
                return entry.text, "wiki"

            except:
                pass
            return None, None

    else:
        return entry.text, "player"


    return None, None