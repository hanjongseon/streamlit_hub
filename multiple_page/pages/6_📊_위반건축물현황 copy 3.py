import streamlit as st
import requests
import re
from pathlib import Path
import urllib.parse

# Dillinger 스타일 CSS
DILLINGER_CSS = """
<style>
body {
    font-family: 'Segoe UI', sans-serif;
    background: #f9f9f9;
    color: #333;
    line-height: 1.6;
    padding: 2rem;
}
pre {
    background: #f6f8fa;
    padding: 1rem;
    overflow-x: auto;
    border-radius: 6px;
}
code {
    background: #f0f0f0;
    padding: 2px 4px;
    border-radius: 4px;
}
h1, h2, h3 {
    border-bottom: 1px solid #e1e4e8;
    padding-bottom: 0.3rem;
}
ul {
    padding-left: 1.2em;
}
</style>
"""

def clean_markdown(text: str) -> str:
    if text.startswith('\ufeff'):
        text = text.replace('\ufeff', '')
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\u200B]', '', text)
    text = re.sub(r'\[(.*?)\]\((.*?\\.*?)\)', r'[\1](#)', text)
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    return text

def convert_md_file_to_html(md_path: Path, output_dir: Path) -> str:
    try:
        with open(md_path, "r", encoding="utf-8-sig") as f:
            raw_text = f.read()
        clean_text = clean_markdown(raw_text)
        safe_filename = urllib.parse.quote(md_path.stem) + ".md"

        url = "https://dillinger.io/factory/fetch_html"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://dillinger.io/",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "name": safe_filename,
            "unmd": clean_text,
            "formatting": "true",
            "preview": "true"
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            output_dir.mkdir(exist_ok=True)
            html_path = output_dir / md_path.with_suffix(".html").name
            full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{DILLINGER_CSS}</head><body>{response.text}</body></html>"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            return f"✅ {md_path.name} → {html_path.name}"
        else:
            return f"❌ 실패: {md_path.name} (코드 {response.status_code})"
    except Exception as e:
        return f"❌ 예외 발생: {md_path.name} | {str(e)}"

def run_page():
    st.title("📁 마크다운 → Dillinger HTML 변환기")

    input_folder = st.text_input("📂 변환할 마크다운 폴더 경로", value="")
    if input_folder:
        input_path = Path(input_folder)
        if not input_path.is_dir():
            st.error("❌ 해당 경로는 존재하지 않거나 폴더가 아닙니다.")
            return

        output_dir = input_path.parent / "htmls"
        md_files = list(input_path.glob("*.md"))
        if not md_files:
            st.warning("📭 폴더에 .md 파일이 없습니다.")
            return

        st.write(f"🔄 총 {len(md_files)}개의 파일을 변환합니다...")
        with st.spinner("변환 중..."):
            results = []
            for md_file in md_files:
                result = convert_md_file_to_html(md_file, output_dir)
                results.append(result)

        st.success("✅ 변환 완료")
        for r in results:
            st.write(r)

# Streamlit 멀티페이지 구조에서 사용 시
if __name__ == "__main__":
    run_page()
