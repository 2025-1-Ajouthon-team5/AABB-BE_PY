from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import os

# id 비번 

# 사용자 정의 Expected Condition 클래스 정의
class first_article_h4_has_text:
    def __init__(self, first_article_element, child_h4_locator_css):
        self.first_article_element = first_article_element
        self.child_h4_locator_css = child_h4_locator_css

    def __call__(self, driver): # driver 인자는 WebDriverWait에 의해 전달됨
        try:
            h4_elem = self.first_article_element.find_element(By.CSS_SELECTOR, self.child_h4_locator_css)
            text_content = h4_elem.text
            if not text_content or not text_content.strip():
                text_content = h4_elem.get_attribute('textContent')
            
            return bool(text_content and text_content.strip()) # 텍스트가 비어있지 않으면 True
        except Exception: # NoSuchElementException, StaleElementReferenceException 등
            return False

def get_coursist(user_id, user_pw):
    LOGIN_URL = "https://eclass2.ajou.ac.kr/ultra/course"
    USER_ID = user_id
    USER_PW = user_pw
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu") # 안정성을 위해 추가
    options.add_argument("--no-sandbox") # 안정성을 위해 추가
    options.add_argument("--window-size=1280,1024")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    dto_list = []
    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 20) # 로그인 폼 요소들을 위한 WebDriverWait

        # 로그인 폼 요소들이 나타날 때까지 대기
        user_id_field_selector = (By.NAME, "userId")
        password_field_selector = (By.NAME, "password")
        login_button_selector = (By.ID, "loginSubmit")

        print("[ℹ️] 로그인 페이지 로딩 및 로그인 폼 요소 대기 중...")
        user_id_field = wait.until(EC.presence_of_element_located(user_id_field_selector))
        password_field = wait.until(EC.presence_of_element_located(password_field_selector))
        login_button = wait.until(EC.element_to_be_clickable(login_button_selector)) # 클릭 가능할 때까지 대기
        print("[✅] 로그인 폼 요소 감지됨.")

        # 로그인 입력
        user_id_field.send_keys(USER_ID)
        password_field.send_keys(USER_PW)
        login_button.click()
        print("[ℹ️] 로그인 시도...")

        # 로그인 후 과목 카드 로딩 대기 (기존 wait 객체 재사용 또는 새로 생성 가능)
        # wait = WebDriverWait(driver, 20) # 이미 위에서 정의했으므로 재정의 필요 없음
        course_article_elements = [] 

        # 로그인 성공 및 과목 카드 로딩 대기
        wait = WebDriverWait(driver, 20) # 대기 시간 20초로 증가
        course_article_elements = [] # 바깥 스코프에서 정의
        try:
            all_article_cards_selector = (By.CSS_SELECTOR, "article[data-course-id]")
            course_article_elements = wait.until(
                EC.presence_of_all_elements_located(all_article_cards_selector)
            )
            print(f"[✅] 로그인 성공 및 {len(course_article_elements)}개의 과목 카드(article) 감지됨.")

            if not course_article_elements:
                print("[❌] 과목 카드(article)를 찾지 못했습니다 (리스트 비어있음).")
                return

            # 첫 번째 과목 카드의 h4 제목에 텍스트가 채워질 때까지 대기
            first_article = course_article_elements[0]
            h4_title_css_within_article = "h4.js-course-title-element"
            
            wait.until(first_article_h4_has_text(first_article, h4_title_css_within_article))
            print("[ℹ️] 첫 번째 과목 카드 내 제목(h4)에 텍스트가 성공적으로 채워짐 (ng-bind 완료 추정).")

        except TimeoutException:
            print("[❌] 로그인 실패, 또는 과목 카드/제목 요소를 시간 내에 찾지 못했거나, 첫 번째 과목 제목에 텍스트가 채워지지 않았습니다.")
            # 디버깅을 위해 현재 페이지 상태 저장 (필요시 주석 해제)
            # driver.save_screenshot("debug_screenshot.png")
            # with open("debug_page_source.html", "w", encoding="utf-8") as f_debug:
            #    f_debug.write(driver.page_source)
            return
        
        # 과목 정보 파싱 시작 (wait.until에서 얻은 course_article_elements 사용)
        if not course_article_elements:
            print("[⚠️] course_article_elements 리스트가 비어있어 파싱을 진행할 수 없습니다.")
            return

        print("[✅] 수강 중인 과목:")
        courses = []
        for article in course_article_elements:
            course_id = article.get_attribute("data-course-id")
            title = "(제목 불명)"
            try:
                h4_elem = article.find_element(By.CSS_SELECTOR, "h4.js-course-title-element")
                title_text = h4_elem.text
                if not title_text or not title_text.strip():
                    title_text = h4_elem.get_attribute('textContent')

                if title_text and title_text.strip():
                    title = title_text.strip()
                else:
                    title = "(제목 비어있음)"
                    
            except Exception as e_title:
                print(f"[debug] article 내에서 제목 요소 탐색 중 오류: {e_title}")
                title = "(제목 요소 탐색 실패)"

            final_id = course_id if course_id and course_id.strip() else "(ID 없음)"
            
            # 제목과 id가 유효할 때만 자료구조에 추가
            if title not in ["(제목 불명)", "(제목 비어있음)", "(제목 요소 탐색 실패)"] and final_id != "(ID 없음)":
                courses.append({"title": title, "id": final_id})
                print(f" - {title} (ID: {final_id})")
                
            else:
                print(f" - {title} (ID: {final_id})", "제목이 비어있거나 유효하지 않음")
            
            # 코스에는 강의명과 아이디가 매칭되어 있다.     
            aaa = courses.copy() 
            
            
        if not courses:
            print("[ℹ️] 유효한 과목 제목/ID를 가진 데이터가 없습니다.")
        else:
            print("[✅] 최종 과목 리스트 자료구조:")
            print(courses)

            # 각 과목별 공지사항 페이지 접속 및 크롤링 (엔터 없이 자동 진행)
            for course in courses:
                ann_url = f"https://eclass2.ajou.ac.kr/ultra/courses/{course['id']}/announcements"
                print(f"[➡️] {course['title']} 공지사항 페이지 이동: {ann_url}")
                driver.get(ann_url)
                # 공지사항 id 추출
                announcement_ids = []
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.list-item-title"))
                    )
                    ann_elems = driver.find_elements(By.CSS_SELECTOR, "a.list-item-title")
                    for ann in ann_elems:
                        ann_id = ann.get_attribute("id")
                        if ann_id and ann_id.startswith("list-item-title-"):
                            ann_num = ann_id.replace("list-item-title-", "")
                            announcement_ids.append(ann_num)
                            print(f"  - 공지사항 id: {ann_num} / 제목: {ann.text.strip()}")
                except Exception as e:
                    print(f"[❌] 공지사항 id 추출 실패: {e}")

                # 공지사항 상세 내용 저장 및 DTO 추가
                save_announcement_details(driver, course["id"], announcement_ids, dto_list, course["title"])

            print("[✅] 모든 공지 DTO 리스트(json):")
            return dto_list

    except Exception as e:
        print("[❌] 오류 발생:", e)

    finally:
        driver.quit() 

