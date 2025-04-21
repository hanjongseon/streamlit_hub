import streamlit as st
import glob
import os
from streamlit_option_menu import option_menu

# 페이지 설정
st.set_page_config(
    page_title="회의용 HTML 뷰어",
    layout="centered"
)

# HTML 파일 위치
target_dir = "E:/회의용"
filelists = glob.glob(os.path.join(target_dir, "*.html"))

# 파일명이 메뉴 옵션
options = [os.path.basename(f) for f in filelists]

# 메뉴 생성
if len(options) > 0:
    with st.sidebar:
        selected = option_menu(
            menu_title="HTML 파일 목록",
            options=options,
            icons=[None] * len(options),
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"background-color": "#f0f2f6"},
                "nav-link": {"font-size": "13px", "text-align": "left", "margin": "0px", "--hover-color": "#cdcfd4"},
                "nav-link-selected": {"background-color": "#dadfe9", 'font-weight': 'bold', 'color': 'black'},
            }
        )

    # 선택한 파일의 전체 경로
    selected_file = os.path.join(target_dir, selected)

    with open(selected_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # ✅ body에 width: 100% 강제 적용
    styled_html = f"""
    <style>
        body {{ margin: 0; padding: 0; width: 100%; }}
        html {{ width: 100%; }}
    </style>
    {html_content}
    """

    st.components.v1.html(styled_html, height=800, width=None, scrolling=True)

else:
    st.sidebar.warning("⚠️ `.html` 파일이 없습니다.")
    st.stop()
