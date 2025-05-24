# assignment_crawler.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
import time
import re
import json
from datetime import datetime

LOGIN_URL = "https://eclass2.ajou.ac.kr/ultra/course"

# 아디비번 

class first_article_h4_has_text:
    def __init__(self, first_article_element, child_h4_locator_css):
        self.first_article_element = first_article_element
        self.child_h4_locator_css = child_h4_locator_css

    def __call__(self, driver):
        try:
            h4_elem = self.first_article_element.find_element(By.CSS_SELECTOR, self.child_h4_locator_css)
            text_content = h4_elem.text
            if not text_content or not text_content.strip():
                text_content = h4_elem.get_attribute('textContent')
            return bool(text_content and text_content.strip())
        except Exception:
            return False

def get_pre_task_list(user_id,user_pw):

    LOGIN_URL = "https://eclass2.ajou.ac.kr/ultra/course"
    USER_ID = user_id
    USER_PW = user_pw
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu") # 안정성을 위해 추가
    options.add_argument("--no-sandbox") # 안정성을 위해 추가
    options.add_argument("--window-size=1280,1024")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 20) # 로그인 폼 요소들을 위한 WebDriverWait

        # 로그인 폼 요소들이 나타날 때까지 대기
        user_id_field_selector = (By.NAME, "userId")
        password_field_selector = (By.NAME, "password")
        login_button_selector = (By.ID, "loginSubmit")

        print("[ℹ️] 로그인 페이지 로딩 및 로그인 폼 요소 대기 중…")
        user_id_field = wait.until(EC.presence_of_element_located(user_id_field_selector))
        password_field = wait.until(EC.presence_of_element_located(password_field_selector))
        login_button = wait.until(EC.element_to_be_clickable(login_button_selector)) # 클릭 가능할 때까지 대기
        print("[✅] 로그인 폼 요소 감지됨.")

        # 로그인 입력
        user_id_field.send_keys(USER_ID)
        password_field.send_keys(USER_PW)
        login_button.click()
        print("[ℹ️] 로그인 시도…")

        # "기존로그인이 존재 합니다." alert 처리
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"[⚠️] Alert 발생: {alert.text.strip()} -> 확인 버튼 클릭")
            alert.accept()
            print("[✅] Alert 확인 버튼 클릭 완료")
        except NoAlertPresentException:
            pass
        except Exception as e:
            print(f"[❌] Alert 처리 중 오류: {e}")

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

        if not courses:
            print("[ℹ️] 유효한 과목 제목/ID를 가진 데이터가 없습니다.")
        else:
            print("[✅] 최종 과목 리스트 자료구조:")
            print(courses)

            # 각 과목별 outline 페이지 접속
            for course in courses:
                outline_url = f"https://eclass2.ajou.ac.kr/ultra/courses/{course['id']}/outline"
                print(f"[➡️] {course['title']} OUTLINE 페이지 이동: {outline_url}")
                driver.get(outline_url)

                try:
                    # "과제출제/제출" 텍스트가 있는 button을 클릭
                    assignment_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[normalize-space()='과제출제/제출']")
                        )
                    )
                    driver.execute_script("arguments[0].click();", assignment_button)
                    print("[✅] '과제출제/제출' 폴더 버튼 클릭 완료")
                    
                    # 폴더 클릭 후 과제 링크가 나타날 때까지 잠시 대기
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//a[contains(@href, '/outline/assessment/')]")
                        )
                    )
                except Exception as e:
                    print(f"[❌] '{course['title']}' 과목의 '과제출제/제출' 폴더 버튼 클릭 또는 과제 목록 대기 실패: {e}")
                    course["assignments"] = []
                    continue # 다음 과목으로 넘어감

                # 과제 목록이 펼쳐진 후 과제 id 추출
                detailed_assignments_list = []
                try:
                    assignment_links_xpath = "//a[contains(@href, '/outline/assessment/') and @data-analytics-id='content.item.courses.outline.gradebook.item.assessment.readOnly.link']"
                    assignment_links = WebDriverWait(driver, 10).until(
                        EC.visibility_of_all_elements_located((By.XPATH, assignment_links_xpath))
                    )
                    
                    print(f"[ℹ️] {course['title']}: {len(assignment_links)}개의 과제 링크 감지됨.")

                    assignments_to_visit = []
                    for a in assignment_links:
                        href = a.get_attribute("href")
                        title = a.text.strip()
                        m = re.search(r'/outline/assessment/(_\d+_\d+)/', href)
                        # 마감일 추출
                        try:
                            parent = a.find_element(By.XPATH, "./ancestor::div[contains(@class, 'makeStylescontentItemComponentDetailsGuts')]")
                            due_elem = parent.find_element(By.XPATH, ".//div[contains(@class, 'makeStylesgradeDetail')]")
                            due_date_raw = due_elem.text.strip()
                            due_date_match = re.search(r'마감일:\s*([\d\. ]+\d:\d+)', due_date_raw)
                            if due_date_match:
                                due_date = due_date_match.group(1).replace(" ", "")
                            else:
                                due_date = ""
                        except Exception:
                            due_date = ""
                        if m:
                            assignment_id = m.group(1)
                            assignments_to_visit.append({
                                "id": assignment_id,
                                "title": title,
                                "course_id": course['id'],
                                "course_title": course['title'],
                                "due_date": due_date
                            })
                            print(f"  - 과제 발견: {title} (ID: {assignment_id}) / 마감일: {due_date}")
                        else:
                            print(f"  - [⚠️] 링크에서 과제 ID 패턴을 찾지 못함: {href}")
                    
                    # 수집된 과제 정보를 바탕으로 각 과제 상세 페이지를 방문합니다.
                    for assign_info in assignments_to_visit:
                        assignment_id = assign_info["id"]
                        assignment_title = assign_info["title"]
                        current_course_id = assign_info["course_id"]
                        current_course_title = assign_info["course_title"]
                        due_date = assign_info["due_date"]

                        assignment_detail_url = f"https://eclass2.ajou.ac.kr/ultra/courses/{current_course_id}/outline/assessment/{assignment_id}/overview/attempt/create?courseId={current_course_id}"
                        print(f"[🔎] '{current_course_title}' - '{assignment_title}' (ID: {assignment_id}) 상세 페이지로 이동: {assignment_detail_url}")
                        driver.get(assignment_detail_url)

                        print(f"[ℹ️] '{assignment_title}' 상세 페이지 로드 후 2초 대기...")
                        time.sleep(2)

                        try:
                            print(f"[⏳] '{assignment_title}' 상세 페이지에서 실제 콘텐츠 요소(id='bb-editorassignment-attempt-authoring-instructions') 대기 중...")
                            wait_for_element = WebDriverWait(driver, 20)
                            actual_content_selector = (By.ID, "bb-editorassignment-attempt-authoring-instructions")
                            content_element = wait_for_element.until(
                               EC.visibility_of_element_located(actual_content_selector)
                            )
                            print(f"[✅] '{assignment_title}' 상세 페이지 실제 콘텐츠 요소 감지됨.")
                            body_content = content_element.text.strip()
                            if not body_content:
                                print(f"[⚠️] '{assignment_title}' (ID: {assignment_id}) 내용이 비어있을 수 있습니다.")
                                body_content = "Error: 내용 없음 (지정된 요소는 찾았으나 텍스트 내용이 비어있음)"
                            
                            # DTO 형태로 저장
                            detailed_assignments_list.append({
                                "title": assignment_title,
                                "detail": body_content,
                                "type": "과제",
                                "due_date": due_date,
                                "status": "not yet",
                                "course_id": current_course_id
                            })
                            print(f"[📄] 과제 DTO 저장 (과목: {current_course_title}, 과제: {assignment_title}, ID: {assignment_id}, 마감일: {due_date})")
                        except TimeoutException:
                            error_message = f"Error: 상세 페이지 로드 또는 지정된 콘텐츠 요소(id='bb-editorassignment-attempt-authoring-instructions')를 시간 내에 찾지 못함 - {assignment_detail_url}"
                            print(f"[❌] '{assignment_title}' {error_message}")
                            detailed_assignments_list.append({
                                "title": assignment_title,
                                "detail": error_message,
                                "type": "과제",
                                "due_date": due_date,
                                "status": "not yet",
                                "course_id": current_course_id
                            })
                        except Exception as e_detail:
                            error_message = f"Error: 상세 페이지 처리 중 오류 - {e_detail}"
                            detailed_assignments_list.append({
                                "title": assignment_title,
                                "detail": error_message,
                                "type": "과제",
                                "due_date": due_date,
                                "status": "not yet",
                                "course_id": current_course_id
                            })

                    course["assignments"] = detailed_assignments_list

                except TimeoutException:
                     print(f"[❌] {course['title']}: 과제 링크를 찾는 중 시간 초과 발생.")
                     course["assignments"] = []
                except Exception as e:
                    print(f"[❌] {course['title']}: 과제 ID 추출 중 오류 발생: {e}")
                    course["assignments"] = []

                if not course["assignments"]:
                    print(f"  - {course['title']}: 처리할 과제가 없거나 가져오지 못했습니다.")
                
                # 다음 과목으로 넘어가기 전에 현재 과목의 outline 페이지로 돌아갈 필요는 없습니다.
                # 바깥쪽 for course in courses 루프가 시작될 때 driver.get(outline_url)을 이미 하고 있기 때문입니다.
                # print(f"[↩️] '{course['title']}' 과목의 모든 과제 상세 확인 후 OUTLINE 페이지로 돌아갑니다: {outline_url}")
                # driver.get(outline_url) # 불필요한 이동이 될 수 있음.
                # WebDriverWait(driver, 10).until(EC.url_to_be(outline_url)) # 돌아왔는지 확인


            print("[✅] 과목별 과제 상세 내용 처리 후 최종 자료구조 (assignments는 각 과제의 ID, 제목, 상세 내용을 포함):")
            all_assignments = []
            for course in courses:
                for assignment in course.get("assignments", []):
                    all_assignments.append(assignment)
            return all_assignments
    except UnexpectedAlertPresentException:
        # 예기치 않은 alert가 떠 있을 때 무조건 닫고 한 번 더 시도
        try:
            alert = driver.switch_to.alert
            print(f"[⚠️] (예외) Alert 발생: {alert.text.strip()} -> 확인 버튼 클릭")
            alert.accept()
            print("[✅] (예외) Alert 확인 버튼 클릭 완료. 다시 시도하세요.")
        except Exception as e:
            print(f"[❌] (예외) Alert 처리 중 오류: {e}")
        return get_course_list(user_id, user_pw)  # 재귀적으로 한 번 더 시도

    except Exception as e:
        print("[❌] 전체 작업 중 오류 발생:", e)
        return []
    finally:
        if 'driver' in locals() and driver:
            driver.quit()
            print("[✅] 드라이버 종료.")

def get_task_dto_list(all_assignments):
    result = []
    for item in all_assignments:
        # due_date 예시: "25.3.9.23:59"
        try:
            # 연,월,일,시:분 분리
            date_obj = datetime.strptime(item["due_date"], "%y.%m.%d.%H:%M")
        except Exception:
            date_obj = None
        # 새 dict에 datetime 객체 추가 (또는 원하는 포맷의 문자열로 변환)
        new_item = item.copy()
        new_item["due_date_obj"] = date_obj
        result.append(new_item)
    return result

## 쓰는법 get_task_dto_list(get_pre_task_list("아이디", "비밀번호"))
