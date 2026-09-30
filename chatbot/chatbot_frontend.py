import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from chatbot_backend import workflow


def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):
    chat_threads = st.session_state.setdefault('chat_threads', [])
    if thread_id not in chat_threads:
        chat_threads.append(thread_id)


def reset_chat():
    new_thread_id = generate_thread_id()
    st.session_state['thread_id'] = new_thread_id
    add_thread(new_thread_id)
    st.session_state['message_history'] = []


def load_conversation(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('message', []) if state and state.values else []
    history = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = 'user'
        elif isinstance(msg, AIMessage):
            role = 'assistant'
        else:
            continue

        history.append({'role': role, 'content': getattr(msg, 'content', '')})

    return history


st.session_state.setdefault('message_history', [])
st.session_state.setdefault('chat_threads', [])
st.session_state.setdefault('thread_id', generate_thread_id())
add_thread(st.session_state['thread_id'])

#--------Sidebar--------#
st.sidebar.title('LangGraph Chatbot')
if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')
for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread)):
        st.session_state['thread_id'] = thread
        st.session_state['message_history'] = load_conversation(thread)

# loading the conversation history
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    def stream_response():
        for message, _ in workflow.stream(
            {'message': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages',
        ):
            content = getattr(message, 'content', '')
            if isinstance(content, str) and content:
                yield content

    with st.chat_message('assistant'):
        ai_message = st.write_stream(stream_response())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})