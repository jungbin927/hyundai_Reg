import os 
import json
from glob import glob
from tqdm import tqdm
import torch

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceBgeEmbeddings  


input_dir = "./data/parsed/pdfminer/chunker"
output_dir = "./data/parsed/pdfminer/embedding/faiss_index"
os.makedirs(output_dir, exist_ok=True)

# 임베딩 모델 로드
embedding_model_name = "BAAI/bge-m3"
embedding_model = HuggingFaceBgeEmbeddings(
    model_name=embedding_model_name,
    model_kwargs={"device": "cuda:0"},
    encode_kwargs={"normalize_embeddings": True},       #true, false 비교 
)


def extract_model_name(path):
    """파일명에서 차종명을 추출"""
    filename = os.path.basename(path)
    return filename.split("_")[0].lower()  # 예: avante_Owner... → avante

def load_chunks(chunk_path):
    docs = []
    with open(chunk_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            content = data["text"]
            metadata = {
                "type": data.get("type", ""),
                "pages": data.get("source_pages", []),
                "model": data.get("model", "미지정")
            }
            docs.append(Document(page_content=content, metadata=metadata))
    return docs

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def main():
    chunk_files = glob(os.path.join(input_dir, "*_chunks.json"))
    print(f"청크 파일 개수: {len(chunk_files)}")

    for chunk_file in chunk_files:
        model_name = extract_model_name(chunk_file)
        print(f"⏳ 차종 '{model_name}' 처리 중...")

        docs = load_chunks(chunk_file)
        if not docs:
            print(f"⚠️ 문서 없음: {chunk_file}")
            continue

        batch_size = 8
        index = None

        for batch in tqdm(list(chunked(docs, batch_size)), desc=f"{model_name} embedding"):
            if not batch:
                continue
            if index is None:
                index = FAISS.from_documents(batch, embedding_model)
            else:
                index.add_documents(batch)
            torch.cuda.empty_cache()

        model_output_dir = os.path.join(output_dir, model_name)
        os.makedirs(model_output_dir, exist_ok=True)
        index.save_local(model_output_dir)

        print(f"✅ '{model_name}' 인덱스 저장 완료 → {model_output_dir}")

if __name__ == "__main__":
    main()