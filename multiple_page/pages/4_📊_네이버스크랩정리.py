import streamlit as st

# 외부 파일에서 마크다운 불러오기
with open(r"G:\내 드라이브\obsidian\NAVER_매물\NAVER SCRAP 데이터 정리.md", "r", encoding="utf-8") as file:
    markdown_text = file.read()
    st.markdown(markdown_text)