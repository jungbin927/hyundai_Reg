from fastapi import FastAPI
from back.app import text_api_router, image_api_router
from back.app.modules import load_embedding, load_llm_chain
from prometheus_fastapi_instrumentator import Instrumentator
from pymongo import MongoClient
from back.routes import router

# ✅ FastAPI 인스턴스 생성 (uvicorn이 찾는 app 객체)
app = FastAPI()
Instrumentator().instrument(app).expose(app)

# ✅ 임베딩 및 LLM 체인 초기화
embedding = load_embedding()
llm_chain = load_llm_chain()

# ✅ 라우터에 주입
text_api_router.embedding = embedding
text_api_router.llm_chain = llm_chain
image_api_router.embedding = embedding
image_api_router.llm_chain = llm_chain

# ✅ 라우터 등록
app.include_router(text_api_router.router)
app.include_router(image_api_router.router)
app.include_router(router)

# ✅ MongoDB 연결 및 FastAPI에 등록
client = MongoClient("mongodb://mongodb:27017")
mongo_db = client.hyundai_db
app.state.mongo_db = mongo_db  # ⭐ 여기가 핵심!

