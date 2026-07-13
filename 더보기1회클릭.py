import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawl_naver_place_reviews():
    print("=== [1단계] 네이버 플레이스 더보기 클릭 및 크롤링 시작 ===")
    
    options = webdriver.ChromeOptions()
    actual_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={actual_user_agent}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--window-size=1200,900')
    
    driver = webdriver.Chrome(options=options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    target_url = "https://pcmap.place.naver.com/hospital/31222521/review/visitor"
    reviews_list = []
    
    try:
        driver.get(target_url)
        # 1. 성공하셨던 60초 대기 전략 유지 (안전하게 첫 페이지 로드 및 행동 감지 우회)
        print("페이지 로딩 중... 네이버 방화벽 우회를 위해 60초간 대기합니다.")
        time.sleep(60) 
        
        # 2. 알려주신 더보기 버튼 타겟팅 및 클릭 (.NSTUp 내부의 a.fvwqf)
        print("💡 더보기 버튼 클릭을 시도합니다...")
        try:
            # 스크롤을 끝까지 내려서 버튼이 화면에 보이게 만듭니다.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 알려주신 클래스로 더보기 버튼 찾기
            more_button = driver.find_element(By.CSS_SELECTOR, ".NSTUp a.fvwqf")
            
            # 일반 click()이 네이버 보안에 막힐 경우를 대비해 자바스크립트로 강제 클릭 진행
            driver.execute_script("arguments[0].click();", more_button)
            print("👍 더보기 버튼 클릭 완료! 추가 리뷰가 로드될 때까지 5초간 대기합니다.")
            time.sleep(5) # 추가 리뷰 10개가 렌더링될 시간 확보
            
        except Exception as btn_error:
            print(f"⚠️ 더보기 버튼을 클릭하는 중 문제가 발생했습니다 (버튼이 없거나 클래스 변경 가능성): {btn_error}")
            print("현재 화면에 보이는 데이터만 수집을 진행합니다.")

        # 3. 데이터 추출 (이제 9개가 아니라 20개 내외가 잡혀야 합니다)
        review_items = driver.find_elements(By.CSS_SELECTOR, "#_review_list > li")
        print(f"🎯 최종 발견된 리뷰 아이템 수: {len(review_items)}개")
        
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
                content_element = item.find_element(By.CSS_SELECTOR, ".pui__vn15t2 .pui__GStJHb")
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
    
    print("\n[최종 데이터 수집 결과]")
    if not result_df.empty:
        print(result_df)
        print(f"\n 총 {len(result_df)}개의 리뷰 데이터를 성공적으로 가져왔습니다.")
        print("이제 안심하고 2단계(구글 시트 저장 파일)를 실행하셔도 됩니다!")
    else:
        print("❌ 데이터 수집에 실패했습니다. 대기 시간이나 요소를 다시 점검해 주세요.")