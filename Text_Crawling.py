import requests
from bs4 import BeautifulSoup
import logging
import re
from typing import Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 로깅 설정 (터미널 출력만 유지)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 터미널 출력만 사용
    ]
)

class WebScrapingError(Exception):
    """웹 스크래핑 관련 사용자 정의 예외"""
    pass

def create_session():
    """재시도 및 연결 관리를 위한 세션 생성"""
    session = requests.Session()
    retries = Retry(
        total=3,  # 최대 재시도 횟수
        backoff_factor=1,  # 지수 백오프
        status_forcelist=[429, 500, 502, 503, 504],  # 특정 상태 코드에 대해 재시도
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_and_clean_text(url: str) -> Optional[str]:
    """URL에서 데이터를 가져와 정제된 텍스트를 반환"""
    session = create_session()
    try:
        logging.info(f"시작: {url}에 대한 요청")
        
        # 헤더 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        logging.debug("User-Agent 설정 완료")
        
        # HTTP 요청
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP 오류 처리
        
        # 인코딩 설정
        response.encoding = response.apparent_encoding or 'utf-8'
        html_content = response.text
        logging.debug(f"응답 데이터 길이: {len(html_content)}")
        
        # HTML 파싱 (html.parser 사용)
        soup = BeautifulSoup(html_content, 'html.parser')  # lxml 대신 html.parser 사용
        raw_text = soup.get_text(separator='\n')
        logging.info("HTML 파싱 및 텍스트 추출 완료")
        
        # 텍스트 정제
        cleaned_text = clean_text(raw_text)
        logging.info("텍스트 정제 완료")
        
        return cleaned_text

    except requests.exceptions.RequestException as e:
        error_msg = f"네트워크 요청 오류: {str(e)}"
        logging.error(error_msg, exc_info=True)
        raise WebScrapingError(error_msg) from e
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP 오류: {response.status_code} - {response.reason}"
        logging.error(error_msg, exc_info=True)
        raise WebScrapingError(error_msg) from e
        
    except re.error as e:
        error_msg = f"정규식 처리 오류: {str(e)}"
        logging.error(error_msg, exc_info=True)
        raise WebScrapingError(error_msg) from e
        
    except AttributeError as e:
        error_msg = "HTML 파싱 오류: 필요한 요소를 찾을 수 없습니다"
        logging.error(error_msg, exc_info=True)
        raise WebScrapingError(error_msg) from e
        
    except Exception as e:
        error_msg = f"예기치 않은 오류: {str(e)}"
        logging.error(error_msg, exc_info=True)
        raise WebScrapingError(error_msg) from e

def clean_text(text: str) -> str:
    """텍스트에서 불필요한 문자열(괄호 및 내용)을 제거"""
    try:
        # 괄호와 그 안의 내용 제거
        text = re.sub(r'\(.*?\)', '', text)  # 소괄호 제거
        text = re.sub(r'\[.*?\]', '', text)  # 대괄호 제거
        
        # 연속된 공백 및 줄바꿈 정리
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 유니코드 제어 문자 제거
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        
        return text
    except re.error as e:
        logging.error(f"정규식 처리 중 오류 발생: {str(e)}")
        raise

def format_text_by_line(text: str, line_length: int = 50) -> str:
    """
    주어진 텍스트를 지정된 길이(line_length)만큼 나눠 줄바꿈을 추가합니다.
    """
    try:
        # 텍스트를 line_length 길이로 나누고 줄바꿈 추가
        lines = [text[i:i + line_length] for i in range(0, len(text), line_length)]
        formatted_text = "\n".join(lines)
        return formatted_text
    except Exception as e:
        logging.error(f"텍스트 포맷팅 중 오류 발생: {str(e)}")
        raise

def save_to_file(text: str, filename: str = "output.txt"):
    """텍스트를 파일로 저장 (50자마다 줄바꿈 추가)"""
    try:
        # 텍스트를 50자마다 줄바꿈으로 포맷팅
        formatted_text = format_text_by_line(text, line_length=50)
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(formatted_text)
        logging.info(f"결과가 파일에 저장되었습니다: {filename}")
    except Exception as e:
        logging.error(f"파일 저장 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    url = "https://www.jobkorea.co.kr/Recruit/GI_Read/46478037?Oem_Code=C1&logpath=1&stext=%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5&listno=1"
    
    try:
        result = fetch_and_clean_text(url)
        if result:            
            # 전체 결과를 파일로 저장 (50자마다 줄바꿈 추가)
            save_to_file(result, "scraped_output.txt")
            
    except WebScrapingError:
        logging.error("스크래핑 작업 실패")
    except KeyboardInterrupt:
        logging.warning("사용자에 의해 작업 중단됨")