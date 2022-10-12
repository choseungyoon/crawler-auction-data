import requests
from bs4 import BeautifulSoup

cookies = {
    'WMONID': '5NmoI-ASb5L',
    'JSESSIONID': 'wzSLPLLsN1HfU8C5JfrdVB8ozkDLAEkb1qtS58LnS6vsybqSbXw91UiKWRNaIQNq.amV1c19kb21haW4vYWlzMQ==',
    'daepyoSiguCd': '',
    'mvmPlaceSidoCd': '',
    'mvmPlaceSiguCd': '',
    'rd1Cd': '',
    'rd2Cd': '',
    'realVowel': '35207_45207',
    'roadPlaceSidoCd': '',
    'roadPlaceSiguCd': '',
    'vowelSel': '35207_45207',
    'realJiwonNm': '%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8',
    'daepyoSidoCd': '',
    'page': 'default20',
    'toMul': '%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20200130003568%2C1%2C20221018%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20180130010600%2C1%2C20221020%2CB%5E',
    'locIdx': '202001300044311',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    # Requests sorts cookies= alphabetically
    # 'Cookie': 'WMONID=5NmoI-ASb5L; JSESSIONID=wzSLPLLsN1HfU8C5JfrdVB8ozkDLAEkb1qtS58LnS6vsybqSbXw91UiKWRNaIQNq.amV1c19kb21haW4vYWlzMQ==; daepyoSiguCd=; mvmPlaceSidoCd=; mvmPlaceSiguCd=; rd1Cd=; rd2Cd=; realVowel=35207_45207; roadPlaceSidoCd=; roadPlaceSiguCd=; vowelSel=35207_45207; realJiwonNm=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8; daepyoSidoCd=; page=default20; toMul=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20200130003568%2C1%2C20221018%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20180130010600%2C1%2C20221020%2CB%5E; locIdx=202001300044311',
    'Origin': 'https://www.courtauction.go.kr',
    'Referer': 'https://www.courtauction.go.kr/RetrieveRealEstMulDetailList.laf',
    'Sec-Fetch-Dest': 'frame',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

data = 'jiwonNm=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&saNo=20200130004431&maemulSer=1&mokmulSer=&_NAVI_CMD=RetrieveMainInfo.laf%5EInitMulSrch.laf&_NAVI_SRNID=PNO102000%5EPNO102001&_SRCH_SRNID=PNO102001&_CUR_CMD=RetrieveRealEstMulDetailList.laf&_CUR_SRNID=PNO102002&_NEXT_CMD=RetrieveRealEstCarHvyMachineMulDetailInfo.laf&_NEXT_SRNID=PNO102015&_PRE_SRNID=&_LOGOUT_CHK=&_FORM_YN=Y&_C_srnID=PNO102000&_C_jiwonNm=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&_C_bubwLocGubun=1&_C_jibhgwanOffMgakPlcGubun=&_C_mvmPlaceSidoCd=&_C_mvmPlaceSiguCd=&_C_roadPlaceSidoCd=&_C_roadPlaceSiguCd=&_C_daepyoSidoCd=&_C_daepyoSiguCd=&_C_daepyoDongCd=&_C_rd1Cd=&_C_rd2Cd=&_C_rd3Rd4Cd=&_C_roadCode=&_C_notifyLoc=1&_C_notifyRealRoad=1&_C_notifyNewLoc=1&_C_mvRealGbncd=1&_C_jiwonNm1=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&_C_jiwonNm2=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&_C_mDaepyoSidoCd=&_C_mvDaepyoSidoCd=&_C_mDaepyoSiguCd=&_C_mvDaepyoSiguCd=&_C_realVowel=00000_55203&_C_vowelSel=00000_55203&_C_mDaepyoDongCd=&_C_mvmPlaceDongCd='

response = requests.post('https://www.courtauction.go.kr/RetrieveRealEstCarHvyMachineMulDetailInfo.laf',
                         cookies=cookies, headers=headers, data=data)

bs = BeautifulSoup(response.content, "html.parser")

baseInfo = []

# base 1
itemBaseInfo = bs.find('table', attrs={'class': 'Ltbl_dt'})

rows = itemBaseInfo.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    baseInfo.append([ele for ele in cols if ele])  # Get rid of empty values

print(baseInfo)
