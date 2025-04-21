# pages/04_address_verification.py

import streamlit as st
from datetime import datetime
import pandas as pd
import pymongo
import plotly.graph_objects as go

def main():
    # Display the current date and time    
    current_datetime = datetime.now()
    st.title(f"{current_datetime.strftime('%Y-%m-%d')}")
    #st.write()

    # MongoDB Connection
    try:
        connection = pymongo.MongoClient('mongodb://220.72.165.102:27017', username="admin", password="rhksflwk!")
        db = connection['hanjongseon']
        collection = db['VIOL_DATA2']
        log_collection = db['VIEW_LOG']  # Log collection

        # 1. INTER 값별 갯수 집계
        pipeline = [
            {"$group": {"_id": "$INTER", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        inter_counts = list(collection.aggregate(pipeline))
        
        temp_data = pd.DataFrame(inter_counts)
        temp_data.columns = ['PC_NUMBER', 'REMAIN_COUNT']
        temp_data['datetime'] = current_datetime
        log_collection.insert_many(temp_data.to_dict('records'))

        # Display the aggregation result
        if inter_counts:
            #st.write("### PC별 잔여대상 카운트")
            df = pd.DataFrame(inter_counts)
            df.columns = ['PC_NUMBER', 'REMAIN_COUNT']

            # 시각화를 위한 로그 데이터 가져오기
            log_data = list(log_collection.find({}, {"_id": 0}))
            log_df = pd.DataFrame(log_data)

            if not log_df.empty:
                log_df['datetime'] = pd.to_datetime(log_df['datetime'])

                # PC_NUMBER별 REMAIN_COUNT 변화를 시간 순으로 시각화
                #st.write("### PC별 잔여대상 카운트 변화 (Interactive)")

                # Create an interactive Plotly figure
                fig = go.Figure()

                for pc_number in log_df['PC_NUMBER'].unique():
                    pc_data = log_df[log_df['PC_NUMBER'] == pc_number]
                    fig.add_trace(go.Scatter(
                        x=pc_data['datetime'],
                        y=pc_data['REMAIN_COUNT'],
                        mode='lines+markers',
                        name=f'PC_NUMBER: {pc_number}'
                    ))

                fig.update_layout(
                    title=f"PC별 잔여대상 카운트 변화",
                    xaxis_title="Datetime",
                    yaxis_title="REMAIN_COUNT",
                    legend_title="PC_NUMBER",
                    xaxis=dict(showgrid=True),
                    yaxis=dict(showgrid=True),
                    template="plotly_white"
                )

                # Render the interactive plot
                st.plotly_chart(fig, use_container_width=True)

                # Add a button to delete logs if all REMAIN_COUNT are 0
                if st.button("Check and Delete Logs"):
                    if log_df['REMAIN_COUNT'].sum() == 0:
                        log_collection.delete_many({})
                        st.success("All logs deleted as all REMAIN_COUNT values are 0.")
                    else:
                        st.warning("Logs not deleted. REMAIN_COUNT values are not all 0.")
            else:
                st.warning("No log data available for visualization.")
        else:
            st.warning("No data found in the collection.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
