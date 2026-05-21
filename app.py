import streamlit as st
import pandas as pd
import requests
import re
from urllib.parse import urlparse, parse_qs
from collections import Counter
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="유튜브 댓글 분석 웹앱", layout="wide")

API_KEY = st.secrets["YOUTUBE_API_KEY"]

st.title("📺 유튜브 댓글 분석 웹앱")
st.write("유튜브 영상 링크를 입력하면 댓글을 수집하고, 시간대별 반응·좋아요·자주 등장한 단어를 분석합니다.")

STOPWORDS = {
    "그리고", "하지만", "그래서", "너무", "정말", "진짜", "영상", "댓글",
    "입니다", "합니다", "있는", "없는", "좋아요", "ㅋㅋ", "ㅎㅎ",
    "the", "and", "is", "are", "to", "of", "in", "for", "that", "this"
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
        url = "https://www.googleapis.com/youtube/v3/commentThreads"
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

        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            st.error(data.get("error", {}).get("message", "댓글 수집 중 오류가 발생했습니다."))
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
    text = re.sub(r"http\S+", " ", str(text))
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
    return text.lower()

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
        st.warning("올바른 유튜브 영상 링크를 입력해주세요.")
    else:
        with st.spinner("댓글을 수집하는 중입니다..."):
            df = fetch_comments(video_id, max_comments)

        if df.empty:
            st.warning("수집된 댓글이 없습니다. 댓글이 비활성화된 영상일 수 있습니다.")
        else:
            df["작성일시"] = pd.to_datetime(df["작성일시"])
            df["날짜"] = df["작성일시"].dt.date
            df["시간"] = df["작성일시"].dt.hour

            st.success(f"총 {len(df)}개의 댓글을 수집했습니다.")

            st.subheader("📋 수집 댓글 데이터")
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

            st.subheader("🕒 날짜별 댓글 추이")
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

            st.subheader("👍 좋아요 수 분석")
            top_likes = df.sort_values("좋아요수", ascending=False).head(10)
            fig_likes = px.bar(
                top_likes,
                x="좋아요수",
                y="댓글",
                orientation="h",
                title="좋아요 수가 많은 댓글 Top 10"
            )
            st.plotly_chart(fig_likes, use_container_width=True)

            st.subheader("☁️ 자주 등장하는 단어 워드클라우드")
            word_counts = get_word_counts(df["댓글"])

            if word_counts:
                wc = WordCloud(
                    font_path="NanumGothic.ttf",
                    width=1000,
                    height=500,
                    background_color="white"
                ).generate_from_frequencies(word_counts)

                fig, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)

                st.subheader("🔤 자주 등장한 단어 Top 20")
                word_df = pd.DataFrame(word_counts.most_common(20), columns=["단어", "빈도"])
                st.dataframe(word_df, use_container_width=True)
            else:
                st.info("워드클라우드를 만들 수 있는 단어가 부족합니다.")