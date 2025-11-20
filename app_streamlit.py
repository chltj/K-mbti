import streamlit as st
import pandas as pd
from analysis import analyze_style, estimate_mbti


# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="AI 말투 분석 + MBTI 추정기",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# 커스텀 CSS (카드, 헤더, 배경 등)
# -----------------------------
st.markdown(
    """
    <style>
    /* 전체 배경 약간 그라데이션 느낌 */
    .stApp {
        background: radial-gradient(circle at top left, #f4f4ff 0, #f9fbff 40%, #ffffff 100%);
    }

    /* 메인 헤더 박스 */
    .main-header {
        padding: 1.5rem 1.5rem;
        border-radius: 1.5rem;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.25);
        margin-bottom: 1.5rem;
    }

    .main-header h1 {
        font-size: 2.1rem;
        margin-bottom: 0.4rem;
    }

    .main-header p {
        font-size: 0.98rem;
        opacity: 0.93;
    }

    .tag-pill {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        margin-right: 0.35rem;
        margin-top: 0.25rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.16);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* 카드 공통 스타일 */
    .card {
        background-color: rgba(255, 255, 255, 0.93);
        border-radius: 1.2rem;
        padding: 1rem 1.1rem;
        box-shadow: 0 12px 30px rgba(148, 163, 184, 0.25);
        border: 1px solid rgba(148, 163, 184, 0.25);
        backdrop-filter: blur(8px);
    }

    .card-soft {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 1rem;
        padding: 0.9rem 1rem;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }

    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.1rem;
    }

    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #111827;
    }

    .mbti-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 1.4rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white;
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        margin-bottom: 0.5rem;
        box-shadow: 0 14px 35px rgba(34, 197, 94, 0.4);
    }

    .mbti-chip {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background-color: rgba(15, 23, 42, 0.06);
        font-size: 0.75rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }

    .comment-dot {
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background-color: #4f46e5;
        display: inline-block;
        margin-right: 0.4rem;
    }

    .comment-text {
        font-size: 0.9rem;
        color: #111827;
    }

    .warning-box {
        background-color: #fef2f2;
        border-radius: 0.75rem;
        padding: 0.7rem 0.9rem;
        border: 1px solid #fecaca;
        font-size: 0.82rem;
        color: #991b1b;
        margin-top: 0.7rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.markdown("### ⚙ 분석 옵션")
    st.write("아래 옵션은 추후 팀에서 직접 추가/튜닝할 수 있는 자리입니다.")

    show_raw_scores = st.toggle("축별 원시 점수 표시", value=True)
    show_axis_chart = st.toggle("축별 그래프 표시", value=True)
    st.markdown("---")

    st.markdown("#### 🧪 샘플 텍스트")
    sample_choice = st.radio(
        "샘플 선택",
        ["직접 입력", "외향적인 말투", "내향적인 말투", "감정 폭발형", "계획적인 스타일"],
        index=0,
    )

    samples = {
        "외향적인 말투": "오늘 진짜 사람들 만나서 수다 떨고 맛있는 거 먹고, 완전 신나게 놀았어 ㅋㅋ 다음에 또 같이 가자!",
        "내향적인 말투": "요즘에는 집에서 혼자 책 읽고 생각 정리하는 시간이 제일 편한 것 같아. 사람 많은 곳은 조금 힘들어.",
        "감정 폭발형": "솔직히 오늘 일 너무 상처였어. 나름 열심히 했는데 그런 말을 들으니까 마음이 좀 무너지는 느낌이야.",
        "계획적인 스타일": "이번 주는 월요일에 계획 세우고, 화요일까지 자료 정리 끝내고, 수요일에는 발표 연습까지 마무리할 생각이야.",
    }

    # 세션 상태에 텍스트 보관 (샘플 클릭 시 반영용)
    if "user_text" not in st.session_state:
        st.session_state["user_text"] = ""

    if sample_choice != "직접 입력":
        st.session_state["user_text"] = samples[sample_choice]


# -----------------------------
# 헤더 영역
# -----------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>🧠 AI 기반 말투 분석 + MBTI 추정기</h1>
        <p>
            대화 텍스트를 입력하면, 말투 특징을 기반으로 MBTI 축별 성향을 추정해주는 가벼운 AI 데모입니다.<br>
            규칙 기반 + 단어 사전 점수로 동작하며, 심리검사가 아닌 <b>연구/재미용 도구</b>입니다.
        </p>
        <div>
            <span class="tag-pill">NLP 기반 텍스트 분석</span>
            <span class="tag-pill">규칙 기반 Scoring</span>
            <span class="tag-pill">MBTI 축별 가시화</span>
            <span class="tag-pill">Streamlit Web Demo</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# 입력 영역
# -----------------------------
left_col, right_col = st.columns([1.4, 1])

with left_col:
    st.markdown("### ✏️ 말투 텍스트 입력")

    user_text = st.text_area(
        "상대와 나눈 카톡/메시지, 일기, 생각 정리 등 자유롭게 입력해 보세요.",
        value=st.session_state.get("user_text", ""),
        height=220,
        key="text_area_main",
    )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        analyze_button = st.button("🚀 분석하기", use_container_width=True)
    with col_btn2:
        clear_button = st.button("🧹 내용 지우기", use_container_width=True)

    if clear_button:
        st.session_state["user_text"] = ""
        st.rerun()

    st.markdown(
        """
        <div class="warning-box">
        이 데모는 **언어 패턴과 단어 사전**만을 활용한 단순 규칙 기반 도구입니다.<br>
        결과를 너무 진지하게 받아들이기보다는, 말투의 경향을 가볍게 관찰하는 용도로 활용해 주세요.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown("### ℹ️ 사용 가이드")
    st.markdown(
        """
        - 한 번에 **2~10문장 정도** 입력하면 가장 보기 좋습니다.  
        - 특정 MBTI 유형처럼 보이게 하고 싶다면, 그 사람의 말투를 흉내 내 보세요.  
        - 팀 프로젝트 발표에서는:
            - 규칙 기반 분석 로직(analysis.py)
            - Streamlit UI 구조(이 화면)
            - 한계점 & 개선 아이디어(딥러닝, BERT 등 활용)
          을 함께 설명하면 설득력이 올라갑니다.
        """
    )
    st.markdown("---")
    st.markdown("#### 📌 오늘의 한 줄 인사이트")
    st.info("“말투는 생각의 패턴이고, 그 패턴은 어느 정도 성향을 드러냅니다. 하지만 ‘사람 전체’는 아닙니다.”")


# -----------------------------
# 분석 실행 및 결과 표시
# -----------------------------
if analyze_button and not user_text.strip():
    st.warning("먼저 텍스트를 입력해 주세요!")
    st.stop()

if analyze_button and user_text.strip():
    with st.spinner("텍스트 분석 중입니다..."):
        analysis = analyze_style(user_text)
        result = estimate_mbti(analysis)

    st.markdown("## 📊 분석 대시보드")

    # 상단: MBTI 요약 & 기본 통계
    top_left, top_mid, top_right = st.columns([1.1, 1.1, 1])

    # --- MBTI 요약 카드 ---
    with top_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("**예측된 MBTI**")
        st.markdown(
            f"""
            <div style="margin-top:0.4rem; margin-bottom:0.6rem;">
                <span class="mbti-badge">{result.mbti_result}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # MBTI 4글자별 축 설명 간단 표시
        axis_labels = {
            "E": "외향 (Extraversion)",
            "I": "내향 (Introversion)",
            "S": "감각 (Sensing)",
            "N": "직관 (iNtuition)",
            "T": "사고 (Thinking)",
            "F": "감정 (Feeling)",
            "J": "판단 (Judging)",
            "P": "인식 (Perceiving)",
        }
        chips_html = ""
        for ch in result.mbti_result:
            label = axis_labels.get(ch, "")
            chips_html += f'<span class="mbti-chip"><b>{ch}</b>&nbsp;&middot;&nbsp;{label}</span>'
        st.markdown(chips_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # --- 기본 통계 카드 ---
    with top_mid:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">텍스트 기본 통계</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="metric-label">문자 수</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{result.char_count}</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="metric-label">문장 수</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{result.sentence_count}</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="metric-label">토큰 수</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{result.token_count}</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="metric-label">평균 문장 길이</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value">{result.avg_sentence_length}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # --- 코멘트 카드 ---
    with top_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">AI 코멘트</div>', unsafe_allow_html=True)
        if result.comments:
            for c in result.comments:
                st.markdown(
                    f'<div><span class="comment-dot"></span><span class="comment-text">{c}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.write("특별히 두드러지는 성향 없이, 비교적 균형 잡힌 말투로 보입니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # -----------------------------
    # 축별 비율 / 그래프 / 원시 점수
    # -----------------------------
    bottom_left, bottom_right = st.columns([1.3, 1])

    with bottom_left:
        st.markdown("### 🧭 MBTI 축별 비율(%)")

        # DataFrame으로 변환해서 bar chart
        axis_data = []
        for axis, scores in result.mbti_axis_percent.items():
            a, b = axis[0], axis[1]
            axis_data.append(
                {
                    "축": axis,
                    "유형": a,
                    "비율": scores[a],
                }
            )
            axis_data.append(
                {
                    "축": axis,
                    "유형": b,
                    "비율": scores[b],
                }
            )
        df_axis = pd.DataFrame(axis_data)

        if show_axis_chart:
            st.bar_chart(
                df_axis,
                x="유형",
                y="비율",
                color="축",
                use_container_width=True,
            )

        with st.expander("축별 비율 상세 보기"):
            st.dataframe(df_axis, use_container_width=True)

    with bottom_right:
        st.markdown("### 🧬 분석 세부 정보")

        if show_raw_scores:
            st.markdown('<div class="card-soft">', unsafe_allow_html=True)
            st.markdown("**축별 원시 점수**", unsafe_allow_html=True)
            for k, v in result.style_scores.items():
                st.write(f"- **{k}**: {v}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")
        with st.expander("입력 텍스트 다시 보기"):
            st.text(result.text)

    st.markdown("---")

    # -----------------------------
    # 설명 / 한계 / 확장 아이디어 (발표용)
    # -----------------------------
    st.markdown("## 📚 프로젝트 설명 & 확장 아이디어")

    col_ex1, col_ex2 = st.columns(2)

    with col_ex1:
        st.markdown("### 1. 현재 버전 구조")
        st.markdown(
            """
            - **analysis.py**
                - 텍스트 전처리 (문장 분리, 토큰화)
                - 단어 사전 기반 축별 점수 계산
                - MBTI 축별 비율 및 최종 MBTI 추정
                - 코멘트 생성 로직
            - **app_streamlit.py**
                - 웹 UI 레이아웃 구성
                - 입력/버튼/결과 대시보드
                - 축별 그래프 및 표 시각화
            """
        )

    with col_ex2:
        st.markdown("### 2. 이후 고도화 아이디어")
        st.markdown(
            """
            - 감정 분석, 욕설/공격성 분석 등 추가 태그 결합  
            - 실제 대화 데이터 기반 학습 모델(BERT, KoELECTRA 등)로 대체  
            - 사용자별 말투 프로파일 저장 및 히스토리 비교  
            - 모바일 최적화 UI 또는 별도 프론트엔드(React/Vue)와 연동  
            """
        )

else:
    # 아직 분석 전이라면, 간단한 안내
    st.markdown("## 👀 아직 분석을 시작하지 않았어요")
    st.markdown(
        """
        왼쪽에 텍스트를 입력하고 **“🚀 분석하기”** 버튼을 누르면,  
        이 영역에 **MBTI 예측 결과 + 말투 분석 대시보드**가 표시됩니다.

        - 샘플 텍스트를 빠르게 보고 싶다면, **왼쪽 사이드바의 샘플 텍스트**를 선택해 보세요.
        - 팀 프로젝트 발표에서는, 이 화면을 캡처해서
            - 서비스 화면 예시
            - UX 구성
            - 분석 결과 시각화
          파트에 활용하면 좋습니다.
        """
    )
