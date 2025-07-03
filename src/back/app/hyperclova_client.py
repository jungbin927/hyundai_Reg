from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
from PIL import Image
import torch

def generate_question_from_image(image_path: str) -> str:
    torch.cuda.empty_cache() 
    model_id = "naver-hyperclovax/HyperCLOVAX-SEED-Vision-Instruct-3B"

    #  사용 시점에만 모델, 토크나이저, 프로세서 로드
    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        torch_dtype=torch.float16
    ).to("cuda")

    # Step 1. VLM chat format 구성
    vlm_chat = [
        {"role": "user", "content": {"type": "image", "image": image_path}},
        {"role": "user", "content": {
            "type": "text",
            "text": (
                "이 사진은 자동차와 관련되어 있습니다.\n"
                "경고등, 파손과 같은 특이한 점이 보이면 다음과 같은 형식으로 정확히 답변해주세요.\n\n"
                "- 특이사항 종류 및 모양: 예) 스티어링 휠 모양, 엔진 모양, 브레이크, 타이어 압력 등\n"
                "- 불빛 색상(존재시): 빨간색, 노란색, 없음 등\n"
                "- 해석: 무엇을 의미하는지, 혹은 알 수 없다면 '모르겠다'라고 명확히 작성\n\n"
                "해당 형식 외의 문장은 절대 포함하지 말고, 반드시 세 줄만 출력하세요.\n"
                "종류 및 경고등 모양, 색상은 반드시 존재해야 합니다."
            )
        }}
    ]

    # Step 2. 이미지 전처리
    new_chat, all_images, is_video_list = processor.load_images_videos(vlm_chat)
    image_features = processor(all_images, is_video_list=is_video_list)

    # Step 3. 입력 텍스트 구성
    input_ids = tokenizer.apply_chat_template(
        new_chat,
        return_tensors="pt",
        tokenize=True,
        add_generation_prompt=True
    ).to("cuda")

    # Step 4. 모델 추론
    with torch.no_grad():    # ✅ 여기 추가
        outputs = model.generate(
            input_ids=input_ids,
            max_new_tokens=512,
            do_sample=True,
            top_p=0.6,
            temperature=0.5,
            repetition_penalty=1.0,
            **image_features
    )


    # Step 5. 결과 디코딩
    result = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    return result
