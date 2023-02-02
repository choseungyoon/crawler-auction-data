import requests
from bs4 import BeautifulSoup

cookies = {
    'WMONID': 'MYjt0UvjqpZ',
    'daepyoSidoCd': '',
    'daepyoSiguCd': '',
    'mvmPlaceSidoCd': '',
    'mvmPlaceSiguCd': '',
    'rd1Cd': '',
    'rd2Cd': '',
    'realVowel': '35207_45207',
    'roadPlaceSidoCd': '',
    'roadPlaceSiguCd': '',
    'vowelSel': '35207_45207',
    'page': 'default40',
    'JSESSIONID': 'g7Fa5RDDjUc27pD2dAaTnWlgOi197JlXMN4VQx7FQTBHC2u9bRcfSifM4lGcxbVD.amV1c19kb21haW4vYWlzMg==',
    'toMul': '%BC%AD%BF%EF%B5%BF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20200130001879%2C1%2C20230206%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20190130005926%2C1%2C20230214%2CB%5E%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130004766%2C1%2C20230214%2CB%5E%5E%BC%F6%BF%F8%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130011571%2C1%2C20230208%2CB%5E%BC%AD%BF%EF%BA%CF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130004468%2C1%2C20230207%2CB%5E%5E%BC%BA%B3%B2%C1%F6%BF%F8%2C20210130005180%2C1%2C20230213%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130108187%2C1%2C20230221%2CB%5E%5E%BC%AD%BF%EF%B5%BF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130055910%2C1%2C20230220%2CB',
    'locIdx': '',
    'realJiwonNm': '%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Cookie': 'WMONID=MYjt0UvjqpZ; daepyoSidoCd=; daepyoSiguCd=; mvmPlaceSidoCd=; mvmPlaceSiguCd=; rd1Cd=; rd2Cd=; realVowel=35207_45207; roadPlaceSidoCd=; roadPlaceSiguCd=; vowelSel=35207_45207; page=default40; JSESSIONID=g7Fa5RDDjUc27pD2dAaTnWlgOi197JlXMN4VQx7FQTBHC2u9bRcfSifM4lGcxbVD.amV1c19kb21haW4vYWlzMg==; toMul=%BC%AD%BF%EF%B5%BF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20200130001879%2C1%2C20230206%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20190130005926%2C1%2C20230214%2CB%5E%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130004766%2C1%2C20230214%2CB%5E%5E%BC%F6%BF%F8%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130011571%2C1%2C20230208%2CB%5E%BC%AD%BF%EF%BA%CF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130004468%2C1%2C20230207%2CB%5E%5E%BC%BA%B3%B2%C1%F6%BF%F8%2C20210130005180%2C1%2C20230213%2CB%5E%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130108187%2C1%2C20230221%2CB%5E%5E%BC%AD%BF%EF%B5%BF%BA%CE%C1%F6%B9%E6%B9%FD%BF%F8%2C20210130055910%2C1%2C20230220%2CB; locIdx=; realJiwonNm=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8',
    'Origin': 'http://www.courtauction.go.kr',
    'Referer': 'http://www.courtauction.go.kr/RetrieveRealEstMulDetailList.laf',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36',
}

data = 'page=default40&page=default40&srnID=PNO102000&jiwonNm=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&bubwLocGubun=1&jibhgwanOffMgakPlcGubun=&mvmPlaceSidoCd=&mvmPlaceSiguCd=&roadPlaceSidoCd=&roadPlaceSiguCd=&daepyoSidoCd=&daepyoSiguCd=&daepyoDongCd=&rd1Cd=&rd2Cd=&rd3Rd4Cd=&roadCode=&notifyLoc=1&notifyRealRoad=1&notifyNewLoc=1&mvRealGbncd=1&jiwonNm1=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&jiwonNm2=%BC%AD%BF%EF%C1%DF%BE%D3%C1%F6%B9%E6%B9%FD%BF%F8&mDaepyoSidoCd=&mvDaepyoSidoCd=&mDaepyoSiguCd=&mvDaepyoSiguCd=&realVowel=00000_55203&vowelSel=00000_55203&mDaepyoDongCd=&mvmPlaceDongCd=&_NAVI_CMD=&_NAVI_SRNID=&_SRCH_SRNID=PNO102000&_CUR_CMD=RetrieveMainInfo.laf&_CUR_SRNID=PNO102000&_NEXT_CMD=&_NEXT_SRNID=PNO102002&_PRE_SRNID=PNO102001&_LOGOUT_CHK=&_FORM_YN=Y&PNIPassMsg=%C1%A4%C3%A5%BF%A1+%C0%C7%C7%D8+%C2%F7%B4%DC%B5%C8+%C7%D8%BF%DCIP+%BB%E7%BF%EB%C0%DA%C0%D4%B4%CF%B4%D9.&pageSpec=default40&pageSpec=default40&targetRow=1&lafjOrderBy='

response = requests.post(
    'http://www.courtauction.go.kr/RetrieveRealEstMulDetailList.laf',
    cookies=cookies,
    headers=headers,
    data=data,
    verify=False,
)
soup = BeautifulSoup(response.text, 'html.parser')
contents = soup.find('form', {"name": "frm1"})
print(contents)
