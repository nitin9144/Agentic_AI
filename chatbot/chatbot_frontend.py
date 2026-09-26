import streamlit as st
from chatbot_backend import workflow

messages=st.
with st.chat_message('assistant'):
    st.text("how can i help you")
with st.chat_message('user'):
    st.text("my name is nitin")
user_input= st.chat_input("Type here")
if user_input :
    with st.chat_message('user'):
        st.text(user_input)
