import streamlit as st
from chatbot_backend import workflow
from langchain_core.messages import HumanMessage
import uuid
# st.session_state -> dict -> 

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id=uuid.uuid4()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['messages']=[]

def add_thread(thread_id):
    if 'thread_id' not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_conversation(thread_id):
    return workflow.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']    

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'])

#--------Sidebar--------#
st.sidebar.title('LangGraph Chatbot')
if st.sidebar.button('New Chat'):
    reset_chat()
st.sidebar.header('My Conversations')
for thread in st.session_state['chat_threads']:
    st.sidebar.button(str(thread))


# loading the conversation history
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=ello'}

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
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

    # Save the response; it has already been rendered above.
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})