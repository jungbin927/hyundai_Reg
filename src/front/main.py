import streamlit as st
import requests
from PIL import Image
import re  # 줄바꿈 처리를 위한 정규표현식 사용
import base64

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "home"

# UI 설정
st.set_page_config(page_title="차량 설명서 기반 챗봇", layout="wide")

# 이미지 Base64 인코딩
with open("src/front/static/intro_illustration.png", "rb") as img_file:
    image_base64 = base64.b64encode(img_file.read()).decode()

# ✅ 홈 화면
if st.session_state.page == "home":
    st.markdown("""
        <style>
        .stApp { background-color: #f5f7fa; }
        .home-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh;
        }
        .title-text {
            font-size: 40px !important; font-weight: 700; color: #111111; text-align: center; margin-bottom: 20px;
        }
        .desc-text {
            font-size: 20px !important; color: #555555; text-align: center; margin-bottom: 50px;
        }
        .notice-text {
            font-size: 12px !important; color: #777777; text-align: center; margin-top: 20px; margin-bottom: 30px;
        }
        .stButton>button {
            background-color: #002c5f; color: white; font-size: 20px; padding: 12px 24px;
            border: none; border-radius: 8px; cursor: pointer;
        }
        .stButton>button:hover { background-color: #004080; }
        </style>
    """, unsafe_allow_html=True)

    # HTML 화면 구성
    st.markdown(f"""
        <div class="home-container">
            <div class="title-text">차량 설명서 기반 챗봇</div>
            <div class="desc-text">
                바쁜 현대인을 위해, 복잡한 설명서 대신 AI가 핵심만 골라 알려드립니다.<br>
                차량 사용자에게 꼭 필요한 정보를 빠르게 검색, 확인하세요!
            </div>
            <img src="data:image/png;base64,{image_base64}" width="450" />
            <div class="notice-text">
                입력된 질문은 데이터베이스에 저장되나 외부에 공유되지 않으며,
                서비스 개선을 위한 분석에만 활용됩니다.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 버튼 중앙 고정 (네 구조 유지)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚗 지금 시작하기", key="start_button"):
            st.session_state.page = "chat"

# ✅ 질문 UI 화면
elif st.session_state.page == "chat":
    import re
    import requests
    from PIL import Image

    st.title("🚗 자동차 매뉴얼 기반 RAG QA 시스템")

    # -------------------- 사이드바 --------------------
    st.sidebar.header("차종 및 질문 유형을 선택해주세요.")
    category_map = {
        "세단": ["아반떼", "소나타", "그랜저"],
        "SUV": ["싼타페", "투싼", "스타리아"],
        "전기차": ["아이오닉9", "아이오닉5"],
        "경차": ["캐스퍼"]
    }
    category = st.sidebar.selectbox("차량 카테고리 선택", list(category_map.keys()))
    model_options = category_map[category]
    car_model = st.sidebar.selectbox("차량 모델 선택", model_options)
    query_mode = st.sidebar.radio("질문 유형 선택", ("텍스트 질문", "이미지 업로드"))

    # -------------------- 상태 초기화 --------------------
    if "history" not in st.session_state:
        st.session_state.history = []

    # -------------------- CSS --------------------
    st.markdown("""
        <style>
        .answer-card {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # -------------------- 줄바꿈 함수 --------------------
    def format_answer_with_smart_linebreaks(answer, threshold=40):
        segments = re.split(r'([.!?])', answer)
        formatted = ""
        temp_sentence = ""

        for segment in segments:
            if segment in '.!?':
                temp_sentence += segment
                if len(temp_sentence.strip()) > threshold:
                    formatted += temp_sentence.strip() + "<br><br>"
                else:
                    formatted += temp_sentence.strip() + " "
                temp_sentence = ""
            else:
                temp_sentence += segment

        if temp_sentence.strip():
            if len(temp_sentence.strip()) > threshold:
                formatted += temp_sentence.strip() + "<br><br>"
            else:
                formatted += temp_sentence.strip()

        return formatted

    # -------------------- 텍스트 질문 모드 --------------------
    if query_mode == "텍스트 질문":
        # 1️⃣ 질문 안내 표시
        st.markdown("❓ **질문을 입력하세요**")

        # 2️⃣ 현재 선택된 카테고리/차종 표시
        st.markdown(
            f"<p style='color:gray; font-size:14px;'>현재 선택된 카테고리는 <b>{category}</b>, 차종은 <b>{car_model}</b>입니다.</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color:#999999; font-size:11px;'>질문해주신 내용은 서비스 개선을 위해 데이터베이스에 저장됩니다.</p>",
            unsafe_allow_html=True
        )


        # 3️⃣ 질문 입력창 (label 제거)
        query = st.text_input(
            label="",
            placeholder="예: 싼타페의 시동이 안 걸릴 때 조치 방법은?"
        )

        if query:
            try:
                with st.spinner("💬 답변 생성 중입니다..."):
                    response = requests.post(
                        "http://backend:8000/query",
                        json={"query": query, "model": car_model}
                    )
                    response.raise_for_status()
                    result = response.json()

                    answer = result.get("answer", "")
                    sources = result.get("sources", [])
                    answer_with_linebreaks = format_answer_with_smart_linebreaks(answer)

                    st.session_state.history.append((query, answer))

                    # 답변 표시
                    st.markdown(
                                    f"""
                                    <div class="answer-card">
                                        <h3>💬 답변</h3>
                                        {answer_with_linebreaks}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                    )

                    # 참고 문서 표시
                    if sources:
                        source_list = ""
                        for i, src in enumerate(sources, 1):
                            source_list += f"• [{i}] page {src['page']} / model: {src['model']}<br>"

                        st.markdown(
                            f"""
                            <div class="answer-card">
                                <h3>📄 참고 문서</h3>
                                {source_list}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        # 답변 피드백
                        st.markdown("### 🙋‍♀️ 이 답변이 도움이 되었나요?")

                        col1, col2 = st.columns(2)

                        if "feedback" not in st.session_state:
                            st.session_state.feedback = None

                        with col1:
                            if st.button("👍 도움이 되었어요"):
                                res = requests.post("http://backend:8000/feedback", json={
                                    "query": query,
                                    "car_model": car_model,
                                    "answer": answer,
                                    "feedback": "good",
                                    "feedback_text": ""
                                })
                                if res.ok:
                                    st.success("감사합니다! 도움이 되었다고 응답해 주셨습니다.")
                                else:
                                    st.warning("⚠️ 피드백 저장에 실패했습니다.")
                                st.session_state.feedback = None

                        with col2:
                            if st.button("👎 개선이 필요해요"):
                                st.session_state.feedback = "bad"

                        if st.session_state.feedback == "bad":
                            feedback_text = st.text_area("어떤 부분이 부족했나요?")
                            if st.button("의견 제출"):
                                res = requests.post("http://backend:8000/feedback", json={
                                    "query": query,
                                    "car_model": car_model,
                                    "answer": answer,
                                    "feedback": "bad",
                                    "feedback_text": feedback_text
                            })
                            if res.ok:
                                st.success("의견이 제출되었습니다. 감사합니다! \n제출해주신 의견은 서비스 개선을 위해 데이터베이스에 저장됩니다.")

                            else:
                                st.warning("⚠️ 피드백 저장에 실패했습니다.")
                            st.session_state.feedback = None


            except Exception as e:
                st.error(f"FastAPI 요청 실패: {e}")

    # -------------------- 이미지 질문 모드 --------------------
    else:
        image_file = st.file_uploader("이미지를 업로드 해주세요", type=["jpg", "jpeg", "png"])
        if image_file:
            image = Image.open(image_file)
            st.image(image, caption="업로드된 이미지", use_column_width=False, width=300)

            try:
                with st.spinner("🧠 이미지 분석 및 질문 생성 중..."):
                    files = {"image": image_file.getvalue()}
                    response = requests.post(
                        "http://backend:8000/image-query",
                        files=files,
                        data={"model": car_model}
                    )
                    response.raise_for_status()
                    result = response.json()

                query = result.get("generated_question", "")
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                answer_with_linebreaks = format_answer_with_smart_linebreaks(answer)

                st.session_state.history.append((query, answer))

                # 생성된 질문 표시
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown("### 🧠 생성된 질문")
                st.write(query)
                st.markdown("</div>", unsafe_allow_html=True)

                with st.spinner("📘 매뉴얼 기반 답변 생성 중..."):
                    # 답변 표시
                    st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                    st.markdown("### 💬 답변")
                    st.markdown(answer_with_linebreaks, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # 참고 문서 표시
                    if sources:
                        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                        st.markdown("### 📄 참고 문서")
                        for i, src in enumerate(sources, 1):
                            st.markdown(f"**[{i}] page {src['page']} / model: {src['model']}**")
                        st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"이미지 질의 처리 실패: {e}")

    # -------------------- 최근 질문 기록 --------------------
    if st.session_state.history:
        history_content = ""
        for q, a in reversed(st.session_state.history[-5:]):
            history_content += f"❓ **{q}**<br>💬 {a}<br>---<br>"

        st.markdown(
            f"""
            <div class="answer-card">
                <h3>📚 최근 질문 기록</h3>
                {history_content}
            </div>
            """,
            unsafe_allow_html=True
        )
