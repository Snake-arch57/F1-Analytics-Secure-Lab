import streamlit as st
from controllers.chat_controller import ChatController

def render_chat():
    LOGO_AVATAR = "assets/agapornis_logo.png"

    # Garante a persistência do controller na sessão do Streamlit
    if "chat_controller" not in st.session_state:
        st.session_state.chat_controller = ChatController()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Renderiza o histórico acumulado
    for message in st.session_state.messages:
        avatar_icon = LOGO_AVATAR if message["role"] == "assistant" else "user"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

    # Captura o prompt na barra estilizada do rodapé
    if prompt := st.chat_input("Pergunte algo ao F1 AI..."):
        
        # Mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Resposta Real da IA (F1 AI)
        with st.chat_message("assistant", avatar=LOGO_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            
            # Dispara a busca e a geração real pelo Qwen via Controller
            stream_generator = st.session_state.chat_controller.process_user_message(prompt)
            
            for chunk in stream_generator:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response.strip())

        # Salva o resultado no histórico e atualiza os containers
        st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
        st.rerun()
