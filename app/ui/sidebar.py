import streamlit as st

def render_sidebar():
    with st.sidebar:
        # 1. Topo: Logo Pequena e Título
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image("assets/agapornis_logo.png", width=35)
        with col2:
            st.markdown("<h3 style='margin-top: 0px; font-weight: 700;'>Agapornis AI</h3>", unsafe_allow_html=True)
        
        st.write("")
        
        # 2. Botão de Nova Conversa (Estilo Claude)
        if st.button("➕ Nova conversa", use_container_width=True):
            st.session_state.messages = []  # Reseta o chat (adiantando lógica da Sprint 3)
            st.rerun()
            
        st.write("---")
        st.markdown("<p style='color: #8a92a6; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;'>Histórico de Corridas</p>", unsafe_allow_html=True)
        
        # 3. Histórico de Conversas Temporário (Mockado)
        history_chats = [
            "🏎️ Telemetria Mônaco 2024",
            "📊 Ritmo de Corrida - Monza",
            "⚙️ Configuração de Asa Traseira",
            "⏱️ Análise de Pit Stop Verstappen"
        ]
        
        for chat_title in history_chats:
            if st.button(chat_title, key=chat_title, use_container_width=True, type="secondary"):
                # Próximas sprints controlarão a troca de contexto aqui
                pass
                
        st.write("---")
        
        # 4. Status da Infraestrutura (Ollama e PostgreSQL)
        st.markdown("<p style='color: #8a92a6; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;'>Status do Sistema</p>", unsafe_allow_html=True)
        
        # Por enquanto simulados (Sprint 4 integrará os serviços reais)
        st.markdown("🟢 **PostgreSQL:** `Conectado`")
        st.markdown("🟢 **Ollama API:** `Pronto (Llama3)`")
        
        # 5. Configurações (Placeholder)
        st.write("---")
        if st.button("⚙️ Configurações", use_container_width=True):
            st.info("Painel de configurações em desenvolvimento para a Sprint 5.")
