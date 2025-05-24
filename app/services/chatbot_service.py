import google.generativeai as genai
import json
from app.config import settings

# Configure the Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

# PRD에서 정의된 프롬프트를 기반으로 구성
# 참고: PRD의 "// 추가 프롬프트 (예시)" 부분은 주석으로 처리되어 있어 실제 프롬프트 문자열로 변환했습니다.
ADDITIONAL_PROMPT = (
    "너는 과제 어시스턴트야. 보내준 공지사항의 task를 분석해서 json으로 답장할것. 여러 과제인 경우 배열"
    "{"
    '"type" : "퀴즈" / "과제" / "시험"/ "일반" 중 택1로 전달,'
    '"title" : "공지사항 제목",'
    '"date": "마감기한이 명시된 경우 YYYY-MM-DD HH:MM:SS 형식으로 전달, 없으면 null",'
    '"detail" : "공지사항의 추가 설명, 없으면 null",'
    '"status" : 200 / 404 # 200은 정상, 404는 잘못 요청한 경우'
    "} 공지사항 내용은 : "
)

DEFAULT_MODEL_NAME = "gemini-2.0-flash" 

async def analyze_announcement(announcement_text: str, model_name: str = DEFAULT_MODEL_NAME) -> dict:
    """
    주어진 공지사항 텍스트를 Gemini 모델을 사용하여 분석하고, 구조화된 JSON 응답을 반환합니다.
    PRD에 명시된 프롬프트와 형식을 따릅니다.
    """
    if not announcement_text:
        return {"error": "Announcement text cannot be empty."}

    if not settings.GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured."}

    try:
        model = genai.GenerativeModel(model_name)
        full_prompt = ADDITIONAL_PROMPT + announcement_text
        
        response = await model.generate_content_async(full_prompt)
        response_text = response.text
        
        try:
            if response_text.strip().startswith("```json"):
                json_text = response_text.strip()[7:-3].strip()
            elif response_text.strip().startswith("```"):
                 json_text = response_text.strip()[3:-3].strip()
            else:
                json_text = response_text.strip()
            
            structured_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e} for model response: {response_text}") # 로그 강화
            return {"error": "Failed to decode JSON from Gemini model response.", "original_response": response_text}

        return structured_data

    except Exception as e:
        # API 호출 자체의 예외 (네트워크, 인증 등) 또는 예상치 못한 오류
        print(f"Error during Gemini API call or processing: {e}") # 로그 강화
        # traceback.print_exc() # 디버깅 시 스택 트레이스 확인
        return {"error": f"An error occurred: {str(e)}"}
