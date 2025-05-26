from fastapi.concurrency import run_in_threadpool
from app.services.chatbot_service import analyze_announcement
from app.services.AnnService import get_coursist
from app.services.assgin_service import get_task_dto_list, get_pre_task_list
from app.services.chatbot_service import analyze_announcement

from sqlalchemy.orm import Session

from datetime import datetime

from app import crud, schemas
from app.database import get_db
from typing import Dict, Any, List
import json

import ast
from app.schemas import TaskType
from typing import Optional

# 테스트용 데이터 정의 (사용자 코드에서 가져옴)
TEST_ANNOUNCEMENT_DATA_STR = """
[
  {
    "title": "[중간과제 안내] - 1.프로젝트 참여 필수 // 2024년에 참여한 학생도 재신청해야 합니다(일부 학생이 수행하지 않아 재공지 드립니다) ~4/30(수)까지 신청",
    "detail": "[중간과제 안내]\\n1.프로젝트 참여 필수\\n- 1~2학년: 재학생 맞춤형 고용서비스 '빌드업' 프로젝트 참여\\n- 3학년 이상: 재학생 맞춤형 고용서비스 점프업' 프로젝트 참여\\n\\n*참여방법: 강의노트 1주차 폴더 - '빌드업', '점프업' 프로젝트 신청 방법 참고\\n*상세 안내: 첨부파일 참조\\n※ 2024년에 참여한 학생도 재신청해야 함.",
    "type": "공지",
    "course_id": "_100756_1"
  },
  {
    "title": "2025년 1학기 중간고사 안내(인문사회계열 취업역량개발)-2차공지",
    "detail": "안녕하세요. '인문사회계열 취업역량개발' 교수 김기진입니다.\\n\\n중간고사(과제)는 학습 정리를 위한 '중간고사 FTP학습설문'에 응답하시면 됩니다.\\n=> 각 문항별로 500자 내외 작성하시기 바랍니다. \\n\\n*응답(과제 제출): https://forms.gle/z22564wpySmTQ6wc7\\n*제출 기간: 2025. 4. 14(월) ~ 4. 25(금)\\n*제출여부 확인:  https://docs.google.com/spreadsheets/d/1SCPIfQNGLhRcHS_QPoHXr2L8zwJJsK3JGEe2fXPWy38/edit?usp=sharing\\n  <작성법>\\nFact. '인문사회계열 취업역량개발' 강의를 통해 배운 내용 중 핵심이 되는 내용을 기술합니다.\\nThink. 상기와 같이 정리한 내용에 대해 본인의 생각이나 느낌을 기술합니다.\\nPlan. 취업준비를 위해 어떻게 적용할 것인지에 대해 구체적으로 기술합니다.\\n=> 작성한 내용은 입력한 이메일로 자동 발송됩니다.(회신 이메일로 과제 제출여부 확인)",
    "type": "공지",
    "course_id": "_100756_1"
  },
  {
    "title": "과제 안내: 2024년에 참여한 학생도 재신청해야 함.",
    "detail": "[중간과제 안내]\\n1.프로젝트 참여 필수\\n- 1~2학년: 재학생 맞춤형 고용서비스 '빌드업' 프로젝트 참여\\n- 3학년 이상: 재학생 맞춤형 고용서비스 점프업' 프로젝트 참여\\n\\n*참여방법: 강의노트 1주차 폴더 - '빌드업', '점프업' 프로젝트 신청 방법 참고\\n 수행기한: 2025년 5월 31일까지\\n*상세 안내: 첨부파일 참조\\n※ 2024년에 참여한 학생도 재신청해야 함.\\n\\n2.FTP학습정리 => 중간과제 제출 기간에 별도 안내 예정입니다\\nFact. 강의를 통해 배운 내용 중 핵심이 되는 내용 작성\\nThink. 상기와 같이 정리한 내용에 대해 본인의 생각이나 느낌 작성\\nPlan. 취업준비를 위해 어떻게 적용할 것인지에 대해 작성",
    "type": "공지",
    "course_id": "_100756_1"
  },
  {
    "title": "인문계열 취업역량개발 수업 참여에 따른 설문 응답(자유)",
    "detail": "안녕하세요~ 김기진(에릭) 교수입니다.\\n금번 인문계열 취업역량개발 수업 참여하심을 환영합니다\\n아래는 설문 응답 바랍니다\\n\\n*목적:\\n1.설문응답 과정에 자신을 정리해보는 시간\\n2.응답 내용은 분석하여 강의 내용에 반영해서 가능한 맞춤형 강의 진행\\n\\n오프닝 설문_아주대_인문사회계열 취업역량개발\\nhttps://forms.gle/GaMc6dxsRZN7asqX8",
    "type": "공지",
    "course_id": "_100756_1"
  },
  {
    "title": "고강도 상호작용 관련 보고서 과제(요일 수정)",
    "detail": "고강도 상호작용 관련 보고서 과제\\n ※ 강의자 이메일(ohdos@ajou.ac.kr)로 제출하시오. 분량은 제한 없고, 파일명에 반드시 본인 이름을 포함할 것.\\n 2 근로자의 권리 또는 노동법 관련하여 궁금한 점, 특히 특강자인 조석영 변호사에게 질문하고 싶은 사항을 최소 3가지 작성하여 제출하시오. [기한 ~ 5. 20.(화) 자정]\\n3&4 1980년 ‘5․18 광주민중항쟁’을 인권 또는 헌법 관점에서 설명하시오. [기한 ~ 5. 27.(화) 자정]\\n5&6 대통령 윤석열에 대한 헌법재판소의 탄핵 결정문을 찾아 자신이 생각하는 가장 중요한 탄핵 사유부터 정리하시오. [기한 ~ 6. 3.(화) 자정]\\n7&8 자신의 전공 관점에서 기후 위기의 문제를 설명하고 자신의 의견을 제시하시오. 전공 관점에 적절하지 않다면, 전공과 무관하게 관련 자료에 근거하여 기후 위기 문제에 대한 의견을 제시하시오. [기한 ~ 6. 10.(화) 자정]",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "5월 5일 줌 강의 링크",
    "detail": "주제: CLAW107_ 인권과 헌법(X508-1)\\n시간: 2025년 5월 5일 09:00 서울\\n\\nZoom 회의 참가\\nhttps://ajou-ac-kr.zoom.us/j/81687734243\\n\\n회의 ID: 816 8773 4243\\n암호: 185082",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "[홍보] 2025 국회의장배 청년 토론대회 – 국회의정연수원 주관",
    "detail": "국회 의정연수원 주관으로 개최되는 「2025 국회의장배 청년 토론대회」가 오는 6월 24일(화)부터 6월 27일(금)까지 3박 4일 일정으로 진행됩니다. \\n이 대회는 대학생들이 민주주의에 대한 비판적 사고력과 공적 표현 능력을 함양할 수 있는 소중한 기회로, 특히 정치·법·사회이론을 학습하는 학생들의 참여에 큰 의미가 있을 것으로 기대됩니다.\\n대회와 관련하여 더 자세한 사항은 아래 링크를 참조하여 주시기 바랍니다.\\nhttps://training.assembly.go.kr/train/edcReqst/edcReqst/viewTrn.do?menuPathCd=C1&menuNo=1700023&eduId=20250317145832285&sdate=&edate=&searchOjrDiv=undefined&searchWrd=&pageIndex=&pageUnit=",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "긴급 공지",
    "detail": "중간시험 자료를 포함한 수정한 파일을 올렸다고 생각했는데, 다른 과목의 파일을 잘못 올렸습니다. 미안합니다. 다시 올린 화일을 보기 바랍니다.",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "중간시험 범위의 참고 자료",
    "detail": "수정된 파일을 참고하기 바랍니다.",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "중간시험 범위 공지",
    "detail": "중간시험 범위는 다음과 같습니다\\n\\n1. 시민불복종\\n2. 저항권\\n3. 대통령 윤석열의 탄핵",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "중간시험 안내",
    "detail": "중간 시험은 4월 23일(수) 09:00 - 10:15 연암관 105호에서 실시합니다.\\n시험 범위를 공지할 테니 강의노트를 중심으로 공부하면 됩니다.\\n시험 유형은 기출 문제를 참고하세요.",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "첫 번째 과제 마감 기한 관련 안내",
    "detail": "공지 사항에서 마감 기한(24일)과 과제 제출 마감 기한(20일)이 달라 후자도 24일로 수정했습니다.",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "보고서 관련 안내",
    "detail": "기한은 3월 24일(월) 자정까지입니다. 아주 Bb 과제물 제출을 이용하여 제출하세요.",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "보고서 첫 번째 과제",
    "detail": "※ 아래의 예시를 참고하여 평소 관심 주제 또는 최근 언론 보도를 통해 관심 있는 인권 또는 헌법 관련 주제를 선택해서 무엇이 쟁점인지 또는 논점인지를 A4 용지 1장 이내로 설명하시오.\\n☞ 경향신문 2025. 3. 17. ““고소득층 왜 많나”… “학원비 보태려는 맞벌이 가구 늘었을 것”: 사교육비 조사…교육청 ‘우문’에 통계청의 ‘현답’” → 사교육과 교육을 받을 권리\\n☞ 경향신문 2025. 3. 17. ““예쁘지 않아도… A급과 똑같이 판매돼야”: 온라인 과일 판매 공석진씨가 말하는 기후위기와 농업” → 기후 위기와 인권 또는 헌법\\n☞ 경향신문 2025. 3. 17. ““원청 한화오션이 교섭에 나서라” 조선소 하청 노동자의 외침” → 원청과 하청 관계에서 근로의 권리 또는 단체교섭권\\n☞ 경향신문 2025. 3. 19. “‘2021년 버스 탑승 시위’ 박경석 전장연 대표 유죄 확정, 법 바뀌지 않는 한… 법 바깥인 ‘장애인 이동권 싸움’” → 장애인의 이동권\\n☞ 경향신문 2025. 3. 19. ““성매매 10대 돕기 핵심은 정상 복귀 아닌 왜 이탈했냐는 물음”, 연대․지원 모임 ‘부라자’ 활동가들 ‘3개월 겪어보니…’” → 성매매 관련 인권 문제\\n☞ 경향신문 2025. 3. 19. “윤 측 주장한 ‘절차상 흠결’, 법조계선 ‘모두 법적 근거 없다’: ‘각하 사유’ 쟁점별 분석” → 탄핵과 헌법\\n☞ 경향신문 2025. 3. 19. “인권위 “미등록 이주아동 구제 계속하라”, D-4 비자 발급 정책 종료 임박” → 미등록 이주아동의 권리\\n☞ 경향신문 2025. 3. 19. “학생에 설립자 묘소 참배시키고… 체험학습 때 이사장 손자 돌보게 한 사학: 서울교육청, 환일중 감사… 입학식서 군대식 거수경례도” → 사립학교에서 학생의 인권\\n☞ 한겨레 2025. 3. 19. “1980~90년대 ‘민감국가’ 지정된 것도 당시 핵무장론이 이유” → 핵의 인권과 헌법\\n☞ 한겨레 2025. 3. 19. “‘3인 체제’ 방통위법도…최상목, 9번째 거부권” → 대통령의 법률안 재의요구권과 대통령 권한대행의 권한\\n☞ 한겨레 2025. 3. 19. ““기후변화 무대응땐 금융권 46조 손실…늑장땐 타격 커져”” → 기후 위기의 인권과 헌법 문제\\n☞ 한겨레 2025. 3. 19. “미, 유앤 구호기관들 ‘반미’ 사상 검증” → 사상의 자유\\n☞ 한겨레 2025. 3. 19. “성추행 가해자와 동선 분리 미흡, 결국 피해자가 회사를 떠났다” → 성적 괴롭힘의 인권 문제\\n☞ 한겨레 2025. 3. 19. “온난화로 빨라지는 봄, 꽃샘추위 더 잦아진다” → 지구온난와의 인권과 헌법 문제",
    "type": "공지",
    "course_id": "_102687_1"
  },
  {
    "title": "2025-1 중간고사 대체과제",
    "detail": "다음주 4월 22일은 중간고사 기간이라 수업이 없으니 참고하세요... \\n\\n중간고사 대체 과제입니다...  \\n안녕하세요? 여지숙입니다...\\n자원봉사자는 다양한 대상의 인권에 민감하게 대응해야 합니다... 인권수호자의 역할을 해야하는 것이지요...\\n그래서 아동인권영화 한편을 소개합니다.. 이영화를 보시고 소감과 함께 아동인권에 대한 여러분의 의견을 제시하고 특히, 한국의 아동인권\\n에 대한 생각과 아동인권정책을 제안해 주시기 바랍니다.\\n\\n* 영화제목 : 가버나움(2019.01.24 개봉, 드라마, 레바논, 미국125분)\\n* 재출분량 : 한글, 워드문서 A4 3~5장(표지제외) 11포인트\\n* 제출기한 : 2025년 5월6일(화요일) 까지 (마감기한 엄수)\\n* 제출방법 : 이메일 cdw99@ajou.ac.kr (첨부화일 누락되지 않도록 주의바람)\\n*영화는 네이버에서 검색해서 다운받고 감상하시면 됩니다 (1,500원 소요예정)",
    "type": "공지",
    "course_id": "_102994_1"
  },
  {
    "title": "3월4일 오티 녹화분",
    "detail": "",
    "type": "공지",
    "course_id": "_102994_1"
  },
  {
    "title": "2025-1학기 사회봉사이론 오티 공지",
    "detail": "안녕하세요? 여지숙입니다...\\n사회봉사이론 오티 수업을 3월 4일 화요일 오후 4:30 에 실시간 zoom 으로 수업하고자 합니다. \\n컨텐츠에서 'zoom' 방에 입장하셔서 수업에 참여하시면 됩니다...\\n수강 변경때문에 오티 수업 참여가 어려우시면 오티 줌 수업분을 녹화하여 올리고자 하오니 꼭 필히 확인하여 듣기를 바랍니다...\\n결석이 총 수강 일수의 1/4 이상이면 F 라는 규정이 있으니 꼭 수업에 출석하시기 바랍니다. 이번학기는 어린이날 대체공휴일로  3번 결석까지만 봐줍니다.. \\n4번결석부터는 F 나갈 수밖에 없음을 꼭 명심하세요...\\n\\n\\n문의사항은 이태훈 조교 이메일 : 이메일 thoon@ajou.ac.kr 또는 전화 031-219-3057 로 연락바랍니다.",
    "type": "공지",
    "course_id": "_102994_1"
  },
  {
    "title": "중간고사 성적통계입니다.",
    "detail": "",
    "type": "공지",
    "course_id": "_101013_1"
  },
  {
    "title": "4월7일 12:00 수업시작하면서 오프라인출석 퀴즈가 있습니다.",
    "detail": "이번퀴즈는 원격에서 온라인으로 치룰수 없습니다.\\n미리 늦지않게 출석하기 바랍니다.",
    "type": "공지",
    "course_id": "_101013_1"
  },
  {
    "title": "캡스톤디자인 경진대회 서류 제출",
    "detail": "캡스톤디자인 경진대회 관련 추천서와 참가 신청서를 조교 메일로 보내주시면 되겠습니다.",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "SW캡스톤디자인 공개특강 05.26(월) 'AI시대, 소프트웨어 인재로 성장하기' 참여 안내",
    "detail": "특강주제: AI시대, 소프트웨어 인재로 성장하기\\n\\n특강연사: 현대오토에버 류석문 전무\\n\\n일시 및 장소: 2025.05.26(월) 16:30 (팔달관 309호)\\n\\n관심있는 학생 누구가 특강 참여가 가능합니다.\\n\\n\\nhttps://www.ajou.ac.kr/kr/ajou/notice.do?mode=view&articleNo=348246&boardNo=43",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "캡스톤디자인 설계발표",
    "detail": "설계 발표자료를 과제 제출란 기한에 맞게 제출 해주시면 감사하겠습니다.",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "2025-1학기 AJOU SOFTCON행사",
    "detail": "2025-1학기 AJOU SOFTCON행사에 관해 안내 드립니다.\\n조교를 통해서 신청 및 일괄 접수가 됩니다.\\n\\n2025-1 AJOU SOFTCON 개요.pdf",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "2025 제 20회 캡스톤디자인 경진대회 개최 안내",
    "detail": "2025년도 캡스톤디자인 경진대회에 대해 안내 드립니다.\\n1. 참여대상: 2024-2, 2025-1학기 캡스톤디자인(종합설계) 교과목을 수강(한)하는 3학년 이상 재학생\\n          (2인 이상 팀 구성)\\n2. 신청방법: ACOT 오픈창의플랫폼 온라인 신청(참가신청서 및 첨부자료 제출)\\n3. 신청기간: 2025.05.22.(목) ~ 05.26.(월) 18:00\\n4. 시상계획: 대상 - 시상금 200만원 / 아주대학교 총장상\\n          최우수상 - 시상금 100만원 / 아주대학교 산학협력단장상 \\n          우수상 - 시상금 50만원 / 아주대학교 창의산학교육원장상\\n          장려상 - 시상금 10만원 / 아주대학교 창의산학교육원장상 \\n\\n캡스톤디자인 교과목을 수강하는 학생을 대상으로 하는 '제20회 캡스톤디자인 경진대회 개최' 공고는\\n금일 오전에 학교 공지사항과 사업단 홈페이지를 통해 공지되었습니다. (제20회 캡스톤디자인 경진대회 개최 공지사항)\\n\\n기타 문의사항이 있으신 경우, 연락주시기 바랍니다.",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "제안 발표 공지 16, 21일",
    "detail": "제안 발표를 16, 21일에 할 예정이고 준비되는 조부터 16일에 세 개조, 그리고 나머지 조는 21일에 할 계획입니다.\\n\\n15일까지 제안 발표 자료를 조교에게 보내주길 바랍니다.\\n\\n조교 메일 - jonahmun96@ajou.ac.kr",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "미니 프로젝트 발표자료 제출",
    "detail": "미니 프로젝트 발표자료 조교 메일로 제출해주시기 바랍니다.",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "멘토링 공지 3월 31일",
    "detail": "31일 아래의 두 분 멘토를 모시고 첫 멘토링을 합니다.\\n\\n멘토 : 삼성전자 무선사업부 클라우드 개발자\\n           BOS반도체(차량SoC전문기업, 삼성전자 SLSI 20년 근무)\\n\\n추가 사항은 수업 시간에 공지하겠습니다.\\n\\n각자 일정에 참고바랍니다.",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "과제 수행 비용 지원 관련",
    "detail": "각 팀별로 정보 (팀명, 팀원, 주제, 멘토 등)가 포함된 과제계획서를 3월 26일 팀별 활동 시간까지 메일로 보내주시기 바랍니다.\\n과제계획서 양식.hwp",
    "type": "공지",
    "course_id": "_101019_1"
  },
  {
    "title": "조 편성 관련",
    "detail": "이미 조 편성을 제출한 조는 팀장 정보도 추가 제출하기 바랍니다.\\n\\n또한 조편성이 필요한 학생들도 메일 보내기 바랍니다.\\n\\n월요일부터는 조 편성 완료하고 팀 별 활동 시작할 예정입니다.\\n\\n각 조는 온/오프 자체 모임을 통해 아이디어 브레인스토밍하기 바라며 수업 자료 참고해서 어떤 아이디어들이 도출되었었는지도 잘 보기 바랍니다.",
    "type": "공지",
    "course_id": "_101019_1"
  }
]
"""

