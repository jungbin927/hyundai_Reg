from locust import HttpUser, task, between
import random

questions = [
    "엔진 경고등이 켜졌어요",
    "타이어 공기압 확인은 어떻게 하나요?",
    "배터리 수명은 얼마나 되나요?",
    "정기점검은 언제 하나요?",
    "차량에서 이상한 소리가 나요"
]

models = [
    "아반떼", "소나타", "그랜저", "투싼", "싼타페",
    "스타리아", "캐스퍼", "아이오닉5", "아이오닉9"
]

class HyundaiUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def send_valid_query(self):
        payload = {
            "query": random.choice(questions),
            "model": random.choice(models)
        }
        print("🔥 요청 전송 시도:", payload)
        response = self.client.post("/query", json=payload)
        print("✅ 응답 코드:", response.status_code)
