import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException

import time
import asyncio
from datetime import datetime, timedelta
import shutil

from prisma import Prisma

import logging
import logging.handlers

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import dotenv_values

# logging
log = logging.getLogger('snowdeer_log')
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] (%(filename)s:%(lineno)d) > %(message)s')

fileHandler = logging.FileHandler(
    './log/log_pdf_download.txt', encoding='utf-8')
streamHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

log.addHandler(fileHandler)
log.addHandler(streamHandler)


class GetSellItemDetail():

    # Get the current date and time
    now = datetime.now()

    # Calculate the date and time 7 days ago
    seven_days_after = now + timedelta(days=7)
    format_string = "%Y.%m.%d"
    download_dir = "downloads"

    def setup_method(self, method):
        # 옵션 생성
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Set the default download directory as a relative path

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        prefs = {
            "download.default_directory": os.path.realpath(self.download_dir)}
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(
            executable_path="linux/chromedriver", chrome_options=chrome_options)

        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def 기일별_매각일정_가져오기(self):
        itemList = []
        # 기일별 매각일정
        table = self.driver.find_element(
            By.XPATH, "//*[@id='content']/div/table")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        trs = tbody.find_elements(By.TAG_NAME, "tr")

        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, "td")
            date_time_convert = datetime.strptime(
                tds[0].text, self.format_string)
            if date_time_convert < self.seven_days_after:
                for a in tds[1].find_elements(By.TAG_NAME, "a"):
                    itemList.append(a.text)
        return itemList

    async def 매각물건명세서_업데이트_확인(self, 사건번호, 물건번호):
        db = Prisma()
        await db.connect()

        items = await db.statementofsale.count(
            where={
                'caseNumber': 사건번호,
                'itemNumber': int(물건번호)
            })

        await db.disconnect()

        if items == 0:
            return True
        else:
            return False

    async def Insert_매각물건명세서_DB(self, 사건번호, 물건번호, src):
        db = Prisma()
        await db.connect()

        await db.statementofsale.create(
            data={
                'caseNumber': 사건번호,
                'itemNumber': int(물건번호),
                'src': src
            })

        await db.disconnect()

    async def DeletePdfFileInDrive(self):
        # Delete pdf files
        folder = 'downloads/'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            except Exception as e:
                log.error('Failed to delete %s. Reason: %s' %
                          (file_path, e))
        log.debug("Completed delete files in downloads folder")

    def Upload_To_Azure(self, caseNumber, itemNumber, fileName, blobName):
        try:
            config = dotenv_values(".env")
            # Define connection string and container name
            connect_str = config["AZURE_CON_STRING"]
            container_name = config["AZURE_CONTAINER_STATEMENTSALE"]

            # Create a BlobServiceClient object using the connection string
            blob_service_client = BlobServiceClient.from_connection_string(
                connect_str, max_block_size=4*1024*1024,  # Note: This is the default value
                max_single_put_size=16*1024*1024)

            # Create a ContainerClient object for the container
            container_client = blob_service_client.get_container_client(
                container_name)

            # Define the path to the local file to upload
            local_path = fileName

            # Define the name for the blob in Azure Storage
            blob_name = blobName

            # Create a BlobClient object for the blob
            blob_client = container_client.get_blob_client(blob_name)

            # Upload the file to Azure Storage
            with open(local_path, "rb") as data:
                blob_client.upload_blob(data)

            log.debug(blob_client.url)

            return blob_client.url

        except Exception as ex:
            log.debug('Exception:')
            log.debug(ex)
            return "none"

    async def 업데이트_매각물건명세서(self, 사건번호, 물건번호, count):

        self.driver.find_element(
            By.CSS_SELECTOR, "li:nth-child(" + str(count) + ") .l_info01").click()

        self.driver.find_element(
            By.LINK_TEXT, "매각물건명세서").click()

        self.driver.find_element(
            By.CSS_SELECTOR, ".btn_mae_down").click()

        while not any(fname.endswith('.pdf') for fname in os.listdir(os.path.realpath(self.download_dir))):
            time.sleep(1)

        # Get Date
        date = str(datetime.now().date())

        fileSrc = self.Upload_To_Azure(
            사건번호, 물건번호, 'downloads/매각물건명세서.pdf',  "매각물건명세서_" + 사건번호 + "_" + 물건번호 + "_" + date + ".pdf")

        if fileSrc != 'none':
            await self.Insert_매각물건명세서_DB(사건번호, 물건번호, fileSrc)

        await self.DeletePdfFileInDrive()

        self.driver.find_element(
            By.CSS_SELECTOR, ".btn_prev > img").click()

    async def openAuction(self, courtName):
        # 모바일 법원 사이트 오픈
        self.driver.get("http://ms.courtauction.go.kr/")
        dropdown = self.driver.find_element(By.ID, "idJiwonNm")
        dropdown.find_element(
            By.XPATH, "//option[. = '{}']".format(courtName)).click()

        self.driver.find_element(By.LINK_TEXT, "물건검색").click()

        # 기일별 매각일정
        itemList = self.기일별_매각일정_가져오기()

        for item in itemList:

            # 경매계 클릭
            self.driver.find_element(By.LINK_TEXT, item).click()

            while True:
                try:
                    ul = self.driver.find_element(
                        By.XPATH, "//*[@id='content']/div/ul")
                    count = 1
                    for li in ul.find_elements(By.TAG_NAME, "li"):

                        사건번호 = self.driver.find_element(
                            By.CSS_SELECTOR, "li:nth-child(" + str(count) + ") .l_info").text.split('|')[0].replace("사건번호 :", "").strip()
                        물건번호 = self.driver.find_element(
                            By.CSS_SELECTOR, "li:nth-child(" + str(count) + ") .l_info").text.split('|')[1].replace("물건번호 :", "").strip()

                        log.debug(사건번호 + " " + 물건번호)

                        isUpdateStatementForSale = await self.매각물건명세서_업데이트_확인(사건번호, 물건번호)

                        if isUpdateStatementForSale == True:
                            log.debug("START 매각물건명세서")
                            await self.업데이트_매각물건명세서(사건번호, 물건번호, count)
                        else:
                            log.debug("PASS 매각물건명세서")

                        count = count + 1
                    # 다음
                    self.driver.find_element(
                        By.CSS_SELECTOR, ".next01").click()

                except NoSuchElementException:
                    break

            # 뒤로가기
            self.driver.find_element(
                By.CSS_SELECTOR, ".btn_prev > img").click()


