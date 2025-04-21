import streamlit as st
import pandas as pd
#import snowflake.connector
import streamlit_option_menu
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import st_folium  # streamlit_folium에서 st_folium 
import polars as pl
from sqlalchemy import create_engine
import plotly.express as px

#e "D:\\project\\streamlit_hub\\multiple_page\\pre_make.py" 이거 먼저 실행


# 페이지 레이아웃 설정
st.set_page_config(
    page_title="My Dashboard",
    layout="centered"
)

# 시도별 연도별 데이터 수
@st.cache_resource
def load_pivot_sido_year_summary():
    return pd.read_csv("d:/토지_AVM/시도별_연도별_데이터_수_20204.csv", index_col=0)

pivot_sido_year_summary = load_pivot_sido_year_summary()


@st.cache_resource
def load_sido_center():
    res = pd.read_csv("d:/토지_AVM/시도별_중심좌표.csv")
    res.columns = ['SIDO', 'LON', 'LAT']
    return res

sido_center = load_sido_center()


@st.cache_resource
def load_ratio_by_use():
    return pl.read_parquet("d:/토지_AVM/용도지역별_격차율.parquet")

ratio_by_use = load_ratio_by_use()

@st.cache_resource
def load_ratio_by_use2():
    return pl.read_parquet("d:/토지_AVM/지목별_격차율.parquet")

ratio_by_use2 = load_ratio_by_use2()

@st.cache_resource
def load_ratio_by_use3():
    return pl.read_parquet("d:/토지_AVM/이용상황별_격차율.parquet")

ratio_by_use3 = load_ratio_by_use3()

#임포트
# 사이드바에서 선택한 결과를 본문에 표시

uri = 'mysql+pymysql://hanjongseon:gonggam1234@localhost:3306/GONGGAM'
engine = create_engine(uri)

# 5. Pandas DataFrame을 데이터베이스에 쓰기
table_name = "REAL_SALES_ORIGIN"

@st.cache_data
def load_data(sql_query = "SELECT * FROM gonggam.REAL_SALES_ORIGIN LIMIT 5;"):        
    data = pd.read_sql(sql_query, engine)
    return data

df = load_data()

with st.sidebar:
    selected = option_menu(
        menu_title="",
        options=["MAIN", "실거래","주변사례","RATIO정보"],
        icons=[None,"credit-card","globe","percent"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"background-color": "#f0f2f6"},
            "nav-link": {"font-size": "13px", "text-align": "left", "margin":"0px", "--hover-color": "#cdcfd4"},
            "nav-link-selected": {"background-color": "#dadfe9", 'font-weight': 'bold', 'color': 'black'},
        }
    )

# 본문에 결과물 표시
if selected == "실거래":    
    selected_sido = st.sidebar.selectbox("시도", sido_center['SIDO'].unique())
    sub_df = load_data(f'SELECT SIDO AS 시도, 지목명 AS 지목, 용도지역명1 AS 용도지역, 토지이동상황 AS 토지이용상황, SALE_TYPE AS 매매유형, LAND_PRICE_PER_SQUARE FROM gonggam.real_sales_origin WHERE SIDO="{selected_sido}";')
    sub_df = sub_df.groupby('지목').apply(lambda group: 
        group[(group['LAND_PRICE_PER_SQUARE'] > (group['LAND_PRICE_PER_SQUARE'].quantile(0.25) - 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25)))) & 
        (group['LAND_PRICE_PER_SQUARE'] < (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) + 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25))))])
    sub_df['LAND_PRICE_PER_SQUARE'] = sub_df['LAND_PRICE_PER_SQUARE'].astype(float)
    fig = px.box(sub_df, x='지목', y='LAND_PRICE_PER_SQUARE')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    sub_df = sub_df.groupby('용도지역').apply(lambda group: 
        group[(group['LAND_PRICE_PER_SQUARE'] > (group['LAND_PRICE_PER_SQUARE'].quantile(0.25) - 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25)))) & 
        (group['LAND_PRICE_PER_SQUARE'] < (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) + 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25))))])
    sub_df['LAND_PRICE_PER_SQUARE'] = sub_df['LAND_PRICE_PER_SQUARE'].astype(float)
    fig = px.box(sub_df, x='용도지역', y='LAND_PRICE_PER_SQUARE')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    sub_df = sub_df.groupby('토지이용상황').apply(lambda group: 
        group[(group['LAND_PRICE_PER_SQUARE'] > (group['LAND_PRICE_PER_SQUARE'].quantile(0.25) - 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25)))) & 
        (group['LAND_PRICE_PER_SQUARE'] < (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) + 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25))))])
    sub_df['LAND_PRICE_PER_SQUARE'] = sub_df['LAND_PRICE_PER_SQUARE'].astype(float)
    fig = px.box(sub_df, x='토지이용상황', y='LAND_PRICE_PER_SQUARE')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    sub_df = sub_df.groupby('매매유형').apply(lambda group: 
        group[(group['LAND_PRICE_PER_SQUARE'] > (group['LAND_PRICE_PER_SQUARE'].quantile(0.25) - 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25)))) & 
        (group['LAND_PRICE_PER_SQUARE'] < (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) + 1.5 * (group['LAND_PRICE_PER_SQUARE'].quantile(0.75) - group['LAND_PRICE_PER_SQUARE'].quantile(0.25))))])
    sub_df['LAND_PRICE_PER_SQUARE'] = sub_df['LAND_PRICE_PER_SQUARE'].astype(float)
    fig = px.bar(sub_df, x='매매유형', y='LAND_PRICE_PER_SQUARE')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    
    st.write("시도별 ratio box랑 RATIO 표시")
    
    # 한국 지도 표시
    map_korea = folium.Map(location=[36.5, 127.5], zoom_start=7)  # 한국 중심 좌표

    # 샘플 폴리곤 추가
    polygon1 = folium.Polygon(
        locations=[[37.0, 126.5], [37.5, 126.5], [37.5, 127.0], [37.0, 127.0]],
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.5,
        popup='Sample Polygon 1'
    )
    polygon1.add_to(map_korea)

    polygon2 = folium.Polygon(
        locations=[[36.5, 126.0], [37.0, 126.0], [37.0, 126.5], [36.5, 126.5]],
        color='green',
        fill=True,
        fill_color='green',
        fill_opacity=0.5,
        popup='Sample Polygon 2'
    )
    polygon2.add_to(map_korea)
    # 폴리곤 위에 텍스트 표시
    folium.Marker(location=[37.25, 126.75], icon=folium.features.DivIcon(icon_size=(150,36), icon_anchor=(12,27), html='<div style="font-size: 30pt; font-weight: bold; color : black">1</div>')).add_to(map_korea)
    folium.Marker(location=[36.75, 126.25], icon=folium.features.DivIcon(icon_size=(150,36), icon_anchor=(12,27), html='<div style="font-size: 30pt; font-weight: bold; color : black">2</div>')).add_to(map_korea)

    st_folium(map_korea, width=700, height=500, use_container_width=True)  # Streamlit에서 folium 지도를 표시
    # 지도 아래쪽에 df의 head값 출력
    
    st.dataframe(df, use_container_width=True)