TEST_ASSIGNMENT_DATA_STR = """
[
  {
    "title": "첫 번째 과제",
    "detail": "※ 헌법 관련 주제를 선택해서 무엇이 쟁점인지 또는 논점인지를 A4 용지 1장 이내로 설명하시오. (기한은 3월 24일 자정까지)☞ 경향신문 2025. 3. 17. ““",
    "type": "과제",
    "due_date": "25.3.24.23:59",
    "status": "not yet",  
    "course_id": "_102687_1",
    "due_date_obj": "2025-03-24T23:59:00"
  },
  {
    "title": "새 과제 25. 3. 4.",
    "detail": "Error: 내용 없음 (지정된 요소는 찾았으나 텍스트 내용이 비어있음)",
    "type": "과제",
    "due_date": "25.3.9.23:59",
    "status": "not yet",
    "course_id": "_102994_1",
    "due_date_obj": "2025-03-09T23:59:00"
  }
]
"""

try:
    TEST_ASSIGNMENT_DATA = json.loads(TEST_ASSIGNMENT_DATA_STR) 
    
except json.JSONDecodeError:
    print("Warning: TEST_ASSIGNMENT_DATA_STR의 JSON 파싱에 실패했습니다. 빈 리스트로 대체됩니다.")
    TEST_ASSIGNMENT_DATA = []
    
