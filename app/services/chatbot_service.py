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
    '"type" : "퀴즈" / "과제" / "시험 (exam)"/ "일반 (아무것도 아닌경우 )" 중 택1로 전달,'
    '"title" : "공지사항 제목",'
    '"date": "마감기한이 명시된 경우 YYYY-MM-DD HH:MM:SS 형식으로 전달, 없으면 null",'
    '"detail" : "공지사항의 추가 설명, 없으면 null",'
    '"status" : 200 / 404 # 200은 정상, 404는 잘못 요청한 경우'
    '"course" : 과목 제목 전달. 예 :  CLAW107_ 인권과 헌법(X508-1)' 
    "} 공지사항 내용은 :"
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
        # 공지사항 분석용 프롬프트 사용 (ADDITIONAL_PROMPT)
        full_prompt = ADDITIONAL_PROMPT + announcement_text 
        
        response = await model.generate_content_async(full_prompt)
        response_text = response.text
        
        try:
            # 모델 응답에서 JSON 부분만 추출 (마크다운 코드 블록 제거)
            if response_text.strip().startswith("```json"):
                json_text = response_text.strip()[7:-3].strip()
            elif response_text.strip().startswith("```"):
                 json_text = response_text.strip()[3:-3].strip()
            else:
                json_text = response_text.strip()
            
            structured_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e} for model response: {response_text}")
            return {"error": "Failed to decode JSON from Gemini model response.", "original_response": response_text}

        return structured_data

    except Exception as e:
        print(f"Error during Gemini API call or processing for announcement analysis: {e}")
        return {"error": f"An error occurred during announcement analysis: {str(e)}"}

# 기존 chat 함수를 사용자 질의응답용으로 수정
async def chat(user_query: str, user_tasks_context: str, model_name: str = DEFAULT_MODEL_NAME) -> str:
    """
    사용자의 질문과 데이터베이스에서 가져온 과제 정보를 바탕으로 Gemini 모델에 질의하고,
    모델의 텍스트 응답을 반환합니다.
    """
    if not user_query:
        return "질문 내용이 없습니다."
    
    if not settings.GEMINI_API_KEY:
        return "GEMINI_API_KEY가 설정되지 않았습니다."

    # 사용자 질문과 과제 컨텍스트를 조합한 프롬프트
    prompt_template = f"""
당신은 사용자 맞춤형 과제 일정 관리 및 답변을 제공하는 AI 어시스턴트입니다.
사용자의 과제 목록은 다음과 같습니다:
{user_tasks_context}

위 과제 목록을 참고하여 다음 사용자의 질문에 대해 친절하고 상세하게 답변해주세요:
{user_query}
"""
    
    try:
        model = genai.GenerativeModel(model_name)
        
        # generate_content_async는 전체 프롬프트를 인자로 받습니다.
        response = await model.generate_content_async(prompt_template) 
        
        # 모델 응답에서 텍스트 부분만 반환
        return response.text

    except Exception as e:
        print(f"Error during Gemini API call for chat: {e}")
        return f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"

