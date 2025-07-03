# Python 3.10 slim 이미지 기반
FROM python:3.10-slim

# 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# 필요 파일 복사
COPY src/front/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pymongo

# 전체 소스 복사
# COPY . .

# Streamlit 앱 실행
CMD ["streamlit", "run", "src/front/main.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.headless=true"]