def crawler():
    courtList = [
        "서울남부지방법원", "서울동부지방법원",  "서울서부지방법원", "서울북부지방법원", "서울중앙지방법원", "인천지방법원", "부천지원", "수원지방법원",
        "여주지원", "안산지원", "안양지원", "춘천지방법원", "강릉지원", "원주지원", "속초지원", "영월지원", "청주지방법원", "충주지원", "제천지원", "영동지원", "대전지방법원",
        "홍성지원", "논산지원", "천안지원", "공주지원", "서산지원", "대구지방법원", "안동지원", "경주지원", "김천지원", "상주지원", "의성지원", "영덕지원", "포항지원",
        "대구서부지원", "부산지방법원", "부산동부법원", "부산서부법원", "울산지방법원", "창원지방법원", "마산지원", "진주지원", "통영지원", "밀양지원", "거창지원", "광주지방법원", "목포지원",
        "장흥지원", "순천지원", "해남지원", "전주지방법원",   "남원지원", "제주지방법원",  "정읍지원", "평택지원", "군산지원", "성남지원", "의정부지방법원", "고양지원", "남양주지원"]
    for court in courtList:
        crawler = GetSellItemDetail()
        crawler.setup_method("")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(crawler.openAuction(court))
        crawler.teardown_method("")


crawler()
