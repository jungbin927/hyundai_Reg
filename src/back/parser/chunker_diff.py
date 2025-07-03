# 아반떼, 스타리아의 pdf차이로 인한 예외 청크 처리


import json
import re

input_path = "./data/parsed/pdfminer/chunker/staria_Owner's_Manual_pdfminer_chunks.json"

# 청크 불러오기
with open(input_path, 'r', encoding='utf-8') as f:
    chunks = [json.loads(line) for line in f.readlines()]

cleaned_chunks = []
buffer = ""
current_chunk = None

for chunk in chunks:
    text = chunk["text"].strip()
    
    # 기준: 너무 짧은 청크는 보류
    if len(text) < 50 and not re.search(r"[.다요습니다]$", text):
        buffer += " " + text
        continue

    # 기존 buffer가 있다면 먼저 병합해서 하나의 청크로 저장
    if buffer:
        if current_chunk:
            current_chunk["text"] += " " + buffer.strip()
            cleaned_chunks.append(current_chunk)
            current_chunk = None
        buffer = ""

    # 현재 청크를 그대로 유지
    current_chunk = chunk
    cleaned_chunks.append(current_chunk)
    current_chunk = None

# 마지막 남은 buffer 처리
if buffer and cleaned_chunks:
    cleaned_chunks[-1]["text"] += " " + buffer.strip()

# 결과 저장 (원래 파일 덮어쓰기)
with open(input_path, 'w', encoding='utf-8') as f:
    for chunk in cleaned_chunks:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"청크 후처리 완료: {len(cleaned_chunks)}개 → 저장 완료")
