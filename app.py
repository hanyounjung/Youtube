import streamlit as st

st.set_page_config(
    page_title="MBTI 진로 & 포켓몬 추천",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 MBTI 진로 & 포켓몬 캐릭터 추천")
st.write("MBTI를 선택하면 어울리는 진로와 포켓몬 캐릭터를 추천해줍니다.")

mbti_data = {
    "INTJ": {
        "nickname": "전략가형",
        "career": ["데이터 분석가", "인공지능 개발자", "전략기획자", "연구원", "소프트웨어 엔지니어"],
        "pokemon": "뮤츠",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/150.png",
        "reason": "논리적이고 독립적이며 전략적으로 문제를 해결하는 성향이 강합니다."
    },
    "INTP": {
        "nickname": "논리술사형",
        "career": ["프로그래머", "과학자", "게임 개발자", "정보보안 전문가", "발명가"],
        "pokemon": "메타몽",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/132.png",
        "reason": "호기심이 많고 새로운 아이디어를 탐구하는 데 강점이 있습니다."
    },
    "ENTJ": {
        "nickname": "통솔자형",
        "career": ["CEO", "프로젝트 매니저", "변호사", "경영 컨설턴트", "창업가"],
        "pokemon": "리자몽",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png",
        "reason": "목표 지향적이고 리더십이 뛰어나 조직을 이끄는 역할에 잘 어울립니다."
    },
    "ENTP": {
        "nickname": "토론가형",
        "career": ["마케터", "기획자", "광고 전문가", "스타트업 창업가", "방송인"],
        "pokemon": "고라파덕",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/54.png",
        "reason": "아이디어가 풍부하고 유연한 사고로 새로운 도전을 즐깁니다."
    },
    "INFJ": {
        "nickname": "옹호자형",
        "career": ["상담가", "교사", "작가", "사회복지사", "심리학자"],
        "pokemon": "라티아스",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/380.png",
        "reason": "사람을 깊이 이해하고 의미 있는 가치를 추구하는 성향이 있습니다."
    },
    "INFP": {
        "nickname": "중재자형",
        "career": ["작가", "디자이너", "일러스트레이터", "상담사", "콘텐츠 크리에이터"],
        "pokemon": "이브이",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/133.png",
        "reason": "감수성이 풍부하고 자신만의 가능성과 개성을 중요하게 생각합니다."
    },
    "ENFJ": {
        "nickname": "선도자형",
        "career": ["교사", "강사", "인사담당자", "상담가", "사회운동가"],
        "pokemon": "피카츄",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
        "reason": "타인에게 긍정적인 영향을 주고 함께 성장하는 것을 좋아합니다."
    },
    "ENFP": {
        "nickname": "활동가형",
        "career": ["유튜버", "홍보 전문가", "이벤트 기획자", "배우", "창작자"],
        "pokemon": "파이리",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png",
        "reason": "에너지가 넘치고 창의적인 표현 활동에 강점이 있습니다."
    },
    "ISTJ": {
        "nickname": "현실주의자형",
        "career": ["공무원", "회계사", "품질관리자", "법무사", "데이터 관리자"],
        "pokemon": "꼬부기",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png",
        "reason": "책임감이 강하고 체계적이며 정확한 업무에 잘 어울립니다."
    },
    "ISFJ": {
        "nickname": "수호자형",
        "career": ["간호사", "교사", "사회복지사", "행정직", "보건의료직"],
        "pokemon": "럭키",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/113.png",
        "reason": "배려심이 깊고 다른 사람을 돕는 일에서 보람을 느낍니다."
    },
    "ESTJ": {
        "nickname": "경영자형",
        "career": ["관리자", "경찰관", "군인", "행정가", "금융 전문가"],
        "pokemon": "거북왕",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/9.png",
        "reason": "규칙과 질서를 중시하며 책임감 있게 조직을 운영합니다."
    },
    "ESFJ": {
        "nickname": "집정관형",
        "career": ["교사", "간호사", "서비스 관리자", "홍보 담당자", "호텔리어"],
        "pokemon": "푸린",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/39.png",
        "reason": "사교성이 좋고 주변 사람들과 조화롭게 협력하는 데 강합니다."
    },
    "ISTP": {
        "nickname": "장인형",
        "career": ["엔지니어", "자동차 정비사", "드론 조종사", "소방관", "기계 설계자"],
        "pokemon": "루카리오",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/448.png",
        "reason": "손으로 직접 만들고 문제를 해결하는 실용적인 능력이 뛰어납니다."
    },
    "ISFP": {
        "nickname": "모험가형",
        "career": ["디자이너", "사진작가", "미용사", "음악가", "플로리스트"],
        "pokemon": "님피아",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/700.png",
        "reason": "감각적이고 예술적인 표현을 즐기며 섬세한 감성이 돋보입니다."
    },
    "ESTP": {
        "nickname": "사업가형",
        "career": ["영업 전문가", "운동선수", "경찰관", "응급구조사", "이벤트 기획자"],
        "pokemon": "잠만보",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png",
        "reason": "활동적이고 상황 판단이 빨라 현장에서 강점을 발휘합니다."
    },
    "ESFP": {
        "nickname": "연예인형",
        "career": ["배우", "가수", "크리에이터", "뷰티 아티스트", "행사 진행자"],
        "pokemon": "토게피",
        "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/175.png",
        "reason": "밝고 활발하며 사람들에게 즐거움을 주는 활동에 잘 어울립니다."
    }
}

mbti = st.selectbox(
    "나의 MBTI를 선택하세요",
    list(mbti_data.keys())
)

result = mbti_data[mbti]

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.image(result["image"], width=220)
    st.subheader(f"추천 포켓몬: {result['pokemon']}")

with col2:
    st.header(f"{mbti} - {result['nickname']}")
    st.write(result["reason"])

    st.subheader("💼 어울리는 진로")
    for job in result["career"]:
        st.write(f"- {job}")

st.divider()

st.info("※ 이 결과는 재미와 진로 탐색 활동을 위한 참고용입니다. 실제 진로 선택은 흥미, 역량, 가치관, 경험을 함께 고려해야 합니다.")