# client에게 TASK LIST를 반환하는 함수 
async def get_task_list(current_school_id: str, current_password: str, db: Session) -> List[Dict[str, Any]]:
    
    responses = []
    
    # DB의 TASK를 조회해서 해당 학생에 맞는 일정을 반환 
    db_user = crud.get_user(db, school_id=current_school_id)
    if db_user:
      
        response = []
        
        for task in db_user.tasks:
            response.append({
                "due_date": task.due_date,
                "id": task.id,
                "title": task.title,
                "type": task.type,
                "course" : task.course
            })
        return response
      
    else:
        return []

async def _fetch_raw_data(current_school_id: str, current_password: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], Exception | None]:
    """로컬 헬퍼 함수: 서비스들로부터 원시 데이터를 가져옵니다."""
    local_announcements = []
    local_assignments = []
    local_service_error = None
    
    try: 
        # 1. 공지사항 크롤링 (AnnService)
        print(f"[CrawlerService] AnnService.get_coursist 호출 시작: user_id={current_school_id}")
        ann_dtos: List[Dict[str, Any]] = await run_in_threadpool(get_coursist, user_id=current_school_id, user_pw=current_password)
        print(f"[CrawlerService] AnnService.get_coursist 호출 완료. {len(ann_dtos) if ann_dtos else 0}개의 공지 DTO 수신.")
        local_announcements = ann_dtos if ann_dtos else []
        
        local_announcements = json.dumps(local_announcements, ensure_ascii=False, indent=4)
        
        print(f"local_announcements: {local_announcements}")

        print(f"[CrawlerService] assgin_service.get_task_dto_list 호출 시작: user_id={current_school_id}")
        
        assign_dtos = get_pre_task_list(current_school_id, current_password)
        
        print(f"[CrawlerService] assgin_service.get_task_dto_list 호출 완료. {len(assign_dtos) if assign_dtos else 0}개의 과제 DTO 수신.")
        local_assignments = assign_dtos if assign_dtos else []

    except Exception as e:
        local_service_error = e
        print(f"[CrawlerService] 크롤링 서비스 호출 중 오류 발생: {e}")
        # 로컬 함수에서는 오류를 반환하고, 메인 함수에서 최종 처리 결정
        
    return local_announcements, local_assignments, local_service_error

