import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

def crawl_samyang_sitemap():
    print("=== [1단계] 삼양그룹 사이트맵 대메뉴 수집 시작 ===")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1400,900')
    
    # 보안 차단이 심하지 않은 사이트이므로 헤더 속이기는 최소한만 적용합니다.
    driver = webdriver.Chrome(options=options)
    
    target_url = "https://samyangwebzine.imweb.me/112"
    # 크롤링 할 페이지 주소
    menu_list = []
    
    try:
        driver.get(target_url)
        print("페이지 로딩 대기 중 (3초)...")
        time.sleep(3)
        
        # 💡 알려주신 경로를 기반으로 대메뉴 <a> 태그들을 모두 찾습니다.
        # #allMenu .menu_cont li.depth1 > a 구조를 타겟팅합니다.
        menu_elements = driver.find_elements(By.CSS_SELECTOR, ".section_wrap:not(.mobile_hide)  .doz_row  .col-dz.col-dz-6  .text-table   span")#크롤링할 내용의 html 태그
        print(f"🎯 발견된 대메뉴 수: {len(menu_elements)}개")
        
        for idx, element in enumerate(menu_elements):
            # 텍스트 추출 (예: "소개", "사업영역" 등)
            # 숨겨진 메뉴의 경우 .text 대신 get_attribute('textContent')를 써야 안전하게 텍스트를 가져옵니다.
            menu_name = element.get_attribute('textContent').strip()
            
            # 🔗 링크 주소(href) 추출
            menu_link = element.get_attribute('href')
            
            # 주소가 없거나 자바스크립트 링크(javascript:void(0))인 경우 예외 처리
            if not menu_link or "javascript" in menu_link:
                menu_link = "이동 링크 없음 (하위 메뉴 존재)"
                
            menu_list.append({
                "메뉴번호": idx + 1,
                "대메뉴명": menu_name,
                "링크주소": menu_link
            })
            
        df = pd.DataFrame(menu_list)
        return df

    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")
        return pd.DataFrame()
        
    finally:
        driver.quit()
        print("브라우저를 안전하게 종료했습니다.")

if __name__ == "__main__":
    # 
    result_df = crawl_samyang_sitemap()
    
    print("\n[삼양그룹 대메뉴 수집 결과]")
    if not result_df.empty:
        print(result_df.to_string(index=False)) # 보기 좋게 출력
        print("\n👍 대성공! 캡차 방해 없이 삼양그룹 대메뉴 주소를 깔끔하게 긁어왔습니다.")
        print("이제 바로 2단계 파일(`2_save_to_sheets.py`)을 실행하여 구글 시트에 누적해 보세요!")
    else:
        print("❌ 수집된 데이터가 없습니다. 사이트 구조나 선택자를 다시 확인해 주세요.")