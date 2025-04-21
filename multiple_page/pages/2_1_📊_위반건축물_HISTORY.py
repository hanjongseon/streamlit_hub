# pages/04_address_verification.py

import streamlit as st
from datetime import datetime


def main():
    st.write(f"#### 📅: {datetime.now().strftime("%Y-%m-%d")}")
    # 파일 경로
    file_path = r"G:\내 드라이브\obsidian\VIO\HISTORY.md"

    try:
        # 파일 내용을 읽어서 표시
        with open(file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()
        st.markdown(markdown_content)  # 파일 내용을 markdown으로 출력
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        st.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
