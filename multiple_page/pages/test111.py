import streamlit as st
from datetime import datetime
from pathlib import Path

# 🔧 CSS 삽입: Dillinger 유사 스타일링
DILLINGER_LIKE_CSS = """
<style>
/* 마크다운 전체 영역 */
.markdown-body {
    font-family: 'Segoe UI', sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #24292e;
    background: #fff;
    padding: 2rem;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
}

/* 코드블럭 */
.markdown-body pre {
    background-color: #f6f8fa;
    padding: 1rem;
    overflow: auto;
    border-radius: 6px;
}

/* 인라인 코드 */
.markdown-body code {
    background-color: #f3f4f6;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 90%;
    font-family: Consolas, monospace;
}

/* 제목 */
.markdown-body h1,
.markdown-body h2,
.markdown-body h3 {
    font-weight: bold;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 0.3rem;
}

/* 리스트 */
.markdown-body ul {
    padding-left: 2rem;
}
</style>
"""

def render_markdown_with_style(md_file_path):
    file_path = Path(md_file_path)

    if not file_path.exists():
        st.error(f"❌ 파일이 존재하지 않습니다: {md_file_path}")
        return

    with open(file_path, encoding="utf-8") as f:
        markdown_content = f.read()

    # 페이지 제목 및 날짜
    st.write(f"### 📄 Git 사용 문서")
    st.write(f"🗓️ {datetime.now().strftime('%Y-%m-%d')}")

    # Dillinger 유사 스타일 삽입
    st.markdown(DILLINGER_LIKE_CSS, unsafe_allow_html=True)

    # 실제 마크다운 내용 출력
    st.markdown(f'<div class="markdown-body">{st.markdown(markdown_content, unsafe_allow_html=False)}</div>', unsafe_allow_html=True)

# 실행 예시
if __name__ == "__main__":
    render_markdown_with_style("G:/내 드라이브/obsidian/VIO/HISTORY.md")
