import os
import re
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

# 1. 설정 및 기본 URL
BASE_URL = "https://www.samyang.co.kr"
TARGET_URL = "https://www.samyang.co.kr/kr/investors/archive"
DOWNLOAD_DIR = "./samyang_reports"

# 다운로드 폴더 생성
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 차단 방지를 위한 User-Agent 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def sanitize_filename(filename: str) -> str:
    """윈도우/리눅스에서 파일명으로 사용할 수 없는 특수문자 제거 및 정제"""
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    return filename.strip()

def download_reports():
    print("삼양홀딩스 사업보고서 다운로드를 시작합니다...")
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"페이지 접속 실패: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # [선택자 최적화] 
    # 대하 구조를 생략하고 데이터 성격이 명확한 테이블 내부의 다운로드 링크('a' 태그)만 정확하게 타겟팅합니다.
    download_links = soup.select('table.ir_table td.down a')
    
    if not download_links:
        print("다운로드 대상을 찾을 수 없습니다. HTML 구조를 다시 확인해주세요.")
        return

    for index, link in enumerate(download_links, start=1):
        # 상위 th 태그나 부모 text를 탐색하여 파일명으로 지정 ('제 75기 사업보고서' 등)
        # 구조상 'a' 태그가 속한 'tr' 안의 'th' 텍스트를 가져옵니다.
        row = link.find_parent('tr')
        title_text = row.find('th').get_text(strip=True) if row and row.find('th') else f"사업보고서_{index}"
        
        # href 경로 추출 및 절대 경로 변환
        relative_href = link.get('href', '')
        if not relative_href:
            continue
            
        full_url = urljoin(BASE_URL, relative_href)
        
        # https://ko.dict.naver.com/ko/entry/koko/3fcdefecb7854a7fb936d313bb55b088 
        # 상대 경로의 인코딩 파트를 정제하여 실제 파일 확장자(.pdf)를 안전하게 확보합니다.
        parsed_url = urlparse(full_url)
        clean_path = parsed_url.path  # 쿼리스트링(?folder=...)을 제외한 순수 파일 경로
        
        # 확장자 추출 (기본값은 .pdf)
        ext = os.path.splitext(clean_path)[1]
        if not ext:
            ext = ".pdf"
            
        # 최종 저장할 파일명 조립
        filename = f"{sanitize_filename(title_text)}{ext}"
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        
        print(f"[{index}/{len(download_links)}] 다운로드 중: {filename}")
        
        # 실제 PDF 파일 다운로드 진행
        try:
            file_response = requests.get(full_url, headers=headers, stream=True, timeout=15)
            file_response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            print(f" -> 완료: {file_path}")
            
        except requests.exceptions.RequestException as e:
            print(f" -> 실패 ({filename}): {e}")

    print("\n모든 다운로드 작업이 종료되었습니다.")

if __name__ == "__main__":
    download_reports()