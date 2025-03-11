import requests
from bs4 import BeautifulSoup

def fetch_and_clean_text(url):
    try:
        # 1. User-Agent를 포함한 headers 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        
        # 2. URL에 GET 요청 보내기 (headers 포함)
        response = requests.get(url, headers=headers)
        
        # 3. 응답 상태 확인 (200: 성공)
        if response.status_code == 200:
            print("페이지 접속 성공!")
            
            # 4. HTML 내용 가져오기
            html_content = response.text 
            
            # 5. BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 6. HTML 태그 제거 및 텍스트 추출
            raw_text = soup.get_text(separator='\n')  # 태그 제거, 줄바꿈으로 구분
            
            # 7. 불필요한 문자열(괄호 등) 제거
            cleaned_text = clean_text(raw_text)
            
            # 8. 결과 출력
            print(cleaned_text)
            return cleaned_text
        else:
            print(f"요청 실패: 상태 코드 {response.status_code}")
            return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def clean_text(text):
    """
    텍스트에서 불필요한 문자열(괄호 및 내용)을 제거합니다.
    """
    import re
    
    # 1. 괄호와 그 안의 내용 제거 (예: "(내용)" 또는 "[내용]")
    text = re.sub(r'\(.*?\)', '', text)  # 소괄호 제거
    text = re.sub(r'\[.*?\]', '', text)  # 대괄호 제거
    
    # 2. 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()  # 연속된 공백을 하나로 줄이고 양쪽 공백 제거
    
    return text

# 사용 예시
url = "https://www.jobkorea.co.kr/Recruit/GI_Read/46478037?Oem_Code=C1&logpath=1&stext=%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5&listno=1"  # 원하는 URL 입력
cleaned_text = fetch_and_clean_text(url)