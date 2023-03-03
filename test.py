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

        # options.add_argument("--headless")
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

    def 사건내역(self, contents):
        사건내역 = """
      <link rel="stylesheet" type="text/css" href="/common.css">
      <link rel="stylesheet" type="text/css" href="/btn_box.css">
      <link rel="stylesheet" type="text/css" href="/sub.css">
      <link rel="stylesheet" type="text/css" href="/table.css"> """
        사건기본내역 = self.사건기본내역(contents)

        사건내역 += 사건기본내역

        tableContents = contents.find_all(
            'div', {"class": "table_contents"})

        for tableContent in tableContents:
            for a_tag in tableContent.find_all('a'):
                a_tag.extract()
            for img_tag in tableContent.find_all('img'):
                img_tag.extract()
            tableContent = str(tableContent).replace(": 등기기록 열람", '')

            사건내역 += tableContent

        # print(사건내역)

    def 사건기본내역(self, contents):

        사건기본내역 = ""

        table_title = contents.find_all('div', {"class": "table_title"})
        basicCaseInfo = contents.find('table', {"summary": "사건기본내역 표"})

        사건기본내역 += str(table_title[0])
        사건기본내역 += str(basicCaseInfo)

        return 사건기본내역

    def 기일내역(self, contents):
        기일내역 = """
      <link rel="stylesheet" type="text/css" href="/common.css">
      <link rel="stylesheet" type="text/css" href="/btn_box.css">
      <link rel="stylesheet" type="text/css" href="/sub.css">
      <link rel="stylesheet" type="text/css" href="/table.css"> """

        table_title = contents.find_all('div', {"class": "table_title"})
        basicCaseInfo = contents.find('table', {"summary": "기일내역 표"})

        기일내역 += str(table_title[0])

        for a_tag in basicCaseInfo.find_all('a'):
            a_tag.extract()
        for img_tag in basicCaseInfo.find_all('img'):
            img_tag.extract()

        기일내역 += str(basicCaseInfo)

        print(기일내역)
        return 기일내역

    def 문건송달내역(self, contents):

        전체 = """ 
      <link rel="stylesheet" type="text/css" href="/common.css">
      <link rel="stylesheet" type="text/css" href="/btn_box.css">
      <link rel="stylesheet" type="text/css" href="/sub.css">
      <link rel="stylesheet" type="text/css" href="/table.css"> """

        문건내역 = ""
        table_title = contents.find_all('div', {"class": "table_title"})
        basicCaseInfo = contents.find('table', {"summary": "문건처리내역 표"})

        문건내역 += str(table_title[0])
        문건내역 += str(basicCaseInfo)

        송달내역 = ""
        basicCaseInfo = contents.find('table', {"summary": "송달내역 표"})

        송달내역 += str(table_title[1])
        송달내역 += str(basicCaseInfo)

        전체 += 문건내역 + 송달내역

        # print(전체)
        return 전체

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

            # 사건내역
            self.사건내역(contents)

            # 기일내역
            self.driver.find_element(
                By.LINK_TEXT, "기일내역").click()
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            contents = soup.find(id='contents')
            self.기일내역(contents)

            # 물건송달내역
            self.driver.find_element(
                By.LINK_TEXT, "문건/송달내역").click()
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            contents = soup.find(id='contents')

            self.문건송달내역(contents)

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