def save_announcement_details(driver, course_id, announcement_ids, dto_list, course_title):
        
    '''
    aaa 는 
    [
        {
            "title": "강의명",
            "id": "강의아이디"
        }
    ] 이때 강의아이디를 알고 있을때 title을 얻고싶다. 
    '''
    
    base_url = "https://eclass2.ajou.ac.kr/ultra/courses/{}/announcements/announcement-detail?courseId={}&announcementId={}"
    if not os.path.exists("announcements"):
        os.makedirs("announcements")
    for ann_id in announcement_ids:
        url = base_url.format(course_id, course_id, ann_id)
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor.bb-editor"))
            )
            # 공지 제목 추출
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, "h1.panel-title")
                ann_title = title_elem.text.strip()
            except Exception:
                ann_title = "(제목 없음)"
            # 공지 본문 텍스트 추출
            detail_elem = driver.find_element(By.CSS_SELECTOR, "div.ql-editor.bb-editor")
            text = detail_elem.text.strip()
            # txt 파일로 저장하는 부분 제거
            # DTO 객체로 저장
            dto_list.append({
                "title": ann_title,
                "detail": text,
                "type": "공지",
                "course_id": course_id,
                "course_title": course_title
            })
            print(f"[✅] DTO 저장 완료: {ann_title}")
        except Exception as e:
            print(f"[❌] {url}에서 공지사항 본문 추출 실패: {e}")

# [{
#     "title": "[중간과제 안내] - 1.프로젝트 참여 필수 // 2024년에 참여한 학생도 재신청해야 합니다(일부 학생이 수행하지 않아 재공지 드립니다) ~4/30(수)까지 신청",
#     "detail": "[중간과제 안내]\n1.프로젝트 참여 필수\n- 1~2학년: 재학생 맞춤형 고용서비스 '빌드업' 프로젝트 참여\n- 3학년 이상: 재학생 맞춤형 고용서비스 점프업' 프로젝트 참여\n\n*참여방법: 강의노트 1주차 폴더 - '빌드업', '점프업' 프로젝트 신청 방법 참고\n*상세 안내: 첨부파일 참조\n※ 2024년에 참여한 학생도 재신청해야 함.",
#     "type": "공지",
#     "course_id": "_100756_1"
#   }]