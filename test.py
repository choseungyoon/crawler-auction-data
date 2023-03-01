from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException

import requests
from bs4 import BeautifulSoup
import asyncio


class GetAuctionInfo():

    def setup_method(self, method):
        # 옵션 생성
        options = webdriver.ChromeOptions()

        options.add_argument("--headless")
        # open Browser in maximized mode
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")  # disabling infobars
        options.add_argument("--disable-extensions")  # disabling extensions
        options.add_argument("--no-sandbox")

        # overcome limited resource problems
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome('mac/chromedriver', options=options)
        self.driver.implicitly_wait(3)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    async def update_date(self):

        # Get item need update

        try:
            # Open courtauctuon page
            self.setup_method("")
            url = "http://www.courtauction.go.kr/RetrieveRealEstDetailInqSaList.laf?jiwonNm=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&saNo=20210130002500&_SRCH_SRNID=PNO102014"

            self.driver.get(url)
            self.driver.implicitly_wait(time_to_wait=1000)

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            contents = soup.find(id='contents')

            table_title = contents.find_all('div', {"class": "table_title"})

            print(table_title[0])

            # 사건기본내역
            basicCaseInfo = contents.find('table', {"summary": "사건기본내역 표"})

            # Find all the <link> tags that refer to external stylesheets
            link_tags = soup.find_all(
                'link', rel='stylesheet', href=True)

            # For each <link> tag, fetch the CSS file and add it to the result
            result = ''
            for link_tag in link_tags:
                # Convert the relative URL to an absolute URL
                css_url = urljoin(url, link_tag['href'])
                css_response = requests.get(css_url)
                result += css_response.text

            # Print the result
            print(result)

        except Exception as UpdateException:
            print(UpdateException)

        # close page
        self.teardown_method("")


def updateJob():
    crawler = GetAuctionInfo()
    crawler.setup_method("")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.update_date())
    crawler.teardown_method("")


updateJob()
