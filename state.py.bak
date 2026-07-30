import streamlit as st


def init_state():
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_version" not in st.session_state:
        st.session_state.chat_version = 0


def get_chat_version():
    return st.session_state.chat_version


def bump_chat_version():
    st.session_state.chat_version += 1


def get_current_session_id():
    return st.session_state.current_session_id


def set_current_session_id(session_id):
    st.session_state.current_session_id = session_id


def clear_session():
    st.session_state.current_session_id = None
    st.session_state.messages = []
    st.session_state.chat_version += 1


def append_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})


def get_messages():
    return st.session_state.messages


def set_messages(messages):
    st.session_state.messages = messages
