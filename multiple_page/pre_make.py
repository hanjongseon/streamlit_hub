import glob
import re
import plotly.express as px
import polars as pl
import pandas as pd
import numpy as np
list_files = glob.glob(r"D:\토지_AVM\건축단가적용_*.parquet")
list_files = [x for x in list_files if re.search(r"[0-9]{8}\.parquet", x)!=None]
target_file = max(list_files, key=lambda x: int(x.split("_")[-1].replace(".parquet", "")))

# 파일 읽기
df = pl.scan_parquet(target_file).collect()

# inf/-inf → null로 바꾸기
df = df.with_columns([
    pl.when(pl.col(c).is_infinite())
      .then(None)
      .otherwise(pl.col(c))
      .alias(c)
    for c in df.columns if df.schema[c] in [pl.Float32, pl.Float64]
])


uri = "mysql+pymysql://hanjongseon:gonggam1234@localhost:3306/gonggam"

df.write_database(connection=uri, table_name="real_sales_origin", if_table_exists="replace")




df.columns
# 데이터 summary

sido_year_summary = df.group_by(["SIDO", "ACC_YEAR"]).count().sort(["SIDO", "ACC_YEAR"])

sido_year_summary_pd = sido_year_summary.to_pandas()
sido_year_summary_pd['ACC_YEAR'] = sido_year_summary_pd['ACC_YEAR'].astype(str)
pivot_sido_year_summary = sido_year_summary_pd.pivot(index='SIDO', columns = 'ACC_YEAR', values='count')

pivot_sido_year_summary.to_csv("d:/토지_AVM/시도별_연도별_데이터_수_20204.csv", index=True)

# fig = px.bar(pivot_sido_year_summary, x=pivot_sido_year_summary.columns, y=pivot_sido_year_summary.index, color_discrete_sequence=px.colors.qualitative.Set1)
# fig.update_layout(title_text='시도별 연도별 데이터 수', xaxis_title='거래량', yaxis_title='지역', yaxis_ticklen=0, plot_bgcolor='white', title_x=0.33, title_font_size=24, title_xanchor="right")
# fig.update_layout(legend_title_text='거래년도')
# fig.show()


sido_center = df.select(['SIDO', 'X', 'Y']).group_by(['SIDO']).agg(pl.col('X').mean(), pl.col('Y').mean()).sort(['SIDO'])


import geopandas as gpd
from shapely.geometry import Point
from pyproj import Proj, transform
from pyproj import CRS, Transformer

# 좌표 변환을 위한 프로젝션 정의

inProj = CRS.from_proj4("+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs")
outProj = CRS.from_epsg(4326)  # WGS84 좌표계
# X, Y 좌표를 Point 객체로 변환
geometry = [Point(xy) for xy in zip(sido_center['X'], sido_center['Y'])]

# Point 객체를 GeoDataFrame으로 변환
gdf = gpd.GeoDataFrame(sido_center, geometry=geometry)

# 좌표 변환
#gdf['geometry'] = gdf['geometry'].apply(lambda x: transform(inProj, outProj, x.x, x.y))


transformer = Transformer.from_crs(inProj, outProj, always_xy=True)

gdf['geometry'] = gdf['geometry'].apply(
    lambda point: Point(*transformer.transform(point.x, point.y))
)

gdf['LON'], gdf['LAT'] = zip(*gdf['geometry'].apply(lambda point: (point.x, point.y)))


#gdf['LON'], gdf['LAT'] = zip(*gdf['geometry'].apply(lambda x: (x[0], x[1])))


gdf.iloc[:, [0, 4, 5]].to_csv("d:/토지_AVM/시도별_중심좌표.csv", index=False)
import plotly.express as px

df_grouped = df.group_by("용도지역명1").agg(
    (pl.col("LAND_PRICE_PER_SQUARE")/pl.col("공시지가")).mean().round(2).alias("격차율")
    ).sort("격차율", descending=True)

df_grouped.write_parquet("d:/토지_AVM/용도지역별_격차율.parquet")


# fig = px.bar(df_grouped, x="용도지역명1", y="격차율", color="격차율", labels={"용도지역명1": "용도지역명", "격차율": "격차율"}, title="용도지역별 격차율")
# fig.update_layout(plot_bgcolor='white')
# fig.show()



df_grouped2 = df.group_by("지목명").agg(
    (pl.col("LAND_PRICE_PER_SQUARE")/pl.col("공시지가")).mean().round(2).alias("격차율")
    ).sort("격차율", descending=True)

df_grouped2.write_parquet("d:/토지_AVM/지목별_격차율.parquet")


df_grouped3 = df.group_by("토지이동상황").agg(
    (pl.col("LAND_PRICE_PER_SQUARE")/pl.col("공시지가")).mean().round(2).alias("격차율")
    ).sort("격차율", descending=True)

df_grouped3.write_parquet("d:/토지_AVM/이용상황별_격차율.parquet")

