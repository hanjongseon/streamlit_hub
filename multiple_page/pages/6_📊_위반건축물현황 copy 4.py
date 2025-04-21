# pages/04_address_verification.py

import streamlit as st
from datetime import datetime
import pandas as pd
import pymongo

def main():
    # Display the current date
    st.title("Address Verification")
    st.write(f"#### Date: {datetime.now().strftime('%Y-%m-%d')}")

    # MongoDB Connection
    try:
        connection = pymongo.MongoClient('mongodb://220.72.165.102:27017', username="admin", password="rhksflwk!")
        db = connection['hanjongseon']
        collection = db['VIOL_DATA2']
        
        # 1. INTER 값별 갯수 집계
        pipeline = [
            {"$group": {"_id": "$INTER", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        inter_counts = list(collection.aggregate(pipeline))

        # Display the aggregation result
        if inter_counts:
            st.write("### INTER Value Counts")
            df = pd.DataFrame(inter_counts)  # Convert to DataFrame for better visualization
            df.rename(columns={"_id": "INTER", "count": "Count"}, inplace=True)
            st.dataframe(df)  # Display as an interactive table
        else:
            st.warning("No data found in the collection.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
