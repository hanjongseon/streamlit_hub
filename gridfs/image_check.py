import streamlit as st
import pymongo
from pymongo import MongoClient
from gridfs import GridFS
from difflib import get_close_matches
from PIL import Image
import io
import re

# 페이지 설정: 넓은 레이아웃
st.set_page_config(page_title="위반건축물 이미지 확인", layout="wide")

# MongoDB 연결 설정
@st.cache_resource
def get_db_connection():
    client = MongoClient('mongodb://192.168.101.237:27017')
    db = client['VIO']
    fs = GridFS(db)
    return db, fs

# 파일명 정리: 목록 표시용과 로드용 원본 파일명 매핑
def get_clean_filenames(db):
    filenames = db['fs.files'].distinct('filename')  # 모든 파일명 가져오기
    clean_to_raw = {
        re.sub("_[0-9]+건$", "", filename.split(']')[-1].replace('.png', '').strip()): filename for filename in filenames
    }
    return clean_to_raw

# 유사도 높은 파일명 검색 함수
def get_similar_filenames(input_text, clean_to_raw, max_results=20):
    clean_filenames = list(clean_to_raw.keys())  # 정리된 파일명 목록
    matches = get_close_matches(input_text, clean_filenames, n=max_results, cutoff=0.1)  # 유사도 높은 순으로 최대 max_results개
    return matches

# GridFS에서 파일 읽기 및 이미지 변환
def get_image_from_gridfs(raw_filename, fs):
    file_data = fs.find_one({'filename': raw_filename})
    if file_data:
        image = Image.open(io.BytesIO(file_data.read()))  # 이미지를 메모리에서 로드
        return image
    return None

# 이미지 가운데 크롭 함수
def crop_center(image, crop_width, crop_height):
    img_width, img_height = image.size
    left = (img_width - crop_width) / 2
    top = (img_height - crop_height) / 2
    right = (img_width + crop_width) / 2
    bottom = (img_height + crop_height) / 2
    return image.crop((left, top, right, bottom))

# Streamlit 앱
def main():
    st.title("위반건축물 이미지 확인")
    st.write("검색어를 입력하고 목록에서 파일을 선택하세요.")

    # CSS 스타일 추가
    st.markdown(
        """
        <style>
        .custom-text-input input {
            width: 300px !important; /* 원하는 너비 설정 */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # MongoDB 연결
    db, fs = get_db_connection()

    # 파일명 매핑 (정리된 파일명 → 원본 파일명)
    clean_to_raw = get_clean_filenames(db)

    # 텍스트 입력 (커스텀 클래스 적용)
    input_text = st.text_input(
        "검색어를 입력하세요:", key="search", placeholder="검색어를 입력하세요"
    )
    st.markdown('<div class="custom-text-input"></div>', unsafe_allow_html=True)

    # 유사 파일 목록 초기화
    selected_clean_filename = None
    if input_text:  # 검색어가 입력된 경우
        similar_filenames = get_similar_filenames(input_text, clean_to_raw)

        if similar_filenames:
            # 실시간 추천 목록 표시
            selected_clean_filename = st.selectbox("추천 파일 목록:", similar_filenames, key="select")
        else:
            st.warning("유사한 파일을 찾을 수 없습니다.")
    
    # 이미지 표시 및 크롭
    if selected_clean_filename:
        raw_filename = clean_to_raw.get(selected_clean_filename)  # 원본 파일명 찾기
        image = get_image_from_gridfs(raw_filename, fs)
        if image:
            # 사용자 지정 크롭 크기 설정
            crop_width = 1100#st.number_input("크롭할 너비 (px):", min_value=10, max_value=image.size[0], value=1100)
            crop_height = 900#st.number_input("크롭할 높이 (px):", min_value=10, max_value=image.size[1], value=800)

            # 크롭된 이미지
            cropped_image = crop_center(image, crop_width, crop_height)

            # 크롭된 이미지 표시
            st.image(
                cropped_image,
                caption=f"Filename: {selected_clean_filename} (크롭된 이미지)",
                use_column_width=True,
                output_format="PNG"
            )
        else:
            st.error("이미지를 불러올 수 없습니다.")

if __name__ == "__main__":
    main()
