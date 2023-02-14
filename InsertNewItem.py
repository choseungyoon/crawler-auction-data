from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from prisma import Prisma

import os
import re
import shutil

import requests
from bs4 import BeautifulSoup

import asyncio
import time
from datetime import datetime, timedelta
from decimal import Decimal
from re import sub

import logging
import logging.handlers

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import dotenv_values

import binascii

# logging
log_update = logging.getLogger('snowdeer_log')
log_update.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] (%(filename)s:%(lineno)d) > %(message)s')

fileHandler = logging.FileHandler('./log/log.txt', encoding='utf-8')
streamHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

log_update.addHandler(fileHandler)
log_update.addHandler(streamHandler)


class GetAuctionInfo():
    API_HOST = 'https://api.cloudflare.com'
    caseNumber = ""
    currentPageIndex = 1

    data = {}

    def setup_method(self, method):
        # 옵션 생성
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
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

    async def selectItemByCaseIndex(self, caseIndex, itemNumber):
        db = Prisma()
        await db.connect()
        items = await db.item.count(
            where={
                'caseIndex': caseIndex,
                'itemNumber': itemNumber
            }
        )
        await db.disconnect()

        if items == 0:
            return True
        else:
            return False

    async def 법원경매정보_물건리스트_가져오기(self):
        itemList = []
        isFirst = True

        table = self.driver.find_elements(
            By.XPATH, "//*[@id='contents']/div[4]/form[1]/table")

        for line in table:
            chks = line.find_elements(By.NAME, "chk")

            for chk in chks:
                inputValue = chk.get_attribute("value").split(',')
                if isFirst == True:
                    firstItem = (inputValue[1], inputValue[2])
                    isFirst = False

                # Duplicated check
                duplicated = await self.selectItemByCaseIndex(inputValue[1], inputValue[2])

                if duplicated == False:
                    print("PASS : ", inputValue[1], " ", inputValue[2])
                else:
                    print("ADD : ", inputValue[1], " ", inputValue[2])

                    # 전체 업데이트
                    if firstItem == (inputValue[1], inputValue[2]):
                        itemList.append(
                            (inputValue[1], inputValue[2], True))
                    else:
                        itemList.append(
                            (inputValue[1], inputValue[2], False))

        return itemList

    def 물건선택(self, item):

        if (item[2] == True):
            # 첫번째 매물
            self.driver.find_element(
                By.CSS_SELECTOR, ".Ltbl_list_lvl0:nth-child(1) > .txtleft a:nth-child(1)").click()
        else:
            # 그외 매물
            self.driver.find_element(
                By.NAME, item[0] + item[1]).click()

    def 다음페이지(self):
        isFinished = False
        while True:
            try:
                pagination = self.driver.find_element(
                    By.CLASS_NAME, "page2")
                pages = pagination.find_elements(By.TAG_NAME, 'a')

                for page in pages:
                    if not page.text:
                        if page.find_element(By.TAG_NAME,
                                             ("img")).get_attribute("alt") == "다음":
                            self.currentPageIndex = self.currentPageIndex + 1
                            page.click()
                            isFinished = True
                            break
                    else:
                        if int(page.text) == self.currentPageIndex+1:
                            self.currentPageIndex = self.currentPageIndex + 1
                            page.click()
                            isFinished = True
                            break

                break
            except Exception as NextPageException:
                print("NextPageException :", NextPageException)

            finally:
                return isFinished

    async def insertItem(self, caseNumber, caseIndex, itemNumber, itemType, initialPrice, minPrice, bidType, saleDate,
                         description, itemLocation, court, caseApplyDate, auctionApplyDate, allocationApplyDate,
                         requestPrice, appraisal, areaOfBuilding, areaOfGround, numOfPass, share, pdfValuation):
        db = Prisma()
        await db.connect()
        item = await db.item.create(
            data={
                'caseNumber': caseNumber,
                'caseIndex': caseIndex,
                'itemNumber': itemNumber,
                'itemType': itemType,
                'initialPrice': initialPrice,
                'minPrice': minPrice,
                'bidType': bidType,
                'saleDate': saleDate,
                'description': description,
                'itemLocation': itemLocation,
                'court': court,
                'caseApplyDate': caseApplyDate,
                'auctionApplyDate': auctionApplyDate,
                'allocationApplyDate': allocationApplyDate,
                'requestPrice': requestPrice,
                'appraisal': appraisal,
                'areaOfBuilding':     areaOfBuilding,
                'areaOfGround': areaOfGround,
                'numOfPass':  numOfPass,
                'share': share,
                'pdfValuation': pdfValuation
            }
        )
        print("Created : ", caseNumber)
        await db.disconnect()

        return item.id

    def 감정평가요양표_요약(self):
        appraisal = ""
        try:
            log_update.debug("감정평가 시작")
            ulOfAppraisal = self.driver.find_element(
                By.XPATH, "//*[@id='contents']/div[7]/table/tbody/tr/td/ul")

            all_li = ulOfAppraisal.find_elements(
                By.TAG_NAME, "li")

            for li in all_li:
                if li.text not in appraisal:
                    appraisal += li.text + "\n"
        except:
            appraisal = "2008년 8월 18일 이전에 감정평가 완료된 물건에 대해서는 본 정보를 제공하지 않습니다.\n감정평가서를 참조하시기 바랍니다."

        return appraisal

    def 목록내역(self):
        try:
            log_update.debug("목록내역 시작")
            estateListTable = self.driver.find_element(
                By.XPATH, "//*[@id='contents']/div[6]/table")

            estateListTbody = estateListTable.find_element(
                By.TAG_NAME, "tbody")

            areaOfGround = 0
            areaOfBuilding = 0
            estateList = []
            estateIdx = 0
            itemLocation = None
            share = False

            for tr in estateListTbody.find_elements(By.TAG_NAME, "tr"):
                tds = tr.find_elements(By.TAG_NAME, "td")

                estateLocation = self.driver.find_element(
                    By.XPATH,
                    "//*[@id='contents']/div[4]/table[1]/tbody/tr[" + str(5 + estateIdx) + "]/td").text.strip()

                estateUsage = ""

                if estateLocation[0] == "(":
                    for usageChar in estateLocation:
                        if usageChar == ")":
                            estateUsage += usageChar
                            estateLocation = estateLocation.replace(
                                estateUsage, "").strip()
                            estateUsage = estateUsage.replace(
                                "(", "").replace(")", "").strip()

                            break
                        else:
                            estateUsage += usageChar
                else:
                    estateUsage = "기타"

                if estateIdx == 0:
                    itemLocation = estateLocation

                estateList.append({
                    "num": int(tds[0].text),
                    "type": tds[1].text,
                    'detail': tds[2].text,
                    "usage": estateUsage,
                    "location": estateLocation}, )

                detailOfList = tds[2].text

                if tds[1].text == "토지":
                    thisGround = float(0)
                    for line in detailOfList.split("\n"):
                        if (line.startswith("주차장") or line.startswith("대") or line.startswith("임야") or line.startswith("구거") or line.startswith("잡종지") or line.startswith("묘지") or line.startswith("도로") or line.startswith("공장용지") or line.startswith("답") or line.startswith("하천") or line.startswith("전")) and line.endswith("㎡"):
                            thisGround = float(re.findall(
                                r'(\d+(?:\.\d+)?)', line)[0])

                        # 지분
                        if "매각지분" in line and "분의" in line:
                            isShare = float(0)
                            if len(re.findall(r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', line)) > 0:
                                for each in re.findall(r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', line):
                                    isShare += float(each[1]) / \
                                        float(each[0])

                                if isShare < 1.0:
                                    share = True
                                    thisGround = thisGround * isShare
                    areaOfGround += thisGround

                elif tds[1].text == "집합건물":
                    thisBuilding = float(0)
                    thisGround = float(0)
                    thisGroundArray = []
                    groundShareIdx = 0

                    for line in detailOfList.split("\n"):
                        line = line.strip()
                        # 건물
                        if "구          조" in line and "㎡" in line:
                            thisBuilding += float(
                                re.findall(r'(\d+(?:\.\d+)?)', line)[0])

                        if "면          적" in line and "㎡" in line:
                            thisBuilding += float(
                                re.findall(r'(\d+(?:\.\d+)?)', line)[0])

                        # 토지
                        # 면적
                        if (line.startswith("학교용지") or line.startswith("주차장") or line.startswith("대") or line.startswith("임야") or line.startswith("구거") or line.startswith("잡종지") or line.startswith("묘지") or line.startswith("도로") or line.startswith("공장용지") or line.startswith("답") or line.startswith("하천") or line.startswith("전")) and (line.endswith("㎡") or line.endswith("평방미터")):
                            thisGroundArray.append(
                                float(re.findall(r'(\d+(?:\.\d+)?)', line)[0]))

                        # 비율
                        if "." in line and "분의" in line and "매각지분" not in line:
                            line = line.replace(",", "")
                            if len(re.findall(r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', line)) > 0:
                                numerator = float(re.findall(
                                    r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', line)[0][0])
                                denominator = float(re.findall(
                                    r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', line)[0][1])

                                if len(thisGroundArray) == 0:
                                    if thisGround == 0:
                                        thisGround += denominator
                                else:
                                    thisGroundArray[groundShareIdx] = thisGroundArray[groundShareIdx] * float(
                                        denominator / numerator)
                                    thisGround += thisGroundArray[groundShareIdx]
                                    groundShareIdx = groundShareIdx + 1
                        # 지분
                        if "매각지분" in line and "분의" in line:
                            isShare = float(0)
                            for each in re.findall(r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', line):

                                isShare += float(each[1]) / \
                                    float(each[0])

                            if isShare < 1.0:
                                share = True
                                thisBuilding = thisBuilding * isShare
                                thisGround = thisGround * isShare

                    areaOfBuilding += thisBuilding
                    areaOfGround += thisGround

                elif tds[1].text == "건물":
                    print("건물")

                estateIdx = estateIdx + 1

            return [areaOfGround, areaOfBuilding, estateList, estateIdx, itemLocation, share]

        except Exception as Error_목록내역:
            log_update.error("Error_목록내역")
            log_update.error("Error message : " + Error_목록내역)
            log_update.error("Error line : " + line)

    def Upload_감정평가서_Azure(self, filePath):
        print("감정평가서 Upload to Azure")
        try:
            config = dotenv_values(".env")
            # Define connection string and container name
            connect_str = config["AZURE_CON_STRING"]
            container_name = config["AZURE_CONTAINER_VALUATION"]

            # Create a BlobServiceClient object using the connection string
            blob_service_client = BlobServiceClient.from_connection_string(
                connect_str)

            # Create a ContainerClient object for the container
            container_client = blob_service_client.get_container_client(
                container_name)

            # Define the path to the local file to upload
            local_path = filePath

            # Define the name for the blob in Azure Storage
            blob_name = "감정평가서_" + self.caseNumber + ".pdf"

            # Create a BlobClient object for the blob
            blob_client = container_client.get_blob_client(blob_name)

            # Upload the file to Azure Storage
            with open(local_path, "rb") as data:
                blob_client.upload_blob(data)

            print(blob_client.url)

            return blob_client.url

        except Exception as ex:
            print('Exception:')
            print(ex)
            return "none"

    def 감정평가서_PDF_다운(self):
        print("감정평가서 다운로드")
        fileUrl = "none"
        try:
            self.vars["window_handles"] = self.driver.window_handles
            self.driver.find_element(
                By.XPATH, "//img[@alt='감정평가서 팝업']").click()

            self.vars["win7232"] = self.wait_for_window(2000)
            self.vars["root"] = self.driver.current_window_handle
            self.driver.switch_to.window(self.vars["win7232"])

            filename = 'pdf/valuation.pdf'

            with open(filename, 'wb') as file:
                iframe = self.driver.find_element(
                    By.XPATH, "/html/frameset/frame[2]")
                self.driver.switch_to.frame(iframe)
                pdf_link = self.driver.find_element(By.TAG_NAME, "iframe")

                # write file
                with open(filename, 'wb') as handle:
                    while True:
                        try:
                            headers = {
                                # Github runner
                                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                                # Local
                                # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                            }

                            response = requests.get(
                                pdf_link.get_attribute('src'), stream=True, headers=headers)

                            if response.status_code == 200:
                                break
                        except Exception as e:
                            print(
                                "Error Write file ", e)
                            time.sleep(3)

                    if not response.ok:
                        print(response)

                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)

                fileUrl = self.Upload_감정평가서_Azure(filename)

                # with open(filename, 'rb') as f:
                #     content = f.read()

                # hex = binascii.hexlify(content).decode('utf-8')

                # Delete pdf files
                folder = 'pdf/'
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' %
                              (file_path, e))
        except Exception as PDF_VALUATION_Error:
            log_update.error(PDF_VALUATION_Error)

        finally:
            self.driver.close()
            self.driver.switch_to.window(self.vars["root"])
            self.driver.switch_to.frame(0)

        print("감정평가서 다운로드 완료")

        return fileUrl

    def uploadImageToAzure(self, imgFileName, imageObjects, caseNumber):
        log_update.debug("Upload to Azure storage serivce")
        config = dotenv_values(".env")
        # Define connection string and container name
        connect_str = config["AZURE_CON_STRING"]
        container_name = config["AZURE_CONTAINER_IMAGE"]

        try:
            config = dotenv_values(".env")
            # Define connection string and container name
            connect_str = config["AZURE_CON_STRING"]
            container_name = config["AZURE_CONTAINER_IMAGE"]

            # Create a BlobServiceClient object using the connection string
            blob_service_client = BlobServiceClient.from_connection_string(
                connect_str)

            # Create a ContainerClient object for the container
            container_client = blob_service_client.get_container_client(
                container_name)

            # Define the path to the local file to upload
            local_path = imgFileName

            # Define the name for the blob in Azure Storage
            blob_name = imgFileName.split('/')[1]

            # Create a BlobClient object for the blob
            blob_client = container_client.get_blob_client(blob_name)

            # Upload the file to Azure Storage
            with open(local_path, "rb") as data:
                blob_client.upload_blob(data)

            imageObjects.append(
                {"caseNumber": caseNumber, "imgSrc": blob_client.url, "cloudflareImgId": ""})

            print(blob_client.url)

        except Exception as ex:
            print('Exception:')
            print(ex)

    async def checkImageDuplicated(self):
        db = Prisma()
        await db.connect()

        images = await db.image.count(
            where={
                'caseNumber': self.caseNumber
            }
        )
        await db.disconnect()

        if images == 0:
            return False
        else:
            return True

    async def 기일내역_DB_업데이트(self, resultAuctionObjects, itemId):
        db = Prisma()
        await db.connect()

        await db.resultauction.delete_many(
            where={
                'itemId': itemId
            }
        )
        await db.resultauction.create_many(
            data=resultAuctionObjects
        )
        print("Completed insert result of auction")
        await db.disconnect()

    async def insertLeaseDetail(self, leaseDetails):
        db = Prisma()
        await db.connect()

        await db.leasedetail.create_many(
            data=leaseDetails
        )
        print("Completed insert leaseDetails")
        await db.disconnect()

    async def insertEstateList(self, estateList):
        db = Prisma()
        await db.connect()

        await db.realestatelist.create_many(
            data=estateList
        )
        print("Completed insert estateLists")
        await db.disconnect()

    async def insertLeasePeople(self, leasePeoples):

        db = Prisma()
        await db.connect()

        await db.leasepeople.create_many(
            data=leasePeoples
        )
        print("Completed insert lease peoples")
        await db.disconnect()

    async def insertImage(self, imageObjects):
        db = Prisma()
        await db.connect()
        await db.image.create_many(
            data=imageObjects
        )
        print("Completed insert images")
        await db.disconnect()

    async def 이미지업로드(self):
        try:
            imageDuplicated = await self.checkImageDuplicated()
            if imageDuplicated == True:
                print("PASS : UPLOAD IMAGE")
            else:
                print("START UPLOAD IMAGE")

                # 사진 업로드
                checkImage = self.driver.find_element(
                    By.XPATH, "//*[@id='contents']/div[4]/div[2]/table/tbody/tr/td")

                if checkImage.text == "감정평가서와 현황조사서에 등록된 사진이미지가 없습니다.":
                    print("감정평가서와 현황조사서에 등록된 사진이미지가 없습니다.")
                else:
                    self.vars["window_handles"] = self.driver.window_handles
                    self.driver.find_element(
                        By.CSS_SELECTOR, "#photo0 li:nth-child(1) img").click()
                    self.vars["win1583"] = self.wait_for_window(
                        2000)
                    self.vars["root"] = self.driver.current_window_handle
                    self.driver.switch_to.window(
                        self.vars["win1583"])

                    nameOfImage = self.driver.find_element(
                        By.XPATH, "//*[@id = 'pop_contents_1']/form/div[1]/table/tbody/tr[1]/td[2]").text
                    numOfImg = int(self.driver.find_element(
                        By.XPATH, "//*[@id='pop_contents_1']/form/div[2]/div[2]/div/span").text)

                    imageObjects = []
                    imagePageIndex = 1

                    for i in range(numOfImg):
                        # something
                        # Download image file
                        print('images/' + nameOfImage +
                              "_" + str(i) + ".png")
                        with open('images/' + nameOfImage + "_" + str(i) + ".png", 'wb') as file:
                            # identify image to be captured

                            img = None
                            while True:
                                try:
                                    img = self.driver.find_element(
                                        By.XPATH, "//*[@id='pop_contents_1']/form/div[2]/table/tbody/tr[1]/td/img")
                                    break
                                except Exception as ImgNotFoundError:
                                    print("ImgNotFoundError : ",
                                          ImgNotFoundError)
                                    time.sleep(2)

                            # write file
                            with open('images/' + nameOfImage + '_' + str(i) + '.png', 'wb') as handle:
                                while True:
                                    try:

                                        headers = {
                                            # Github runner
                                            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                                            # Local
                                            # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
                                        }

                                        response = requests.get(
                                            img.get_attribute('src'), stream=True, headers=headers)

                                        if response.status_code == 200:
                                            break
                                    except Exception as e:
                                        print(
                                            "Error Write file ", e)
                                        time.sleep(3)

                                if not response.ok:
                                    print(response)

                                for block in response.iter_content(1024):
                                    if not block:
                                        break
                                    handle.write(block)

                            # Uplocat image to Azure Storage blob
                            self.uploadImageToAzure(
                                'images/' + nameOfImage + "_" + str(i) + ".png", imageObjects, nameOfImage)

                        # nextpage
                        pagination = self.driver.find_element(
                            By.CLASS_NAME, "page2")

                        pages = pagination.find_elements(
                            By.TAG_NAME, 'a')
                        for page in pages:
                            if not page.text:
                                if page.find_element(By.TAG_NAME,
                                                     ("img")).get_attribute("alt") == "다음":
                                    imagePageIndex = imagePageIndex + 1
                                    print("GO TO PAGE : ",
                                          imagePageIndex)
                                    page.click()
                                    break
                            else:
                                if int(page.text) == imagePageIndex+1:
                                    imagePageIndex = imagePageIndex + 1
                                    print("GO TO PAGE : ",
                                          imagePageIndex)
                                    page.click()
                                    break
                    await self.insertImage(imageObjects)

                    # Delete img files
                    folder = 'images/'
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        try:
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            print('Failed to delete %s. Reason: %s' %
                                  (file_path, e))

                    print("사진 업로드 완료")

                    self.driver.close()
                    self.driver.switch_to.window(
                        self.vars["root"])
                    self.driver.switch_to.frame(0)
        except Exception as Error_사진:
            log_update.error("Error_사진")
            log_update.error(Error_사진)

    def 유찰_카운트(self):
        numOfPass = 0
        DetailOfSaleDate = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[5]/table")

        tbody = DetailOfSaleDate.find_element(
            By.TAG_NAME, "tbody")
        for tr in tbody.find_elements(By.TAG_NAME, "tr"):
            tds = tr.find_elements(By.TAG_NAME, "td")
            saleResultRow = tds[4].get_attribute("innerText")
            if "유찰" in saleResultRow:
                numOfPass += 1
        return numOfPass

    async def 기일내역_데이터(self, itemId):
        formatYYYMMDD_HHMM = '%Y.%m.%d (%H:%M)'
        # 기일내역
        arrayResultAuction = []
        numOfPass = 0
        DetailOfSaleDate = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[5]/table")

        tbody = DetailOfSaleDate.find_element(
            By.TAG_NAME, "tbody")
        for tr in tbody.find_elements(By.TAG_NAME, "tr"):
            tds = tr.find_elements(By.TAG_NAME, "td")

            saleDateRow = datetime.strptime(
                tds[0].get_attribute("innerText").strip(), formatYYYMMDD_HHMM)

            saleTypeRow = tds[1].get_attribute("innerText")
            saleLocationRow = tds[2].get_attribute("innerText")
            salePriceRow = tds[3].get_attribute("innerText")
            saleResultRow = tds[4].get_attribute("innerText")
            if "유찰" in saleResultRow:
                numOfPass += 1

            arrayResultAuction.append(
                {"date": saleDateRow, "type": saleTypeRow, 'location': saleLocationRow, 'minSalePrice': salePriceRow, 'result': saleResultRow})

            for result in arrayResultAuction:
                result['itemId'] = itemId

        await self.기일내역_DB_업데이트(arrayResultAuction, itemId)

        print("기일내역 완료")

    async def 현황조사서_데이터(self, itemId):
        log_update.debug("현황조사서 시작")

        try:
            leaseDetails = []
            leasePeoples = []

            self.vars["window_handles"] = self.driver.window_handles
            self.driver.find_element(
                By.XPATH, "//img[@alt='현황조사서 팝업']").click()

            self.vars["win7232"] = self.wait_for_window(2000)
            self.vars["root"] = self.driver.current_window_handle

            self.driver.switch_to.window(self.vars["win7232"])

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            contents = soup.find(id='pop_contents_1')

            부동산의_점유관계_Tables = contents.find_all(
                'table', {"summary": "부동산의 점유관계 표"})

            for 부동산의_점유관계 in 부동산의_점유관계_Tables:

                for tr in 부동산의_점유관계.find_all('tr'):
                    td = tr.find_all('td')
                    # if "소재지" in tr.text:
                    #     itemIndx = td[0].text.split('.')[0]
                    if "기타" in tr.text:
                        leaseDetails.append({"content": td[0].text.strip()})

            임대차_관계_조사서_Tables = contents.find_all(
                'table', {"summary": "임차 목적물의 용도 및 임대차 계약등의 내용 표 "})

            # leaseFlag = False
            # endFlag = False

            for 임대차 in 임대차_관계_조사서_Tables:
                점유인 = ""
                당사자구분 = ""
                점유부분 = ""
                점유기간 = ""
                보증금 = ""
                차임 = ""
                전입일자 = ""
                확정일자 = ""

                for tr in 임대차.find_all('tr'):
                    td = tr.find_all('td')
                    if "점유인" in tr.text:
                        점유인 = td[1].text.strip()
                        당사자구분 = td[2].text.strip()

                    if "점유부분" in tr.text:
                        점유부분 = td[0].text.strip()

                    if "점유기간" in tr.text:
                        점유기간 = td[0].text.strip()

                    if "보증(전세)금" in tr.text:
                        보증금 = td[0].text.strip()
                        차임 = td[1].text.strip()

                    if "전입일자" in tr.text:
                        전입일자 = td[0].text.strip()
                        확정일자 = td[1].text.strip()

                        leasePeoples.append({"leaseName": 점유인, "leaseType": 당사자구분,
                                             'deposit': 보증금, 'transferDate': 전입일자, 'confirmDate': 확정일자,
                                             'occupancy': 점유부분, 'period': 점유기간, 'rent': 차임})
            if len(leaseDetails) > 0:
                for leaseDetailItem in leaseDetails:
                    leaseDetailItem['itemId'] = itemId
                await self.insertLeaseDetail(leaseDetails)
                log_update.debug("임차내용 DB Insert 완료")

            if len(leasePeoples) > 0:
                for leasePeopleItem in leasePeoples:
                    leasePeopleItem['itemId'] = itemId
                await self.insertLeasePeople(leasePeoples)
                log_update.debug("임차인 DB Insert 완료")

        except Exception as Error_현황조사서:
            log_update.error("Error_현황조사서")
            log_update.error(Error_현황조사서)

        finally:
            self.driver.close()
            self.driver.switch_to.window(self.vars["root"])
            self.driver.switch_to.frame(0)

    async def 물건기본정보(self, item):
        formatYYYMMDDHHMM = '%Y.%m.%d %H:%M'
        formatYYYMMDD = '%Y.%m.%d'

        self.caseNumber = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[1]/td[1]").text.split(' ')[0]

        itemNumber = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[1]/td[2]").text

        itemType = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[1]/td[3]")

        initialPrice = Decimal(sub(r'[^\d.]', '', self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[2]/td[1]").text))

        minPrice = Decimal(sub(r'[^\d.]', '', self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[2]/td[2]").text))

        bidType = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[2]/td[3]")

        saleDate = datetime.strptime(
            self.driver.find_element(
                By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[3]/td").text
            [0:16], formatYYYMMDDHHMM)
        description = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[4]/td")

        # 사건접수
        caseApplyDate = datetime.strptime(self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[2]/tbody/tr[1]/td[1]")
            .text, formatYYYMMDD)
        # 경매개시
        auctionApplyDate = datetime.strptime(self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[2]/tbody/tr[1]/td[2]")
            .text, formatYYYMMDD)

        # 배당요구종기
        field = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[2]/tbody/tr[2]/td[1]")
        if not field.text:
            allocationApplyDate = None
        else:
            allocationApplyDate = datetime.strptime(self.driver.find_element(
                By.XPATH, "//*[@id='contents']/div[4]/table[2]/tbody/tr[2]/td[1]").text.split("/")[-1].replace("\n", "").replace("(연기)", "").strip(), formatYYYMMDD)
        requestPrice = Decimal(sub(r'[^\d.]', '', self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[2]/tbody/tr[2]/td[2]").text))

        # 감정평가요양표 요약
        appraisal = self.감정평가요양표_요약()
        목록내역데이터 = self.목록내역()

        court = self.driver.find_element(
            By.XPATH, "//*[@id='contents']/div[4]/table[1]/tbody/tr[" + str(5 + 목록내역데이터[3]) + "]/td").text

        # 유찰 횟수 카운트
        numOfPass = self.유찰_카운트()

        # 감정평가서 다운로드
        pdfValuation = self.감정평가서_PDF_다운()

        itemId = await self.insertItem(self.caseNumber,
                                       item[0],
                                       itemNumber,
                                       itemType.text,
                                       initialPrice,
                                       minPrice,
                                       bidType.text,
                                       saleDate,
                                       description.text,
                                       목록내역데이터[4],
                                       court,
                                       caseApplyDate,
                                       auctionApplyDate,
                                       allocationApplyDate,
                                       requestPrice,
                                       appraisal,
                                       목록내역데이터[1],
                                       목록내역데이터[0],
                                       numOfPass,
                                       목록내역데이터[5],
                                       pdfValuation)
        # 부동산 내역
        if len(목록내역데이터[2]) > 0:
            for estateItem in 목록내역데이터[2]:
                estateItem['itemId'] = itemId
            await self.insertEstateList(목록내역데이터[2])

        return itemId

    async def 물건업데이트(self):

        print("START GET ITEMS")
        while True:
            itemList = await self.법원경매정보_물건리스트_가져오기()

            # 물건 탐색
            for item in itemList:
                try:
                    # 물건 화면으로 접속
                    self.물건선택(item)

                    # 물건기본정보 + 감정평가요양표 요약 + 목록내역 + 감정평가서
                    itemId = await self.물건기본정보(item)

                    # 사진
                    await self.이미지업로드()

                    # 기일내역
                    await self.기일내역_데이터(itemId)

                    # 현황조사서
                    await self.현황조사서_데이터(itemId)

                    # 물건리스트로 돌아가기
                    self.driver.find_element(
                        By.XPATH, "//div[@id='contents']/div[4]/div/div/a[2]/img").click()

                except Exception as Error_물건업데이트:
                    log_update.error(Error_물건업데이트)

            # 다음페이지 넘어가기
            if self.다음페이지() == False:
                break

    async def linkToCourt(self, courtName):

        # 법원 사이트 오픈
        print(courtName)
        self.driver.get("http://www.courtauction.go.kr")
        self.driver.switch_to.frame(0)

        # 해당 법원으로 검색
        dropdown = self.driver.find_element(By.ID, "idJiwonNm1")
        dropdown.find_element(
            By.XPATH, "//option[. = '{}']".format(courtName)).click()
        self.driver.find_element(By.CSS_SELECTOR, "#main_btn img").click()

        # 물건 정보 가져오기
        await self.물건업데이트()

        # 닫기
        self.driver.close()


def crawler():
    courtList = [
        "서울서부지방법원", "서울중앙지방법원", "서울동부지방법원",  "서울남부지방법원", "서울북부지방법원", "의정부지방법원", "고양지원", "남양주지원", "인천지방법원", "부천지원", "수원지방법원",
        "성남지원", "여주지원", "평택지원", "안산지원", "안양지원", "춘천지방법원", "강릉지원", "원주지원", "속초지원", "영월지원", "청주지방법원", "충주지원", "제천지원", "영동지원", "대전지방법원",
        "홍성지원", "논산지원", "천안지원", "공주지원", "서산지원", "대구지방법원", "안동지원", "경주지원", "김천지원", "상주지원", "의성지원", "영덕지원", "포항지원",
        "대구서부지원", "부산지방법원", "부산동부법원", "부산서부법원", "울산지방법원", "창원지방법원", "마산지원", "진주지원", "통영지원", "밀양지원", "거창지원", "광주지방법원", "목포지원",
        "장흥지원", "순천지원", "해남지원", "전주지방법원", "군산지원", "정읍지원", "남원지원", "제주지방법원", ""]

    for court in courtList:
        crawler = GetAuctionInfo()
        crawler.setup_method("")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(crawler.linkToCourt(court))
        crawler.teardown_method("")


crawler()
