import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Big Abmitions Analyzer",
    page_icon="🎮",
    layout="wide"
)


st.title("🎮 Big Ambitions Business Analyzer")
st.write("Analize you business data from Big Ambitions")


#Upload file 
uploaded_file = st.file_uploader(
    "upload your csv file",
    type=["csv"],
    help="Export file from your game and upload here"
)

if uploaded_file is not None:
    st.success("File uploaded")
else:
    st.info("Upload file for start analysis")