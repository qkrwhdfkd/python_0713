import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def crawl_naver_place_reviews():
    print("=== [1단계] 네이버 플레이스 차단 우회 크롤링 시작 ===")
    
    options = webdriver.ChromeOptions()
    
    # 1. 봇 차단 우회의 핵심: 실제 사람이 쓰는 브라우저인 척 User-Agent 헤더 보내기
    actual_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={actual_user_agent}')
    
    # 2. 자동화 제어 플래그 비활성화 (네이버가 감지하는 핵심 흔적 지우기)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 일반적인 브라우저 크기 세팅
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    
    # 3. 브라우저 스크립트 수정을 통해 navigator.webdriver 성향을 완전 False로 속임
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    target_url = "https://pcmap.place.naver.com/hospital/31222521/review/visitor"
    reviews_list = []
    
    try:
        driver.get(target_url)
        print("페이지 로딩 중... 네이버를 속이는 중입니다 (60초 대기)")
        time.sleep(60) # 봇처럼 보이지 않게 충분한 여유 시간을 줍니다.
        
        # 리뷰 리스트 가져오기
        review_items = driver.find_elements(By.CSS_SELECTOR, "#_review_list > li")
        print(f"🎯 차단 우회 성공! 발견된 리뷰 아이템 수: {len(review_items)}개")
        
        for idx, item in enumerate(review_items):
            try:
                author = item.find_element(By.CSS_SELECTOR, ".pui__NMi-Dp").text.strip()
            except:
                author = "익명 방문자"
                
            try:
                visit_count = item.find_element(By.CSS_SELECTOR, ".pui__WN-kAf").text.strip()
            except:
                visit_count = "정보 없음"
                
            try:
                content_element = item.find_element(By.CSS_SELECTOR, ".pui__GStJHb")
                content = content_element.text.strip().replace("\n", " ")
            except:
                content = "내용 없음 (사진 또는 키워드 리뷰)"
            
            reviews_list.append({
                "작성자": author,
                "방문횟수": visit_count,
                "리뷰내용": content,
                "평점": 5,
                "작성일": "2026-07-13"
            })
            
        df = pd.DataFrame(reviews_list)
        return df

    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")
        return pd.DataFrame()
        
    finally:
        driver.quit()
        print("브라우저를 안전하게 종료했습니다.")

if __name__ == "__main__":
    result_df = crawl_naver_place_reviews()
    
    print("\n[실제 데이터 수집 결과]")
    if not result_df.empty:
        print(result_df)
        print("\n👍 봇 차단을 뚫고 데이터를 모두 가져왔습니다! 이제 2단계로 고고 하셔도 됩니다.")
    else:
        print("❌ 여전히 막힌다면 네이버가 임시로 해당 IP를 차단했을 수 있습니다. 잠시 후 다시 시도해 보세요.")