import streamlit as st
from ui.header import render_header
from ui.cards import render_cards
from ui.chat import render_chat

def render_ai_home():
    col_left, col_center, col_right = st.columns([1, 4, 1])

    with col_center:
        # O histórico real só contém o que o usuário e a IA conversaram
        has_real_messages = "messages" in st.session_state and len(st.session_state.messages) > 0
        
        if not has_real_messages:
            render_header()  # Logo e Título central
            
            # Caixa de introdução idêntica ao Claude/ChatGPT adaptada para F1
            st.markdown("""
            <div style='background-color: #16191f; border: 1px solid #232731; border-radius: 12px; padding: 20px; margin-bottom: 25px;'>
                <p style='margin-top:0;'>Olá! Sou o <b>AGAPORNIS AI CORE</b>.</p>
                <p>Estou em modo de simulação visual. Na próxima sprint, estarei conectado ao PostgreSQL e ao Ollama para processar telemetria real da Fórmula 1.</p>
                <ul style='margin-bottom:0;'>
                    <li>Análise de ritmo médio e consistência de stints</li>
                    <li>Janelas de pit stops e desgaste de compostos</li>
                    <li>Comparativos diretos entre pilotos e escuderias</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            render_cards()   # Grid de sugestões rápidas
            st.write("")
        
        # O motor do chat roda aqui embaixo
        render_chat()
