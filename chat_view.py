import streamlit as st
import state


def render_chat_input():
    return st.chat_input("Digite sua mensagem sobre telemetria ou estratégia da F1...")


def render_messages():
    messages = state.get_messages()
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def render_user_message_instant(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)


def render_stream_response(stream):
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    return response
