from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup as bs
import time

def get_all_links(url):
    options = Options()
    options.headless = False
    options.incognito = True
    driver = Firefox(options=options)
    driver.get(url)


    recentList = driver.find_elements_by_xpath("//div[@class='simplebar-scrollbar']")
    time.sleep(3)
    for list in recentList :
        driver.execute_script("window.scrollBy(0, 1000)")
    # should be hockey hope it doesnt change https://tipkurz.etipos.sk/#/zapasy/14920?categoryId=14920
    time.sleep(5)

get_all_links("https://tipkurz.etipos.sk/#/zapasy/14888?categoryId=14888")