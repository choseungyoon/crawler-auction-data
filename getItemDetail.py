from bs4 import BeautifulSoup
import requests

cookies = {
    'WMONID': 'M_dIKjwilSC',
    'JSESSIONID': 'ZaLAdTv6aKP7zMWTPxVoX8xt4NUUzG71OsMQ2zrdx1I3pI04bX5YbcPd231vud21.amV1c19kb21haW4vYWlzMg==',
    'realJiwonNm': '%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8',
    'daepyoSidoCd': '',
    'daepyoSiguCd': '',
    'rd1Cd': '',
    'rd2Cd': '',
    'realVowel': '35207_45207',
    'page': 'default20',
    'toMul': '%BC%AD%BF%EF%B5%BF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130055248%2C1%2C20221024%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130111237%2C1%2C20221026%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130003237%2C1%2C20221026%2CB%5E',
    'locIdx': '202201300537801',
}
# 202201300537801
# 202101300552481
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    # Requests sorts cookies= alphabetically
    # 'Cookie': 'WMONID=M_dIKjwilSC; JSESSIONID=ZaLAdTv6aKP7zMWTPxVoX8xt4NUUzG71OsMQ2zrdx1I3pI04bX5YbcPd231vud21.amV1c19kb21haW4vYWlzMg==; realJiwonNm=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8; daepyoSidoCd=; daepyoSiguCd=; rd1Cd=; rd2Cd=; realVowel=35207_45207; page=default20; toMul=%BC%AD%BF%EF%B5%BF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130055248%2C1%2C20221024%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130111237%2C1%2C20221026%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130003237%2C1%2C20221026%2CB%5E; locIdx=202101300552481',
    'Origin': 'https://www.courtauction.go.kr',
    'Referer': 'https://www.courtauction.go.kr/RetrieveRealEstMulDetailList.laf',
    'Sec-Fetch-Dest': 'frame',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

data = 'jiwonNm=%BC%AD%BF%EF%B5%BF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8&saNo=20210130055248&maemulSer=1&mokmulSer=&_NAVI_CMD=RetrieveMainInfo.laf%5EInitMulSrch.laf&_NAVI_SRNID=PNO102000%5EPNO102001&_SRCH_SRNID=PNO102001&_CUR_CMD=RetrieveRealEstMulDetailList.laf&_CUR_SRNID=PNO102002&_NEXT_CMD=RetrieveRealEstCarHvyMachineMulDetailInfo.laf&_NEXT_SRNID=PNO102015&_PRE_SRNID=&_LOGOUT_CHK=&_FORM_YN=Y&_C_page=default20&_C_srnID=PNO102000&_C_lclsUtilCd=0000802&_C_mclsUtilCd=000080201&_C_sclsUtilCd=00008020104&_C_jiwonNm=&_C_PNIPassMsg=%C1%A4%C3%A5%BF%A1+%C0%C7%C7%D8+%C2%F7%B4%DC%B5%C8+%C7%D8%BF%DCIP+%BB%E7%BF%EB%C0%DA%C0%D4%B4%CF%B4%D9.&_C_pageSpec=default20&_C_targetRow=1&_C_lafjOrderBy=order+by+maeGiil+asc'

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
