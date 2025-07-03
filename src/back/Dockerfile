# CUDA 11.8 PyTorch 이미지 기반
FROM pytorch/pytorch:2.1.2-cuda11.8-cudnn8-runtime

# 기본 설정
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y git curl libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install prometheus_fastapi_instrumentator && \
    pip install pymongo

# 파이썬 패키지 설치용 requirements.txt 복사
COPY src/back/requirements.txt .

# pip 업그레이드 및 의존성 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install av decord timm einops

# 프로젝트 코드 복사
COPY . .

# PYTHONPATH 설정 (src 폴더를 루트 패키지로 인식하게 함)
ENV PYTHONPATH=/app/src

# FastAPI 앱 실행
CMD ["uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]