async def _save_assignments(
    assignments_data: List[Dict[str, Any]], 
    current_school_id: str, 
    current_db: Session
) -> int:
    """Helper function to save assignment data to DB."""
    count = 0
    
    if assignments_data:
      
        for task_data in assignments_data:
            try:
                due_date_obj = task_data.get("due_date_obj") or task_data.get("due_date")
                if isinstance(due_date_obj, str):
                    try:
                        due_date_obj = datetime.strptime(due_date_obj, "%y.%m.%d.%H:%M")
                    except ValueError:
                        try:
                            due_date_obj = datetime.strptime(due_date_obj, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            print(f"[CrawlerService] 과제 날짜 형식 오류: {due_date_obj}. Null로 처리.")
                            due_date_obj = None
                
                task_type_str = task_data.get("type")
                task_type_enum = schemas.TaskType.assignment # 기본값
                if task_type_str:
                    try:
                        task_type_enum = schemas.TaskType(task_type_str)
                    except ValueError:
                        print(f"[CrawlerService] 알 수 없는 과제 타입: {task_type_str}. 기본값({task_type_enum.value}) 사용.")
                        pass 

                task_create = schemas.TaskCreate(
                    title=task_data.get("title", "제목 없음"),
                    detail=task_data.get("detail"),
                    type=task_type_enum,
                    due_date=due_date_obj,
                    source_description=task_data.get("detail"),
                    course=task_data.get("course_title")
                )
                
                print(f"task_create: {task_create}")
                
                # 중복검증 
                duplicate_task = crud.check_duplicate_task(db=current_db, task=task_create, user_school_id=current_school_id)
                
                
                if duplicate_task:
                    print(f"Warning: 중복 과제 발견 - ID: {duplicate_task.id}, 제목: {duplicate_task.title}")
                    continue
                
                crud.create_user_task(db=current_db, task=task_create, user_school_id=current_school_id)
                count += 1
            except Exception as e:
                print(f"[CrawlerService] 과제 저장 중 오류: {task_data.get('title')} - {e}")
        print(f"[CrawlerService] 과제 {count}개 저장 완료.")
    return count

async def _analyze_and_save_announcements(
    announcements_data: str,
    current_school_id: str,
    current_db: Session
) -> int:
    """Helper function to analyze announcements and save them as tasks to DB."""
    count = 0

    if announcements_data:
        # analyze_announcement는 Python literal string을 반환
        analysis_result_str: str = await analyze_announcement(announcements_data)
        
        analysis_result_str = json.dumps(analysis_result_str, ensure_ascii=False, indent=4)
        
        try:
            parsed_items = json.loads(analysis_result_str)

        except Exception as e:
            print(f"Error: analyze_announcement의 반환값 파싱 실패. 오류: {e}")
            print(f"받은 문자열: {analysis_result_str}")
   
        for item_data in parsed_items:
          
            print(f"item_data: {item_data}")

            try:
                # 'type' 필드 처리
                task_type_str = item_data.get('type')
                if not task_type_str: # 타입이 없거나 빈 문자열이면 기본값 사용 또는 로깅
                    print(f"Warning: 'type' 필드가 없거나 비어있습니다. item: {item_data}. 기본값 '일반' 사용.")
                    task_type_str = "일반" # 또는 TaskType.일반.value (Enum 정의에 따라)

                # TaskType Enum으로 변환
                try:
                    task_type_enum_value = TaskType(task_type_str)
                except ValueError:
                    print(f"Warning: 유효하지 않은 TaskType 값 '{task_type_str}'. 기본값 '일반' 사용.")
                    task_type_enum_value = TaskType.일반 # 또는 적절한 기본값

                # 'date' 필드를 'due_date'로 변환 (datetime 객체로)
                due_date_obj: Optional[datetime] = None
                date_str = item_data.get('date') # 'date' 키로 받아옴
                if date_str:
                    try:
                        # ISO 8601 형식 문자열 "YYYY-MM-DD HH:MM:SS"을 datetime 객체로 변환
                        due_date_obj = datetime.fromisoformat(date_str)
                    except ValueError:
                        print(f"Warning: 날짜 형식 오류 - '{date_str}'. None으로 처리합니다. item: {item_data}")
                        # 날짜 파싱 실패 시 due_date_obj는 None으로 유지


                print(f"item_data.get('course'): {item_data.get('course')}")
                
                # TaskCreate 스키마 객체 생성
                task_to_create = schemas.TaskCreate(
                    title=item_data.get('title', '제목 없음'), # title이 없을 경우 기본값
                    detail=item_data.get('detail'),
                    type=task_type_enum_value,
                    due_date=due_date_obj,
                    source_description="CrawlerService Announcement", # 또는 다른 출처 정보 
                    course = item_data.get('course') # 
                )
                                
                # 중복검증 
                duplicate_task = crud.check_duplicate_task(db=current_db, task=task_to_create, user_school_id=current_school_id)
                
                if duplicate_task:
                    continue
                
                created_task = crud.create_user_task(db=current_db, task=task_to_create, user_school_id=current_school_id)
                print(f"created_task: {created_task}")
                
                if created_task:
                    count += 1
                    print(f"DEBUG: Task 생성 성공 - ID: {created_task.id}, 제목: {created_task.title}")
                else:
                    print(f"Error: Task 생성 실패 - 데이터: {task_to_create.model_dump_json()}")


            except Exception as e:
                # 각 아이템 처리 중 발생할 수 있는 모든 예외 처리
                # (예: 필수 필드 누락으로 인한 Pydantic ValidationError, DB 오류 등)
                print(f"Error: 아이템 처리 및 DB 저장 중 오류 발생: {item_data}. 오류: {e}")
                # 필요하다면, 특정 아이템 실패 시 전체 롤백 또는 부분 성공 로직 추가

    else:
        print("[CrawlerService] announcements_data가 비어있어 처리할 내용이 없습니다.")

    print(f"[CrawlerService] 총 {count}개의 Task가 생성되었습니다.")
    return count

async def process_crawled_data_for_user(school_id: str, password: str, db: Session) -> Dict[str, Any]:
    """
    지정된 사용자의 공지사항 및 과제 정보를 크롤링하고, 분석하여 데이터베이스에 저장합니다.
    """
    service_error = None # 테스트 데이터 사용 시 오류는 없다고 가정 
    
    # 실제 운영 시에는 위의 _fetch_raw_data 호출 결과 사용:
    announcements_data_to_process, assignments_data_to_process, service_error = await _fetch_raw_data(school_id, password)

    # DB에 저장 
    saved_tasks_from_assign = await _save_assignments(assignments_data_to_process, school_id, db)
    
    # LLM 호출 후 DB에 저장하기 
    saved_tasks_from_ann = await _analyze_and_save_announcements(announcements_data_to_process, school_id, db)
    
    return await get_task_list(school_id, password, db) 
  
async def process_crawled_data_for_user2(school_id: str, password: str, db: Session) -> Dict[str, Any]:
    """
    지정된 사용자의 공지사항 및 과제 정보를 크롤링하고, 분석하여 데이터베이스에 저장합니다.
    """
    service_error = None # 테스트 데이터 사용 시 오류는 없다고 가정 
    
    # 가짜 데이터 
    announcements_data_to_process = TEST_ASSIGNMENT_DATA
    assignments_data_to_process = TEST_ASSIGNMENT_DATA
        
    # DB에 저장 
    saved_tasks_from_assign = await _save_assignments(assignments_data_to_process, school_id, db)
    
    # LLM 호출 후 DB에 저장하기 
    saved_tasks_from_ann = await _analyze_and_save_announcements(announcements_data_to_process, school_id, db)
    
    return await get_task_list(school_id, password, db) 
        
        
        
