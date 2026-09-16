import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("STREAMLIT_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="EgoBiz Wiki",
    page_icon="📚",
    layout="centered",
)

st.title("EgoTech Solutions")
st.caption("EgoBiz Wiki — ИИ-ассистент по корпоративной базе знаний")

query = st.text_input(
    "Ваш вопрос",
    placeholder="Например: Как подключиться к корпоративному VPN?",
)

if st.button("Задать вопрос", type="primary"):
    if not query.strip():
        st.warning("Введите вопрос.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"query": query},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            st.subheader("Ответ")
            st.write(data["answer"])

            sources = data.get("sources", [])
            if sources:
                st.subheader("Источники")
                for source in sources:
                    st.write(
                        f"- **{source['title']}** "
                        f"(`{source['source']}`)"
                    )

        except requests.RequestException as exc:
            st.error(
                "Не удалось получить ответ от API. "
                "Убедитесь, что FastAPI запущен."
            )
            st.caption(f"Ошибка подключения: {exc}")
