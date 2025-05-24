알겠습니다. 요청하신 내용을 바탕으로 FastAPI 서버 구축을 위한 PRD (Product Requirements Document)를 Markdown 형식으로 작성해 드리겠습니다.

# PRD: Blackboard 과제 관리 및 알림 서버

**Version:** 1.0
**Date:** 2023-10-27 (문서 작성일)
**Author:** (사용자 이름 또는 팀 이름)

## 1. 개요 (Introduction)

본 문서는 대학교 Blackboard (블랙보드) 시스템의 과제 및 공지사항 정보를 크롤링하고, Google Gemini API와 LangChain을 활용하여 주요 정보를 추출 및 구조화한 뒤, 이를 MySQL 데이터베이스에 저장하는 FastAPI 기반 백엔드 서버 개발을 위한 요구사항 명세서입니다. 사용자는 이 서버를 통해 자신의 과제 정보를 효과적으로 관리하고, 프론트엔드 애플리케이션을 통해 해당 정보를 조회할 수 있습니다.

## 2. 목표 (Goals)

*   Blackboard 내 공지사항 및 과제 정보를 자동화된 방식으로 수집한다.
*   수집된 텍스트 데이터를 Google Gemini 및 LangChain을 통해 분석하여 체계적인 JSON 형식의 과제 정보로 변환한다.
*   변환된 과제 정보를 사용자별로 MySQL 데이터베이스에 영구적으로 저장한다.
*   프론트엔드 애플리케이션이 사용자별 과제 목록을 요청하고 받을 수 있는 API 엔드포인트를 제공한다.
*   사용자의 학사 관리 편의성을 증진시킨다.

## 3. 대상 사용자 (Target Users)

*   대학교 Blackboard 시스템을 사용하는 학생

## 4. 주요 기능 (Key Features)

### 4.1. 사용자 인증 및 관리
    *   사용자는 학교 ID와 비밀번호를 시스템에 등록하여 Blackboard 정보 접근 권한을 위임합니다.
    *   사용자 정보(학교 ID, 암호화된 비밀번호, 학번)를 데이터베이스에 저장합니다.

### 4.2. Blackboard 데이터 크롤링 (외부 모듈)
    *   지정된 사용자의 Blackboard 계정으로 로그인합니다.
    *   수강 중인 과목 목록 및 각 과목의 공지사항/과제 게시판에 접근합니다.
    *   새로운 공지사항이나 과제 관련 텍스트 데이터를 수집합니다.
    *   **참고:** 크롤링 로직은 별도의 서비스 파일/모듈로 개발되어 본 서버와 연동될 예정입니다. (본 PRD에서는 상세 구현 명시 X)
    * 따라서 이것은 개발과정에서 무시하시면 되겠습니다. 

### 4.3. AI 기반 공지사항 분석 및 과제 정보 추출 (Gemini & LangChain)
    *   크롤링된 공지사항 텍스트 데이터를 입력으로 받습니다.
    *   Google Gemini API와 LangChain을 사용하여 다음 프롬프트 엔지니어링 규칙에 따라 정보를 추출하고 JSON 형식으로 구조화합니다:
        ```
        // 추가 프롬프트 (예시)
        String additionalPrompt = "너는 과제 어시스턴트야. 보내준 공지사항의 task를 분석해서 json으로 답장할것. 여러 과제인 경우 배열" +
                "{" +
                "type : \"퀴즈\" / \"과제\" / \"시험\"/ \"일반\" 중 택1로 전달"+ // 따옴표 추가하여 문자열 명시
                "title : \"공지사항 제목\"" +
                "date: \"마감기한이 명시된 경우 YYYY-MM-DD HH:MM:SS 형식으로 전달, 없으면 null\"" + // 형식 명시
                "detail : \"공지사항의 추가 설명, 없으면 null\"" +
                "is_announcement_valid : true / false // 요청 내용이 유의미한 과제/공지사항인지 여부" +
                "} 공지사항 내용은 : ";
        ```
    *   Gemini가 반환한 JSON 데이터를 파싱합니다. `is_announcement_valid`가 `true`인 경우에만 다음 단계를 진행합니다.

### 4.4. 과제 정보 데이터베이스 저장
    *   Gemini를 통해 추출 및 구조화된 과제 정보(type, title, date, detail)를 `Task` 테이블에 저장합니다.
    *   각 `Task`는 해당 정보를 수집한 `User`와 매핑됩니다.
    *   초기 `status` (사용자의 과제 완료 여부)는 `false` (미완료)로 설정됩니다.

### 4.5. 수강 과목 정보 관리
    *   사용자가 수강하는 과목 목록(과목명, 과목 ID)을 `ClassList` 테이블에 저장하고 `User`와 매핑합니다.
    *   이 정보는 크롤링 시 대상 과목을 특정하거나, 사용자에게 과목별 필터링 기능을 제공하는 데 사용될 수 있습니다.

### 4.6. API 엔드포인트 제공
    *   **사용자 등록/로그인 API:**
        *   `POST /auth/register`: 사용자 정보(학교 ID, 비밀번호, 학번)를 받아 저장 (비밀번호는 해싱하여 저장)
        *   `POST /auth/login`: 사용자 로그인 (세션 또는 토큰 기반 인증)
    *   **과제 정보 API:**
        *   `GET /users/{user_id}/tasks`: 특정 사용자의 모든 과제 목록을 반환합니다.
            *   쿼리 파라미터로 필터링 기능 제공 (예: `?status=false` 미완료 과제, `?type=과제` 타입별 과제)
        *   `PUT /tasks/{task_id}/status`: 특정 과제의 완료 여부(`status`)를 업데이트합니다.
    *   **데이터 동기화 API:**
        *   `POST /users/{user_id}/sync`: 특정 사용자의 Blackboard 데이터를 크롤링하고 AI 분석 후 DB에 저장하는 프로세스를 트리거합니다.
    *   **수강 과목 API (선택적):**
        *   `GET /users/{user_id}/courses`: 특정 사용자의 수강 과목 목록을 반환합니다.

