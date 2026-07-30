import streamlit as st
import streamlit.components.v1 as components
import state
import callbacks
import sidebar
import chat_view
import chat_controller

st.set_page_config(page_title="F1 Analytics", layout="wide", initial_sidebar_state="expanded")

state.init_state()

chat_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700;900&display=swap');

:root {
    --f1-red: #E10600;
    --f1-font: 'Titillium Web', -apple-system, sans-serif;
    --f1-veil: rgba(128,128,128,0.10);
    --f1-veil-2: rgba(128,128,128,0.16);
    --f1-line: rgba(128,128,128,0.26);
}

/* Regra de ouro: nenhum background-color nem color fixo aqui.
   Fundo e texto vem do config.toml; paineis usam veu translucido. */

.stApp, [data-testid="stSidebar"], textarea, button {
    font-family: var(--f1-font) !important;
}

header { background-color: transparent !important; }
.stAppDeployButton, [data-testid="stHeaderActionElements"] { display: none !important; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    border-right: 1px solid var(--f1-line) !important;
}
[data-testid="stSidebar"] > div:first-child {
    border-top: 3px solid var(--f1-red);
}
[data-testid="stSidebar"] .stButton > button {
    border-radius: 4px !important;
    border: 1px solid transparent !important;
    border-left: 3px solid transparent !important;
    padding: 10px 12px !important;
    background-color: transparent !important;
    opacity: 0.72;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button * {
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 400 !important;
    font-size: 14px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: var(--f1-veil) !important;
    border-left: 3px solid var(--f1-red) !important;
    opacity: 1;
}
[data-testid="stSidebar"] p {
    opacity: 0.55;
    padding-left: 5px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Botao de apagar: discreto, vermelho so no hover */
[class*="st-key-del_"] button,
[class*="st-key-del_"] button:hover {
    background-color: transparent !important;
    border: none !important;
    border-left: none !important;
    text-align: center !important;
}
[class*="st-key-del_"] button * { justify-content: center !important; }
[class*="st-key-del_"] button { opacity: 0.45; }
[class*="st-key-del_"] button:hover { opacity: 1; color: var(--f1-red) !important; }

/* ---------- Fluxo de mensagens ---------- */
[data-testid="stChatMessageContainer"] {
    display: flex; flex-direction: column; height: auto;
    width: 100%; max-width: 800px; margin: 0 auto;
    padding-top: 20px; padding-bottom: 120px;
}
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 20px 0 !important;
    border-bottom: 1px solid var(--f1-line) !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    line-height: 1.7; font-size: 15px;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] { display: none !important; }

/* ---------- Input ---------- */
[data-testid="stChatInput"] { background-color: transparent !important; }
[data-testid="stChatInput"] > div {
    background-color: var(--f1-veil-2) !important;
    backdrop-filter: blur(12px) !important;
    border-radius: 8px !important;
    border: 1px solid var(--f1-line) !important;
    padding: 5px 10px !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--f1-red) !important;
}

/* Menu 3 pontinhos: mantem so o seletor de tema */
[data-testid="stMainMenuPopover"] > div > *:nth-child(n+2),
[data-testid="stMainMenuPopover"] ul > li:nth-child(n+2),
[data-testid="stMainMenuList"] > *:nth-child(n+2) {
    display: none !important;
}

/* rodape "Made with Streamlit" dentro do menu */
[data-testid="stMainMenuInfo"],
[data-testid="stMainMenuPopover"] footer,
[data-testid="stMainMenuPopover"] a[href*="streamlit.io"],
[data-testid="stMainMenuPopover"] *:has(> a[href*="streamlit.io"]),
[data-testid="stMainMenuPopover"] hr,
[data-testid="stMainMenuPopover"] hr ~ * {
    display: none !important;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# Remove o rodape "Made with Streamlit" do menu (o menu so renderiza ao abrir,
# por isso o observer). components.html e necessario: st.markdown nao executa JS.
components.html(
    """
    <script>
    const doc = window.parent.document;

    function limpar() {
        doc.querySelectorAll('a[href*="streamlit.io"]').forEach(function (a) {
            const alvo = a.closest('li, [role="menuitem"], div') || a;
            alvo.style.display = 'none';
        });
        doc.querySelectorAll('span, p, div, li').forEach(function (el) {
            if (el.children.length === 0 && /Made with Streamlit/i.test(el.textContent)) {
                const alvo = el.closest('li, [role="menuitem"]') || el.parentElement || el;
                alvo.style.display = 'none';
            }
        });
    }

    limpar();
    new MutationObserver(limpar).observe(doc.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
)

# 1. Renderiza a sidebar
sessions = chat_controller.get_all_sessions()
sidebar.render_sidebar(sessions)

# 2. Container dinâmico: chave baseada no ID da sessão atual limpa o VDOM instantaneamente ao trocar/criar chat
current_sid = state.get_current_session_id()
chat_container = st.container(key=f"chat_container_v_{state.get_chat_version()}")

# 3. Declara o input na raiz (fixo no rodapé)
prompt = chat_view.render_chat_input()

# 4. Injeta a renderização e o fluxo de mensagens dentro do container seguro
with chat_container:
    chat_view.render_messages()
    
    if prompt:
        chat_view.render_user_message_instant(prompt)
        state.append_message("user", prompt)

        is_new_session = callbacks.handle_lazy_session_creation(prompt)
        session_id = state.get_current_session_id()

        stream = chat_controller.get_ai_stream_response(prompt, session_id)
        full_response = chat_view.render_stream_response(stream)

        state.append_message("assistant", full_response)
        callbacks.save_interaction(session_id, prompt, full_response)

        if is_new_session:
            st.rerun()
