import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋"
)

st.write("# made by Han 👋")

st.sidebar.success("Select a menu above.")

st.markdown(
    """    
    **👈 Select a demo from the sidebar** to do some projects    
    ### menu description
    1. **plotting demo**
        - 토지 AVM plot 데이터 시각화
    2. **Mapping Demo**
        - 토지 AVM 지도 시각화 
    3. **DataFrame Demo**
        - data description
    4. **similarity calculation**
        - 텍스트의 유사도를 계산하여 우선순위로 정렬하여 데이터 리턴
        - 텍스트 매칭 후 데이터 추출
        - 텍스트 매칭 후 데이터 추출
    
    *※ updated by Han at 2024.12.02*
"""
)
