import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Optional argument, if not specified will search path.
driver = webdriver.Chrome('./chromedriver')
driver.get('https://www.courtauction.go.kr/')

time.sleep(3)

driver.switch_to.frame(0)
driver.find_element(By.LINK_TEXT, "아파트").click()

time.sleep(3)

# store window
winHandleBefore = driver.getWindowHandle()

driver.find_element(
    By.CSS_SELECTOR, ".Ltbl_list_lvl0:nth-child(17) > .txtleft a:nth-child(1)").click()
