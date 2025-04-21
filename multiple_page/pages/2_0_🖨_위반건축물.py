import streamlit as st
import numpy as np
import uuid
import pymongo
from pymongo import MongoClient
from gridfs import GridFS
from rapidfuzz import process  # For fuzzy matching
from PIL import Image
import io
import re
import pandas as pd
import glob
import os

st.title("위반건축물 대장 조회")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_addresses" not in st.session_state:
    st.session_state.selected_addresses = {}

# Load parquet file
if "db_parquet" not in st.session_state:
    @st.cache_resource
    def get_db_parquet():
        filelistss = glob.glob("d:/work/VIOL/matched_result_*.parquet")        
        return pd.read_parquet(max(filelistss, key=os.path.getctime))

    st.session_state.db_parquet = get_db_parquet()

# Connect to MongoDB and initialize GridFS
if "clean_to_raw" not in st.session_state:
    @st.cache_resource
    def get_db_connection():
        client = MongoClient('mongodb://192.168.101.237:27017')
        db = client['VIO']
        fs = GridFS(db)
        return db, fs

    def get_clean_filenames(db):
        pipeline = [
            {"$group": {"_id": "$filename"}},
            {"$project": {"filename": "$_id", "_id": 0}}
        ]
        filenames_cursor = db['fs.files'].aggregate(pipeline)
        filenames = [doc['filename'] for doc in filenames_cursor]
        clean_to_raw = {
            (re.search(r"HPK-(.+?)\]", filename).group(1) if "HPK-" in filename else 
             re.sub("_[0-9]+건$", "", filename.split(']')[-1].replace('.png', '').strip())): filename
            for filename in filenames
        }
        return clean_to_raw

    db, fs = get_db_connection()
    st.session_state.db = db
    st.session_state.fs = fs
    st.session_state.clean_to_raw = get_clean_filenames(db)

# Create mapping_dict and save it in session state
if "mapping_dict" not in st.session_state:
    df = st.session_state.db_parquet
    st.session_state.mapping_dict = dict(zip(df['HPK'], df['ORI_ADDRESS'].astype(str)))

# Helper functions
def get_similar_filenames(input_text, clean_to_raw, df, max_results=5):
    clean_filenames = list(clean_to_raw.keys())        
    mapping_dict = st.session_state.mapping_dict

    # Transform clean filenames using mapping_dict
    #clean_filenames2 = clean_filenames
    clean_filenames2 =[mapping_dict[x] if x in mapping_dict.keys() else x for x in clean_filenames]
    st.session_state.clean_to_raw = dict(zip(clean_filenames2, clean_to_raw.values()))
    
    # Match input_text with transformed filenames
    matches = process.extract(input_text, clean_filenames2, limit=max_results, score_cutoff=0.7)
    return [match[0] for match in matches]

def get_image_from_gridfs(raw_filename, fs):
    file_data = fs.find_one({'filename': raw_filename})
    if file_data:
        image = Image.open(io.BytesIO(file_data.read()))
        return image
    return None

def crop_center(image, crop_width, crop_height):
    img_width, img_height = image.size
    left = (img_width - crop_width) / 2
    top = (img_height - crop_height) / 2
    right = (img_width + crop_width) / 2
    bottom = (img_height + crop_height) / 2
    return image.crop((left, top, right, bottom))

# Display chat messages from history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "similar_filenames" in message:
            st.markdown(message["content"])
            message_id = message["id"]
            similar_filenames = message["similar_filenames"]

            # Get the current selected address for this message
            current_selected_address = st.session_state.selected_addresses.get(message_id, similar_filenames[0])
            selected_address = st.selectbox(
                "추천 파일 목록:",
                options=similar_filenames,
                index=similar_filenames.index(current_selected_address),
                key=f"address_selectbox_{message_id}"
            )
            # Update the selected address in session state
            st.session_state.selected_addresses[message_id] = selected_address

            # Get the image
            raw_filename = st.session_state.clean_to_raw.get(selected_address)
            if not raw_filename:
                raw_filename = st.session_state.clean_to_raw.get(st.session_state.mapping_dict.get(selected_address))
            image = get_image_from_gridfs(raw_filename, st.session_state.fs)
            if image:
                # Crop the image
                crop_width = 1100
                crop_height = 900
                cropped_image = crop_center(image, crop_width, crop_height)
                st.image(
                    cropped_image,
                    caption=f"Filename: {selected_address} (크롭된 이미지)",
                    use_container_width=True,
                    output_format="PNG"
                )
            else:
                st.warning("이미지를 불러올 수 없습니다. HPK로 시도하세요.")
        else:
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("주소를 입력하세요:"):    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the prompt as an address
    input_text = prompt.strip()

    # Find similar filenames
    similar_filenames = get_similar_filenames(input_text, st.session_state.clean_to_raw, st.session_state.db_parquet, max_results=30)
    if similar_filenames:
        # Generate a unique ID for this message
        message_id = str(uuid.uuid4())

        # Set default selected address
        st.session_state.selected_addresses[message_id] = similar_filenames[0]

        # Save assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": "주소를 입력하고 목록에서 해당목록을 선택하세요.",
            "similar_filenames": similar_filenames,
            "id": message_id
        })

        # Display assistant message
        with st.chat_message("assistant"):
            st.markdown("주소를 입력하고 목록에서 해당목록을 선택하세요.")
            selected_address = st.selectbox(
                "추천 파일 목록:",
                options=similar_filenames,
                key=f"address_selectbox_{message_id}"
            )
            # Update the selected address in session state
            st.session_state.selected_addresses[message_id] = selected_address

            # Get the image
            raw_filename = st.session_state.clean_to_raw.get(selected_address)
            if not raw_filename:
                raw_filename = st.session_state.clean_to_raw.get(st.session_state.mapping_dict.get(selected_address))
            image = get_image_from_gridfs(raw_filename, st.session_state.fs)
            if image:
                # Crop the image
                crop_width = 1100
                crop_height = 900
                cropped_image = crop_center(image, crop_width, crop_height)
                st.image(
                    cropped_image,
                    caption=f"Filename: {selected_address} (크롭된 이미지)",
                    use_container_width=True,
                    output_format="PNG"
                )
            else:
                st.warning("이미지를 불러올 수 없습니다.HPK로 시도하세요.")
    else:
        response = "유사한 파일을 찾을 수 없습니다."
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
