import re
from bs4 import BeautifulSoup


def calculateSpace(목록구분, detailOfList):

    areaOfGround = 0
    isShareGround = False

    areaOfBuilding = 0
    isShareBuilding = False

    if 목록구분 == "토지":
        print("토지")
        areaOfGround, isShareGround = calculate_토지_area(detailOfList)
    elif 목록구분 == "집합건물":
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
                    isShareBuilding = True
                    isShareGround = True
                    thisBuilding = thisBuilding * isShare
                    thisGround = thisGround * isShare

        areaOfBuilding += thisBuilding
        areaOfGround += thisGround

    elif 목록구분 == "건물":
        print("건물")
        areaOfGround = calculate_건물_area(detailOfList)

    return areaOfBuilding, isShareBuilding, areaOfGround, isShareGround


def calculate_토지_area(html_td_data):
    # HTML 파싱
    soup = BeautifulSoup(html_td_data, 'html.parser')

    # 면적 추출을 위한 정규표현식 패턴
    area_pattern = re.compile(r'([\d.]+)㎡')

    # 면적 추출을 위한 변수 초기화
    total_area = 0.0
    is_excepted = False

    # HTML에서 모든 텍스트 요소 추출
    for text in soup.stripped_strings:
        # 제외 구간 시작
        if "매각지분" in text and "분의" in text:
            isShare = float(0)
            if len(re.findall(r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', text)) > 0:
                for each in re.findall(r'(\d+(?:\.\d+)?)\s*분의\s*(\d+(?:\.\d+)?)', text):
                    isShare += float(each[1]) / \
                        float(each[0])

                if isShare < 1.0:
                    share = True
                    total_area = total_area * isShare
        elif text == '제시외':
            is_excepted = True
        # 제외 구간 종료
        elif is_excepted and text.startswith('1.'):
            is_excepted = False
        # 면적 값이 있는 경우 계산
        elif area_pattern.search(text):
            area = float(area_pattern.search(text).group(1))
            if not is_excepted:
                total_area += area

    return total_area, share


def calculate_건물_area(html_td_data):
    # HTML 파싱
    soup = BeautifulSoup(html_td_data, 'html.parser')

    # 면적 추출을 위한 정규표현식 패턴
    area_pattern = re.compile(r'([\d.]+)㎡')

    # 면적 추출을 위한 변수 초기화
    total_area = 0.0
    is_excepted = False

    # HTML에서 모든 텍스트 요소 추출
    for text in soup.stripped_strings:
        # 제외 구간 시작
        if text == '제시외':
            is_excepted = True
        # 제외 구간 종료
        elif is_excepted and text.startswith('1.'):
            is_excepted = False
        # 면적 값이 있는 경우 계산
        elif area_pattern.search(text):
            area = float(area_pattern.search(text).group(1))
            if not is_excepted:
                total_area += area

    return total_area
