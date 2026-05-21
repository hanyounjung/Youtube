import streamlit as st
import pandas as pd
import requests
import re
import os
from urllib.parse import urlparse, parse_qs
from collections import Counter
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="유튜브 댓글 분석 웹앱", layout="wide")

st.title("📺 유튜브 댓글 분석 웹앱")
st.write("유튜브 영상 링크를 입력하면 댓글을 수집하고 분석합니다.")

API_KEY = st.secrets["YOUTUBE_API_KEY"]

STOPWORDS = {
    "그리고", "하지만", "그래서", "정말", "진짜", "너무",
    "영상", "댓글", "합니다", "입니다", "있는", "없는",
    "좋아요", "ㅋㅋ", "ㅎㅎ", "ㅋㅋㅋ", "ㅎㅎㅎ",
    "the", "and", "is", "are", "to", "of", "in", "for", "this", "that"
}

def extract_video_id(url):
    parsed = urlparse(url)

    if parsed.hostname in ["www.youtube.com", "youtube.com", "m.youtube.com"]:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    return None

def fetch_comments(video_id, max_comments):
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        api_url = "https://www.googleapis.com/youtube/v3/commentThreads"

        params = {
            "part": "snippet",
            "videoId": video_id,
            "key": API_KEY,
            "maxResults": 100,
            "textFormat": "plainText",
            "order": "time"
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(api_url, params=params)
        data = response.json()

        if response.status_code != 200:
            st.error("댓글 수집 중 오류가 발생했습니다.")
            st.write(data)
            break

        for item in data.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]

            comments.append({
                "작성자": snippet.get("authorDisplayName"),
                "댓글": snippet.get("textDisplay"),
                "좋아요수": snippet.get("likeCount", 0),
                "작성일시": snippet.get("publishedAt")
            })

            if len(comments) >= max_comments:
                break

        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break

    return pd.DataFrame(comments)

def clean_text(text):
    text = str(text)
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
    text = text.lower()
    return text

def get_word_counts(texts):
    all_words = []

    for text in texts:
        words = clean_text(text).split()
        words = [w for w in words if len(w) >= 2 and w not in STOPWORDS]
        all_words.extend(words)

    return Counter(all_words)

youtube_url = st.text_input("🔗 유튜브 영상 링크 입력")

max_comments = st.slider(
    "수집할 댓글 수",
    min_value=20,
    max_value=10000,
    value=200,
    step=20
)

if st.button("댓글 수집 및 분석 시작"):

    video_id = extract_video_id(youtube_url)

    if not video_id:
        st.warning("올바른 유튜브 영상 링크를 입력하세요.")

    else:
        with st.spinner("댓글 수집 중입니다..."):
            df = fetch_comments(video_id, max_comments)

        if df.empty:
            st.warning("댓글을 가져오지 못했습니다. 댓글이 비활성화되었거나 API 키 문제가 있을 수 있습니다.")

        else:
            st.success(f"총 {len(df)}개의 댓글을 수집했습니다.")

            df["작성일시"] = pd.to_datetime(df["작성일시"])
            df["날짜"] = df["작성일시"].dt.date
            df["시간"] = df["작성일시"].dt.hour

            st.subheader("📋 댓글 데이터")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False, encoding="utf-8-sig")

            st.download_button(
                "📥 댓글 데이터 CSV 다운로드",
                data=csv,
                file_name="youtube_comments.csv",
                mime="text/csv"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("총 댓글 수", len(df))
            col2.metric("총 좋아요 수", int(df["좋아요수"].sum()))
            col3.metric("평균 좋아요 수", round(df["좋아요수"].mean(), 2))

            st.subheader("📈 날짜별 댓글 추이")

            daily = df.groupby("날짜").size().reset_index(name="댓글 수")

            fig_daily = px.line(
                daily,
                x="날짜",
                y="댓글 수",
                markers=True,
                title="날짜별 댓글 수 변화"
            )

            st.plotly_chart(fig_daily, use_container_width=True)

            st.subheader("⏰ 시간대별 댓글 분포")

            hourly = df.groupby("시간").size().reset_index(name="댓글 수")

            fig_hourly = px.bar(
                hourly,
                x="시간",
                y="댓글 수",
                title="시간대별 댓글 수"
            )

            st.plotly_chart(fig_hourly, use_container_width=True)

            st.subheader("👍 좋아요 수가 많은 댓글 TOP 10")

            top_likes = df.sort_values("좋아요수", ascending=False).head(10)

            fig_likes = px.bar(
                top_likes,
                x="좋아요수",
                y="댓글",
                orientation="h",
                title="좋아요 수 TOP 10 댓글"
            )

            st.plotly_chart(fig_likes, use_container_width=True)

            st.subheader("☁️ 자주 등장하는 단어 워드클라우드")

            word_counts = get_word_counts(df["댓글"])

            if len(word_counts) > 0:

                font_path = "NanumGothic.ttf"
                wc = None

                try:
                    if os.path.exists(font_path):
                        wc = WordCloud(
                            font_path=font_path,
                            width=1200,
                            height=600,
                            background_color="white"
                        ).generate_from_frequencies(word_counts)
                    else:
                        st.warning("NanumGothic.ttf 파일이 없어 워드클라우드는 생략합니다.")

                    if wc is not None:
                        fig, ax = plt.subplots(figsize=(15, 7))
                        ax.imshow(wc, interpolation="bilinear")
                        ax.axis("off")
                        st.pyplot(fig)

                except Exception:
                    st.error("워드클라우드 생성 중 오류가 발생했습니다.")
                    st.info("NanumGothic.ttf 파일을 삭제 후 다시 업로드하거나, 아래 단어 빈도표를 사용하세요.")

                st.subheader("🔤 자주 등장한 단어 TOP 20")

                word_df = pd.DataFrame(
                    word_counts.most_common(20),
                    columns=["단어", "빈도"]
                )

                st.dataframe(word_df, use_container_width=True)

                fig_words = px.bar(
                    word_df,
                    x="빈도",
                    y="단어",
                    orientation="h",
                    title="자주 등장한 단어 TOP 20"
                )

                st.plotly_chart(fig_words, use_container_width=True)

            else:
                st.info("분석 가능한 단어가 부족합니다.")
