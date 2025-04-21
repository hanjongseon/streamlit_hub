import streamlit as st
import pandas as pd
import numpy as np
import fasttext
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import io
import os  # 파일 삭제를 위해 추가
import pymongo
import datetime
import time
from telegram import Bot
from ssh.ssh_connect import execute_ssh_command as sh

# 텔레그램 봇 설정
bot = Bot(token='524563424:AAEosELj0cDxdNWwDQKwjWuzqpFjnVrdFWQ')

# 비동기 메시지 전송 함수
def send_pub_message(text, type="pub"):
    chat_id = "-4033624555" if type == "pub" else "-347361310"
    bot.send_message(chat_id=chat_id, text=text)

# MongoDB 연결
connection = pymongo.MongoClient("localhost", 27024)

def main():
    #st.title("유사도 계산기")
    
    # 파일 업로드
    uploaded_file = st.file_uploader("txt 파일을 업로드하세요", type=["txt"])

    if uploaded_file is not None:
        try:
            # 파일이 비어 있는지 확인
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            if len(file_content) == 0:
                st.error("업로드된 파일이 비어 있습니다. 다시 확인해주세요.")
                return
            uploaded_file.seek(0)  # 파일 포인터를 다시 처음으로 이동

            # 파일 미리보기 (UTF-8 → EUC-KR 순으로 시도)
            try:
                preview_data = pd.read_table(uploaded_file, nrows=5, sep="|", encoding="utf-8")
            except Exception:
                uploaded_file.seek(0)  # 다시 처음으로 이동
                preview_data = pd.read_table(uploaded_file, nrows=5, sep="|", encoding="euc-kr")

            # 데이터 미리보기 출력
            if preview_data.empty:
                st.error("파일에 데이터가 없습니다. 다시 확인해주세요.")
                return

            st.write("데이터 미리보기:")
            st.dataframe(preview_data)

            # 칼럼 선택
            columns = list(preview_data.columns)
            col_ori = st.selectbox("주소 칼럼을 선택하세요", columns)

            if st.button("고유번호수집"):
                # 선택한 칼럼이 존재하는지 확인
                if col_ori not in columns:
                    st.error(f"선택한 칼럼 '{col_ori}'이(가) 존재하지 않습니다. 다시 확인하세요.")
                    return

                with st.spinner("전체 데이터를 읽고 있습니다."):
                    try:
                        uploaded_file.seek(0)
                        full_data = pd.read_table(uploaded_file, sep="|", usecols=[col_ori], encoding="utf-8")
                    except Exception:
                        uploaded_file.seek(0)
                        full_data = pd.read_table(uploaded_file, sep="|", usecols=[col_ori], encoding="euc-kr")

                    if full_data.empty:
                        st.error("선택한 칼럼에 데이터가 없습니다. 다시 확인해주세요.")
                        return

                    df = full_data.dropna().drop_duplicates()
                    df.columns = ['ADDR_NM']

                # 진행 상태 표시
                progress_bar = st.progress(0)
                progress_bar.progress(10)
                info_placeholder = st.empty()

                # FastText 모델 준비
                info_placeholder.info("작업을 위한 사전 설정 진행")

                with st.spinner("DB 업로드 중..."):
                    connection.hanjongseon.IROS_LIST.drop()
                    connection.hanjongseon.INSTANCE_STATUS.drop()
                    connection.hanjongseon.RESP.drop()

                    if not df.empty:
                        connection.hanjongseon.IROS_LIST.insert_many(df.to_dict('records'))
                    else:
                        st.error("DB에 저장할 데이터가 없습니다.")
                        return

                info_placeholder.success("VPN 작업을 위해 DB로 이동을 시작합니다.")
                progress_bar.progress(30)

                with st.spinner("WSL 접속 중..."):                    
                    try:
                        sh("cd ~/project/python_ovpn && docker compose up -d --scale vpn_app=10")
                        time.sleep(5)
                    except :
                        pass

                info_placeholder.success("ssh command 완료")
                info_placeholder.info("VPN 세팅 시작")

                with st.spinner("수집작업 진행 중..."):
                    while True:
                        #info_placeholder.success("1수집작업 완료")
                        result = sh("docker stats --no-stream")                                            
                        info_placeholder.info(f"{result}")
                        if isinstance(result, list):
                            result = join(result[1:])  # 리스트라면 줄바꿈으로 연결
                        elif not isinstance(result, str):
                            result = str(result)  # 혹시라도 다른 타입이면 문자열 변환
                        container_ps_list = result.split("\n")                        
                        info_placeholder.info(f"{container_ps_list}")
                        if sum("python_ovpn-vpn_app" in i for i in container_ps_list) == 0:
                            break
                        else:
                            info_placeholder.info("수집이 아직 진행중입니다.")
                            time.sleep(5)
                        info_placeholder.success("수집작업 완료")

                info_placeholder.success("수집작업 완료")
                full_data = pd.DataFrame(connection.hanjongseon.RESP.find({}, {"_id": 0}))
                full_data.drop('rd_addr_detail', axis=1, inplace=True)
                #full_data['rd_addr_detail'] = full_data['rd_addr_detail'].str.replace("\\<.*?\\>", "", regex=True)
                full_data['real_indi_cont_detail'] = full_data['real_indi_cont_detail'].str.replace("\\<.*?\\>", "", regex=True)
                full_data['addItem'] = full_data['addItem'].str.replace("\\<.*?\\>", "", regex=True)                
                progress_bar.progress(80)


                @st.cache_data
                def convert_df(df):
                    output = io.StringIO()
                    df.to_csv(output, index=False, sep="|", encoding="utf-8-sig")  # 🔹 UTF-8-SIG로 저장
                    processed_data = output.getvalue()
                    return processed_data


                excel_data = convert_df(full_data)
                now = datetime.datetime.now()
                formatted_date = now.strftime("%Y%m%d_%H%M%S")

                # 다운로드 버튼을 통해 원하는 위치에 파일 저장
                st.download_button(
                    label="결과 파일 다운로드",
                    data=excel_data,
                    file_name=f"고유번호스크래핑_결과_{formatted_date}.txt",
                    mime="text/plain"
                )
                sh("cd ~/project/python_ovpn && docker compose down")
                info_placeholder.success("작업이 완료되었습니다.")
                progress_bar.progress(100)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