if selected == "주변사례":
    st.title("여기에 주변사례 결과물이 표시")
    st.write("지도 시각화 한다음에 덴서티형태나 point 형태 표시")
if selected == "RATIO정보":
    st.title("여기에 RATIO정보 결과물이 표시")
    st.write("radiobox로 년도랑, 시도 나오게 하고 그에 따른 RATIO 표시")
# 선택되어 있지 않은 상태의 디폴트 페이지
if selected == "MAIN":
    fig1 = px.bar(pivot_sido_year_summary, color_discrete_sequence=['slateblue','steelblue', 'powderblue', 'skyblue', 'lightsteelblue', 'lightskyblue', 'cadetblue', 'cornflowerblue', 'royalblue', 'midnightblue', 'navy', 'darkslateblue', 'indigo', 'peru', 'teal', 'turquoise', 'dodgerblue'], orientation='h')  # 임시로 색상을 정의하고 방향을 가로로 설정
    fig1.update_layout(yaxis_ticklen=0, plot_bgcolor='white', title_x=0.1, title_font_size=15, font=dict(size=9), xaxis_title=None, yaxis_title=None)
    fig1.update_layout(legend_title_text='거래년도')
    fig1.update_layout(title_text='')  # 제목을 비워 제목을 없애는 방법
    fig1.update_yaxes(tickfont=dict(size=8), categoryorder='total ascending')  # y축 텍스트 사이즈만 줄이고 오름차순으로 정렬
    #fig1.update_layout(config={'displayModeBar': False})
    #fig1.update_layout(dragmode=False)  # 확대/축소 기능 비활성화
    #fig1.update_layout(config=dict(displayModeBar=False))  # 툴바 숨기기

    # Streamlit 레이아웃: 두 열로 나누기
    col1, col2 = st.columns(2)

    res2 = pivot_sido_year_summary.sum(axis=1).rename('총합').reset_index()
    res2 = res2.merge(sido_center, on='SIDO', how='left')
    #res2['총합'] = res2['총합'].astype(int).apply(lambda x: '{:,}'.format(x))
    with col1:
        #st.write("시도별 실거래량 분포", style={'font-size': '26px', 'font-weight': 'normal', 'text-align': 'center'})
        st.markdown("##### 시도별 실거래량 분포")
        map_korea = folium.Map(location=[36.2, 131.2], zoom_start=6.2, tiles='CartoDB.Positron', attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.', zoom_control=True)  
        sido_colors = {'서울특별시': 'slateblue', '부산광역시': 'steelblue', '대구광역시': 'powderblue', '인천광역시': 'skyblue', '광주광역시': 'lightsteelblue', '대전광역시': 'lightskyblue', '울산광역시': 'cadetblue', '세종특별자치시': 'cornflowerblue', '경기도': 'royalblue', '강원도': 'midnightblue', '충청북도': 'navy', '충청남도': 'darkslateblue', '전라북도': 'indigo', '전라남도': 'darkgreen', '경상북도': 'teal', '경상남도': 'turquoise', '제주특별자치도': 'dodgerblue'}
        for _, row in res2.iterrows():
            color = sido_colors.get(row['SIDO'], 'black')  # SIDO에 해당하는 색을 가져오거나 기본값으로 'blue'를 설정
            folium.CircleMarker(location=[row['LAT'], row['LON']], radius=row['총합']/10000*2, color='black', fill=True, fill_color=color, fill_opacity=0.5, tooltip=f"{row['SIDO']}:\n {int(row['총합']):,}").add_to(map_korea)
        st_folium(map_korea, width=700, height=400, use_container_width=True)  # Streamlit에서 folium 지도를 표시
    with col2:
        st.markdown("##### 시도별, 연도별 거래량분포")
        #st.write("시도별, 연도별 거래량분포", style={'font-size': '26px', 'font-weight': 'normal', 'text-align': 'center'})
        st.plotly_chart(fig1, config={'responsive': True}, use_container_width=True)     
        
    st.markdown("---")
    fig2 = px.scatter(pivot_sido_year_summary.iloc[:,1:].T, x=pivot_sido_year_summary.iloc[:,1:].T.index, y=pivot_sido_year_summary.iloc[:,1:].T.columns, color_discrete_sequence=['slateblue','steelblue', 'powderblue', 'skyblue', 'lightsteelblue', 'lightskyblue', 'cadetblue', 'cornflowerblue', 'royalblue', 'midnightblue', 'navy', 'darkslateblue', 'indigo', 'darkgreen', 'teal', 'turquoise', 'dodgerblue'])
    fig2.update_traces(mode='lines+markers')
    
    st.markdown("##### 시도별 거래량의 시계열 변화량")
    fig2.update_layout(xaxis_title='연도', yaxis_title='거래량', title_text='', plot_bgcolor='white', title_font_size=15, font=dict(size=12))
    st.plotly_chart(fig2, config={'responsive': True}, use_container_width=True)
        # Streamlit 레이아웃: 두 열로 나누기    
    st.markdown("---")
    col3, col4, col5 = st.columns(3)
    with col3 :
        st.markdown("##### 지목별 격차율")        
        fig3 = px.bar(ratio_by_use2, x="지목명", y="격차율", color="격차율", title="", color_discrete_sequence=['slateblue','steelblue', 'powderblue', 'skyblue', 'lightsteelblue', 'lightskyblue', 'cadetblue', 'cornflowerblue', 'royalblue', 'midnightblue', 'navy', 'darkslateblue', 'indigo', 'darkgreen', 'teal', 'turquoise', 'dodgerblue'])
        fig3.update_layout(plot_bgcolor='white', height=200, xaxis_title="", yaxis_title="")  # 높이를 400으로 설정하여 높이를 줄이고 x,y축 라벨을 공백으로 세팅
        st.plotly_chart(fig3, config={'responsive': True}, use_container_width=True, key='fig3')
    with col4 :
        st.markdown("##### 용도지역별 격차율")        
        fig4 = px.bar(ratio_by_use, x="용도지역명1", y="격차율", color="격차율", title="", color_discrete_sequence=['slateblue','steelblue', 'powderblue', 'skyblue', 'lightsteelblue', 'lightskyblue', 'cadetblue', 'cornflowerblue', 'royalblue', 'midnightblue', 'navy', 'darkslateblue', 'indigo', 'darkgreen', 'teal', 'turquoise', 'dodgerblue'])
        fig4.update_layout(plot_bgcolor='white', height=200, xaxis_title="", yaxis_title="")  # 높이를 400으로 설정하여 높이를 줄이고 x,y축 라벨을 공백으로 세팅
        st.plotly_chart(fig4, config={'responsive': True}, use_container_width=True, key='fig4')
    with col5 :
        st.markdown("##### 토지이용상황 격차율")        
        fig5 = px.bar(ratio_by_use3, x="토지이동상황", y="격차율", color="격차율", title="", color_discrete_sequence=['slateblue','steelblue', 'powderblue', 'skyblue', 'lightsteelblue', 'lightskyblue', 'cadetblue', 'cornflowerblue', 'royalblue', 'midnightblue', 'navy', 'darkslateblue', 'indigo', 'darkgreen', 'teal', 'turquoise', 'dodgerblue'])
        fig5.update_layout(plot_bgcolor='white', height=200, xaxis_title="", yaxis_title="")  # 높이를 400으로 설정하여 높이를 줄이고 x,y축 라벨을 공백으로 세팅
        st.plotly_chart(fig5, config={'responsive': True}, use_container_width=True, key='fig5')


st.markdown("""
> *Updated on the 5th of every month by the scheduler [plot data pre-make]*  
    *Updated on the 4th of every month by the scheduler [sample]*
""")
