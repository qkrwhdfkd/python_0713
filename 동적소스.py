import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def fetch_samyang_dynamic_titles():
    url = "https://www.samyang.co.kr/kr/investors/notice/list"
    
    # 1. 크롬 옵션 설정 (보안 우회 및 백그라운드 안정성 최적화)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 창 띄우지 않기
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 봇 인식 차단 우회
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # 2. 크롬 드라이버 세팅 및 실행
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("동적 웹페이지에 접속하여 렌더링 완료를 기다리는 중...")
    
    try:
        driver.get(url)
        
        # 3. [선택자 최적화 대기] 
        # 요소검사 결과로 확인하신 주 고유 ID '#board-table'이 브라우저 화면에 완전히 그려질 때까지 대기
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "board-table")))
        
        # 동적 객체 데이터 처리를 위해 안정적으로 1.5초 추가 대기
        time.sleep(1.5)
        
        # 4. 동적으로 렌더링된 최종 HTML 소스 확보 및 파싱
        dynamic_html = driver.page_source
        soup = BeautifulSoup(dynamic_html, 'html.parser')
        
        # [선택자 최적화 탐색] 요소검사에서 주신 'id="board-table"' 내부의 'td.tit a'만 정확히 매칭
        title_elements = soup.select('#board-table td.tit a')
        
        if not title_elements:
            print("태그 구조가 매칭되지 않거나, 데이터를 가져오지 못했습니다.")
            return

        # 5. 순수 텍스트 제목만 추출하여 출력
        print(f"\n================ 총 {len(title_elements)}개의 공고 제목 추출 성공 ================")
        for index, element in enumerate(title_elements, start=1):
            # strip=True로 태그 뒤에 숨은 무작위 공백 제거
            title_text = element.get_text(strip=True)
            print(f"[{index}] {title_text}")
        print("=================================================================\n")
            
    except Exception as e:
        print(f"크롤링 도중 오류가 발생했습니다: {e}")
        
    finally:
        # 6. 브라우저 자원 반환
        driver.quit()
        print("브라우저 세션이 안전하게 종료되었습니다.")

if __name__ == "__main__":
    fetch_samyang_dynamic_titles()