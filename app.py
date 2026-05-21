import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re
import os
from youtube_comment_downloader import YoutubeCommentDownloader

st.set_page_config(page_title="유튜브 댓글 분석기", page_icon="☁️", layout="wide")

st.title("☁️ 유튜브 댓글 분석 웹앱")
st.write("유튜브 영상 링크를 입력하면 댓글을 수집하고, 좋아요 수 분석과 워드클라우드를 보여줍니다.")

# -----------------------------
# 한글 폰트 설정
# -----------------------------
FONT_PATH = "NanumGothic.ttf"

def get_font_path():
    if os.path.exists(FONT_PATH):
        return FONT_PATH
    return None

# -----------------------------
# 유튜브 댓글 수집 함수
# -----------------------------
@st.cache_data(show_spinner=False)
def load_comments(video_url, max_comments):
    downloader = YoutubeCommentDownloader()
    comments = []

    try:
        for comment in downloader.get_comments_from_url(video_url, sort_by=0):
            comments.append({
                "작성자": comment.get("author", ""),
                "댓글": comment.get("text", ""),
                "좋아요": comment.get("votes", 0),
                "시간": comment.get("time", "")
            })

            if len(comments) >= max_comments:
                break

    except Exception as e:
        return pd.DataFrame(), str(e)

    return pd.DataFrame(comments), None

# -----------------------------
# 텍스트 전처리
# -----------------------------
def clean_text(text):
    text = str(text)
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_words(texts):
    stopwords = {
        "그리고", "하지만", "너무", "정말", "진짜", "영상", "댓글",
        "입니다", "합니다", "해서", "하는", "있는", "없는",
        "the", "and", "you", "this", "that", "with", "for"
    }

    all_text = " ".join(texts)
    all_text = clean_text(all_text)

    words = all_text.split()
    words = [
        w for w in words
        if len(w) >= 2 and w not in stopwords
    ]

    return Counter(words)

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("⚙️ 설정")
video_url = st.sidebar.text_input("유튜브 영상 URL 입력")
max_comments = st.sidebar.slider("수집할 댓글 수", 50, 1000, 300, 50)

analyze_btn = st.sidebar.button("댓글 분석 시작")

# -----------------------------
# 메인
# -----------------------------
if analyze_btn:
    if not video_url:
        st.warning("유튜브 영상 URL을 입력해주세요.")
        st.stop()

    with st.spinner("댓글을 수집하는 중입니다..."):
        df, error = load_comments(video_url, max_comments)

    if error:
        st.error("댓글 수집 중 오류가 발생했습니다.")
        st.code(error)
        st.stop()

    if df.empty:
        st.warning("수집된 댓글이 없습니다.")
        st.stop()

    st.success(f"댓글 {len(df)}개를 수집했습니다.")

    # 좋아요 숫자 정리
    df["좋아요"] = pd.to_numeric(df["좋아요"], errors="coerce").fillna(0).astype(int)

    # -----------------------------
    # 요약 지표
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("수집 댓글 수", f"{len(df)}개")

    with col2:
        st.metric("총 좋아요 수", f"{df['좋아요'].sum():,}개")

    with col3:
        st.metric("평균 좋아요 수", f"{df['좋아요'].mean():.1f}개")

    st.divider()

    # -----------------------------
    # 댓글 원본 보기
    # -----------------------------
    st.subheader("📋 수집된 댓글")
    st.dataframe(df, use_container_width=True)

    # CSV 다운로드
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="댓글 데이터 CSV 다운로드",
        data=csv,
        file_name="youtube_comments.csv",
        mime="text/csv"
    )

    st.divider()

    # -----------------------------
    # 좋아요 상위 댓글
    # -----------------------------
    st.subheader("👍 좋아요 수가 많은 댓글 TOP 10")
    top_like = df.sort_values("좋아요", ascending=False).head(10)
    st.dataframe(top_like[["작성자", "댓글", "좋아요"]], use_container_width=True)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.barh(top_like["작성자"].astype(str), top_like["좋아요"])
    ax1.set_xlabel("좋아요 수")
    ax1.set_ylabel("작성자")
    ax1.set_title("좋아요 수 TOP 10")
    ax1.invert_yaxis()
    st.pyplot(fig1)

    st.divider()

    # -----------------------------
    # 자주 등장하는 단어
    # -----------------------------
    st.subheader("🔤 자주 등장하는 단어 TOP 20")

    word_counts = extract_words(df["댓글"].tolist())

    if len(word_counts) == 0:
        st.warning("분석할 단어가 부족합니다.")
        st.stop()

    word_df = pd.DataFrame(
        word_counts.most_common(20),
        columns=["단어", "빈도"]
    )

    st.dataframe(word_df, use_container_width=True)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(word_df["단어"], word_df["빈도"])
    ax2.set_xlabel("단어")
    ax2.set_ylabel("빈도")
    ax2.set_title("자주 등장하는 단어 TOP 20")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    st.divider()

    # -----------------------------
    # 워드클라우드
    # -----------------------------
    st.subheader("☁️ 자주 등장하는 단어 워드클라우드")

    font_path = get_font_path()

    if font_path is None:
        st.error("""
        한글 워드클라우드를 만들기 위한 폰트 파일이 없습니다.

        GitHub 프로젝트 폴더에 `NanumGothic.ttf` 파일을 추가해주세요.
        """)
        st.stop()

    try:
        wc = WordCloud(
            font_path=font_path,
            width=1000,
            height=500,
            background_color="white"
        ).generate_from_frequencies(word_counts)

        fig3, ax3 = plt.subplots(figsize=(12, 6))
        ax3.imshow(wc, interpolation="bilinear")
        ax3.axis("off")
        st.pyplot(fig3)

    except Exception as e:
        st.error("워드클라우드 생성 중 오류가 발생했습니다.")
        st.code(str(e))

else:
    st.info("왼쪽 사이드바에 유튜브 영상 URL을 입력하고 분석을 시작하세요.")

    st.markdown("""
    ### 사용 방법
    1. 유튜브 영상 URL 입력  
    2. 수집할 댓글 수 선택  
    3. 댓글 분석 시작 클릭  
    4. 댓글 목록, 좋아요 분석, 단어 빈도, 워드클라우드 확인  
    """)
