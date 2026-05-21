import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from collections import Counter
import re
import os
from youtube_comment_downloader import YoutubeCommentDownloader

st.set_page_config(
    page_title="유튜브 댓글 분석기",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ 유튜브 댓글 분석 웹앱")
st.write("유튜브 영상 링크를 입력하면 댓글을 수집하고 자주 등장하는 단어를 분석합니다.")

# -----------------------------
# 한글 폰트 설정
# -----------------------------
FONT_PATH = "NanumGothic.ttf"

def get_font_path():
    if os.path.exists(FONT_PATH):
        return FONT_PATH
    return None

font_path = get_font_path()

if font_path:
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams["axes.unicode_minus"] = False
else:
    font_prop = None

# -----------------------------
# 댓글 수집
# -----------------------------
@st.cache_data(show_spinner=False)
def load_comments(video_url, max_comments):
    downloader = YoutubeCommentDownloader()
    comments = []

    for comment in downloader.get_comments_from_url(video_url, sort_by=0):
        comments.append({
            "작성자": comment.get("author", ""),
            "댓글": comment.get("text", ""),
            "좋아요": comment.get("votes", 0),
            "시간": comment.get("time", "")
        })

        if len(comments) >= max_comments:
            break

    return pd.DataFrame(comments)

# -----------------------------
# 텍스트 정리
# -----------------------------
def clean_text(text):
    text = str(text)
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_words(text_list):
    stopwords = {
        "그리고", "하지만", "너무", "정말", "진짜", "영상", "댓글",
        "입니다", "합니다", "해서", "하는", "있는", "없는", "으로",
        "에서", "에게", "이거", "저거", "그거", "ㅋㅋ", "ㅎㅎ",
        "때문", "같아요", "좋아요", "정도", "이번", "오늘",
        "the", "and", "you", "this", "that", "with", "for", "are"
    }

    full_text = " ".join(text_list)
    full_text = clean_text(full_text)
    words = full_text.split()

    words = [
        word for word in words
        if len(word) >= 2 and word not in stopwords
    ]

    return Counter(words)

# -----------------------------
# matplotlib 한글 적용 함수
# -----------------------------
def apply_korean_font(ax):
    if font_prop is not None:
        ax.title.set_fontproperties(font_prop)
        ax.xaxis.label.set_fontproperties(font_prop)
        ax.yaxis.label.set_fontproperties(font_prop)

        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)

        for label in ax.get_yticklabels():
            label.set_fontproperties(font_prop)

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("⚙️ 분석 설정")

video_url = st.sidebar.text_input(
    "유튜브 영상 URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

max_comments = st.sidebar.slider(
    "수집할 댓글 수",
    min_value=50,
    max_value=1000,
    value=300,
    step=50
)

start_button = st.sidebar.button("댓글 분석 시작")

# -----------------------------
# 실행
# -----------------------------
if start_button:
    if not video_url:
        st.warning("유튜브 영상 URL을 입력해주세요.")
        st.stop()

    if font_path is None:
        st.error("NanumGothic.ttf 파일을 찾을 수 없습니다. GitHub에 폰트 파일을 업로드해주세요.")
        st.stop()

    st.info(f"사용 중인 폰트 파일: {font_path}")

    try:
        with st.spinner("댓글을 수집하는 중입니다..."):
            df = load_comments(video_url, max_comments)

    except Exception as e:
        st.error("댓글 수집 중 오류가 발생했습니다.")
        st.code(str(e))
        st.stop()

    if df.empty:
        st.warning("수집된 댓글이 없습니다.")
        st.stop()

    st.success(f"댓글 {len(df)}개를 수집했습니다.")

    df["좋아요"] = pd.to_numeric(df["좋아요"], errors="coerce").fillna(0).astype(int)

    # -----------------------------
    # 요약
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("수집 댓글 수", f"{len(df)}개")
    col2.metric("총 좋아요 수", f"{df['좋아요'].sum():,}개")
    col3.metric("평균 좋아요 수", f"{df['좋아요'].mean():.1f}개")

    st.divider()

    # -----------------------------
    # 댓글 데이터
    # -----------------------------
    st.subheader("📋 수집된 댓글")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="📥 댓글 데이터 CSV 다운로드",
        data=csv,
        file_name="youtube_comments.csv",
        mime="text/csv"
    )

    st.divider()

    # -----------------------------
    # 좋아요 TOP 10
    # -----------------------------
    st.subheader("👍 좋아요 수 TOP 10 댓글")

    top_like = df.sort_values("좋아요", ascending=False).head(10)
    st.dataframe(top_like[["작성자", "댓글", "좋아요"]], use_container_width=True)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.barh(top_like["작성자"].astype(str), top_like["좋아요"])
    ax1.set_xlabel("좋아요 수")
    ax1.set_ylabel("작성자")
    ax1.set_title("좋아요 수 TOP 10")
    ax1.invert_yaxis()
    apply_korean_font(ax1)
    st.pyplot(fig1)

    st.divider()

    # -----------------------------
    # 단어 빈도 분석
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

    for label in ax2.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")

    apply_korean_font(ax2)
    plt.tight_layout()
    st.pyplot(fig2)

    st.divider()

    # -----------------------------
    # 워드클라우드
    # -----------------------------
    st.subheader("☁️ 워드클라우드")

    try:
        wordcloud = WordCloud(
            font_path=font_path,
            width=1000,
            height=500,
            background_color="white",
            max_words=100
        ).generate_from_frequencies(word_counts)

        fig3, ax3 = plt.subplots(figsize=(12, 6))
        ax3.imshow(wordcloud, interpolation="bilinear")
        ax3.axis("off")
        st.pyplot(fig3)

    except Exception as e:
        st.error("워드클라우드 생성 중 오류가 발생했습니다.")
        st.code(str(e))
        st.stop()

else:
    st.info("왼쪽 사이드바에 유튜브 영상 URL을 입력하고 [댓글 분석 시작]을 누르세요.")

    st.markdown("""
    ### 사용 방법
    1. 유튜브 영상 URL 입력  
    2. 수집할 댓글 수 선택  
    3. 댓글 분석 시작 클릭  
    4. 댓글 목록, 좋아요 분석, 단어 빈도, 워드클라우드 확인  
    """)
