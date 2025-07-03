from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class FeedbackRequest(BaseModel):
    query: str
    car_model: str
    answer: str
    feedback: str  # "good" or "bad"
    feedback_text: str = ""  # optional

@router.post("/feedback")
async def save_feedback(req: FeedbackRequest, request: Request):
    try:
        mongo_db = request.app.state.mongo_db

        # 현재 한국 시간 기준 timestamp 생성
        korea_time = datetime.utcnow() + timedelta(hours=9)

        # 수정 대상 문서 찾기
        result = mongo_db.qa_feedback_logs.update_one(
            {
                "query": req.query,
                "car_model": req.car_model,
                "answer": req.answer,
                "feedback": "not_yet"  # 질문 후 피드백 전 상태인 문서만 수정
            },
            {
                "$set": {
                    "feedback": req.feedback,
                    "feedback_text": req.feedback_text,
                    "timestamp": korea_time
                }
            }
        )

        if result.matched_count == 0:
            # 해당하는 질문 기록이 없을 때 에러 메시지
            print("❌ 피드백 업데이트 실패: 해당 질문 기록을 찾을 수 없습니다.")
            return {"status": "error", "message": "해당 질문 기록을 찾을 수 없습니다. (이미 피드백 제출되었거나 질문 기록이 없음)"}

        print(f"✅ 피드백 업데이트 완료: query={req.query}, feedback={req.feedback}")
        return {"status": "success"}

    except Exception as e:
        print(f"❌ 피드백 저장 실패: {e}")
        return {"status": "error", "message": f"피드백 저장 실패: {str(e)}"}
