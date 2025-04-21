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
from telegram import Bot

# 텔레그램 봇 설정
bot = Bot(token='524563424:AAEosELj0cDxdNWwDQKwjWuzqpFjnVrdFWQ')

# 비동기 메시지 전송 함수
def send_pub_message(text, type="pub"):
    chat_id = "-4033624555" if type == "pub" else "-347361310"
    bot.send_message(chat_id=chat_id, text=text)


connection = pymongo.MongoClient("192.168.101.237", 27017)

def main():
    global connection
    #st.title("유사도 계산기")
    
    # 파일 업로드
    uploaded_file = st.file_uploader("Excel 파일을 업로드하세요", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # 엑셀 파일의 첫 5개 행만 읽기                                           
            preview_data = pd.read_excel(uploaded_file, nrows=5)
            st.write("데이터 미리보기:")
            st.dataframe(preview_data)

            # 칼럼 선택
            columns = list(preview_data.columns)
            col_ori = st.selectbox("인덱스가 될 칼럼을 선택하세요", columns)
            col1 = st.selectbox("첫 번째 텍스트 칼럼을 선택하세요", columns)
            col2 = st.selectbox("두 번째 텍스트 칼럼을 선택하세요", columns)
            
            if st.button("유사도 계산"):
                # 전체 데이터 읽기
                with st.spinner("전체 데이터를 읽고 있습니다."):
                    if col_ori in [col1, col2] :
                        st.info("인덱스 칼럼이 비교 대상과 동일하여 제외합니다.")
                        full_data = pd.read_excel(uploaded_file,usecols=[col1, col2])
                    else :                
                        full_data = pd.read_excel(uploaded_file,usecols=[col_ori, col1, col2])
                    df = full_data[[col1, col2]].dropna()
                    df.columns = ['ORI_DATA', 'TARGET']
                
                # 진행 상태 표시
                progress_bar = st.progress(0)
                progress_bar.progress(10)
                info_placeholder = st.empty()
                # FastText 모델 준비
                info_placeholder.info("FastText 모델을 준비하고 있습니다.")
                with st.spinner("FastText 모델을 학습 중입니다."):
                    with open("text_data.txt", "w", encoding="utf-8") as f:
                        for text in df['ORI_DATA'].tolist() + df['TARGET'].tolist():
                            f.write(text + "\n")
                    model = fasttext.train_unsupervised('text_data.txt', model='skipgram')
                info_placeholder.success("FastText 모델 반영을 완료했습니다.")
                progress_bar.progress(40)

                # 문자와 숫자 분리 후 임베딩 생성 함수
                def get_separated_embeddings(text, model):
                    words = re.sub(r'\d+', '', text)  # 문자만 추출
                    numbers = re.findall(r'\d+', text)  # 숫자만 추출

                    word_vectors = [model.get_word_vector(word.strip()) for word in words.split() if word.strip()]
                    number_vectors = [model.get_word_vector(number) for number in numbers if number]

                    word_embedding = np.mean(word_vectors, axis=0) if word_vectors else np.zeros(model.get_dimension())
                    number_embedding = np.mean(number_vectors, axis=0) if number_vectors else np.zeros(model.get_dimension())

                    return word_embedding, number_embedding

                # TF-IDF 계산
                info_placeholder.info("TF-IDF 가중치를 계산하고 있습니다. 다소 시간이 소요됩니다.")
                vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
                combined_text = df['ORI_DATA'].tolist() + df['TARGET'].tolist()
                vectorizer.fit(combined_text)
                embeddings_A_tfidf = vectorizer.transform(df['ORI_DATA'].tolist())
                embeddings_B_tfidf = vectorizer.transform(df['TARGET'].tolist())
                tfidf_similarities = cosine_similarity(embeddings_A_tfidf, embeddings_B_tfidf).diagonal()
                info_placeholder.success("계산이 모두 반영되었습니다!")
                progress_bar.progress(60)

                # FastText 문자 유사도 및 숫자 유사도 계산
                info_placeholder.info("모델들을 반영하여 유사도를 계산하고 있습니다.")
                text_similarities = []
                number_similarities = []
                for i in range(len(df)):
                    word_embedding_A, number_embedding_A = get_separated_embeddings(df['ORI_DATA'].iloc[i], model)
                    word_embedding_B, number_embedding_B = get_separated_embeddings(df['TARGET'].iloc[i], model)

                    text_similarity1 = cosine_similarity([word_embedding_A], [word_embedding_B])[0][0]
                    text_similarity2 = cosine_similarity([word_embedding_B], [word_embedding_A])[0][0]
                    text_similarity = max([text_similarity1, text_similarity2])
                    text_similarities.append(text_similarity)

                    numbers_A = re.findall(r'\d+', df['ORI_DATA'].iloc[i])
                    numbers_B = re.findall(r'\d+', df['TARGET'].iloc[i])
                    number_similarity = 1.0 if numbers_A == numbers_B else 0.5
                    number_similarities.append(number_similarity)

                progress_bar.progress(80)

                final_similarities = [
                    0.3 * tfidf_similarities[i] + 0.2 * text_similarities[i] + 0.5 * number_similarities[i]
                    for i in range(len(df))
                ]

                # 결과 저장: 원본 데이터에 유사도 추가
                full_data['Similarity'] = None
                full_data.loc[df.index, 'Similarity'] = final_similarities

                # 데이터 정렬 및 인덱스 재설정 (자동 저장 제거)
                full_data.sort_values(by=["Similarity"], ascending=False, inplace=True)
                full_data.reset_index(drop=True, inplace=True)

                # 중간 파일 삭제
                if os.path.exists("text_data.txt"):
                    os.remove("text_data.txt")

                # 결과 파일 다운로드
                info_placeholder.success("유사도 계산이 완료되었습니다.")
                st.write("결과 데이터 미리보기:")
                st.dataframe(full_data.head())

                # 데이터 업로드       
                info_placeholder.info("데이터를 DB에 업로드합니다.")                         
                
                with st.spinner("DB에 업로드 중입니다..."):                    
                    connection.hanjongseon.MATCHING_DATA.insert_many(full_data.loc[:,[col1, col2,"Similarity"]].rename(columns={col1:'ORI_DATA', col2: 'TARGET'}).to_dict('records'))
                send_pub_message(f"{str(uploaded_file)} uploaded") 
                info_placeholder.success("업로드가 완료되었습니다.")                
                progress_bar.progress(90)
                
                @st.cache_data
                def convert_df(df):
                    # 메모리 버퍼에 엑셀 파일 저장
                    output = io.BytesIO()
                    writer = pd.ExcelWriter(output, engine='xlsxwriter')
                    df.to_excel(writer, index=False)
                    writer.close()
                    processed_data = output.getvalue()
                    return processed_data

                excel_data = convert_df(full_data)
                now = datetime.datetime.now()
                formatted_date = now.strftime("%Y%m%d_%H%M%S")
                
                # 다운로드 버튼을 통해 원하는 위치에 파일 저장
                st.download_button(
                    label="결과 파일 다운로드",
                    data=excel_data,
                    file_name = f"유사도_결과_{formatted_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )                
                info_placeholder.success("작업이 완료되었습니다.")
                progress_bar.progress(100)
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