## 5. 기술 스택 (Technical Stack)

*   **프로그래밍 언어:** Python 3.9+
*   **웹 프레임워크:** FastAPI
*   **데이터베이스:** MySQL
*   **ORM:** SQLAlchemy
*   **AI:** Google Gemini API, LangChain
*   **크롤러:** Python 기반 Selenium - 이것은 개발자가 별도 개발합니다.
*   **비동기 처리:** `async/await` (FastAPI 기본), Celery (백그라운드 크롤링/AI 처리 시 고려)

## 6. 데이터베이스 스키마 (Database Schema - MySQL)

```sql
-- 사용자 정보 테이블
CREATE TABLE User (
    school_id VARCHAR(255) PRIMARY KEY,  -- 학교 ID (PK)
    school_password VARCHAR(255) NOT NULL, -- 암호화된 학교 비밀번호
    student_number VARCHAR(50) NOT NULL, -- 학번
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 수강 과목 목록 테이블
CREATE TABLE ClassList (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_school_id VARCHAR(255) NOT NULL,    -- User 테이블의 school_id (FK)
    course_name VARCHAR(255) NOT NULL,       -- 과목명
    course_id VARCHAR(100) NOT NULL,         -- 과목 ID (Blackboard 내 고유 ID)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_school_id) REFERENCES User(school_id) ON DELETE CASCADE
);

-- 과제 정보 테이블
CREATE TABLE Task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_school_id VARCHAR(255) NOT NULL,    -- User 테이블의 school_id (FK)
    title VARCHAR(255) NOT NULL,             -- 해야 할 일 제목
    detail TEXT,                             -- 해야 할 일의 세부 정보 (NULL 가능)
    type ENUM('퀴즈', '과제', '시험', '일반') NOT NULL, -- 종류
    due_date DATETIME,                       -- 마감 기한 (NULL 가능, YYYY-MM-DD HH:MM:SS 형식)
    status BOOLEAN NOT NULL DEFAULT FALSE,   -- 유저의 과제 완료 여부 (기본값: 미완료)
    source_description TEXT,                 -- Gemini 분석 전 원본 공지 내용 (선택적, 디버깅/로깅용)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_school_id) REFERENCES User(school_id) ON DELETE CASCADE
);


관계:

User : Task (1 : N) - 한 명의 유저는 여러 개의 Task를 가질 수 있습니다.

User : ClassList (1 : N) - 한 명의 유저는 여러 개의 수강 과목 정보를 가질 수 있습니다.

7. 비기능적 요구사항 (Non-Functional Requirements)

보안:

사용자의 Blackboard 비밀번호는 일단 해커톤임을 고려하여 암호화하여 저장하지는 않습니다. 로그인은 추후에 제대로 구현합니다. 

API 통신은 HTTPS를 사용합니다.

Gemini API 키 등 민감 정보는 환경 변수 또는 보안 저장소를 통해 관리합니다.

성능:

API 응답 시간은 평균 1초 이내를 목표로 합니다. (크롤링 및 AI 처리 시간 제외)

크롤링 및 AI 처리 작업은 백그라운드에서 비동기적으로 처리하여 사용자 경험에 영향을 주지 않도록 고려합니다. (예: Celery)

안정성:

Blackboard 웹사이트 구조 변경 시 크롤러의 안정적인 동작을 위한 유지보수 방안을 고려합니다.

Gemini API 호출 실패 등 예외 상황에 대한 적절한 오류 처리 및 로깅 메커니즘을 구현합니다.

확장성:

향후 사용자 증가 및 기능 확장에 대비하여 모듈식 설계를 지향합니다.

8. 위험 요소 및 고려 사항 (Risks and Considerations)

Blackboard 이용 약관: 자동화된 크롤링은 대학교 또는 Blackboard 서비스 제공업체의 이용 약관에 위배될 수 있습니다. 반드시 관련 규정을 확인하고 준수해야 하며, 필요한 경우 학교 측의 허가를 받아야 합니다. 이로 인한 계정 정지 등의 불이익은 서비스 제공자가 책임지지 않습니다.

Blackboard UI 변경: Blackboard 시스템 업데이트로 인해 웹사이트의 HTML 구조가 변경되면 크롤러가 정상 동작하지 않을 수 있습니다. 주기적인 유지보수가 필요합니다.

로그인 보안: 2FA(2단계 인증)가 설정된 계정의 경우 크롤링 자동화가 더 복잡해질 수 있습니다.

AI 모델의 정확도: Gemini가 항상 100% 정확하게 정보를 추출하고 분류하지 못할 수 있습니다. 예외 처리 및 사용자에 의한 수정 기능이 필요할 수 있습니다.

서버 부하: 과도한 크롤링 요청은 Blackboard 서버에 부하를 줄 수 있으므로, 적절한 요청 간격(delay)을 설정해야 합니다.

9. 향후 개선 사항 (Future Enhancements - Out of Scope for v1.0)

향후 개선 사항은 지금 개발은 하지 않습니다. 

과제 마감일 푸시 알림 기능 (예: 모바일 앱, 이메일)

캘린더 연동 기능 (iCal export)

사용자 정의 태그/카테고리 기능

팀/스터디 그룹 간 과제 공유 기능 (권한 관리 필요)

이 PRD를 바탕으로 FastAPI 서버 개발을 진행합니다. 