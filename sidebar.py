import streamlit as st
import callbacks


_CSS_DELETE = """
<style>
/* Botao primario: fundo claro com texto vermelho */

/* Botao de enviar do chat input */
[data-testid="stChatInputSubmitButton"] svg {
    fill: #E10600 !important;
    color: #E10600 !important;
}
</style>
"""


@st.dialog("Apagar conversa")
def _dialog_confirmar(session_id, titulo):
    st.markdown(_CSS_DELETE, unsafe_allow_html=True)

    st.markdown(
        "Apagar <strong style='color:#E10600'>%s</strong>?" % titulo.strip(),
        unsafe_allow_html=True,
    )
    st.caption("Esta ação não pode ser desfeita.")

    c_sim, c_nao = st.columns(2)
    if c_sim.button("🗑️ Apagar", key="dlg_yes",
                    type="primary", use_container_width=True):
        callbacks.on_delete_confirmed(session_id)
        st.rerun()
    if c_nao.button("Cancelar", key="dlg_no", use_container_width=True):
        callbacks.on_delete_cancelled()
        st.rerun()


def render_sidebar(sessions):
    pendente = st.session_state.get("pending_delete_id")

    st.markdown(_CSS_DELETE, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<p>Chat</p>", unsafe_allow_html=True)

        st.button(
            "➕ Nova Conversa",
            key="btn_new_chat",
            use_container_width=True,
            on_click=callbacks.on_new_chat_clicked
        )

        st.markdown("---")
        st.markdown("<p>Histórico</p>", unsafe_allow_html=True)

        erro = st.session_state.pop("chat_delete_error", None)
        if erro:
            st.error(erro)

        if sessions:
            for session in sessions:
                session_id = session.get("id")
                session_title = session.get("title", "Conversa %s" % session_id)

                col_open, col_del = st.columns([0.78, 0.22])

                col_open.button(
                    session_title,
                    key="session_%s" % session_id,
                    use_container_width=True,
                    on_click=callbacks.on_session_clicked,
                    args=(session_id,)
                )

                col_del.button(
                    "🗑️",
                    key="del_%s" % session_id,
                    use_container_width=True,
                    help="Apagar conversa",
                    on_click=callbacks.on_delete_requested,
                    args=(session_id,)
                )

    ids = {s.get("id") for s in (sessions or [])}
    if pendente is not None and pendente not in ids:
        st.session_state.pop("pending_delete_id", None)
        pendente = None

    if pendente is not None:
        titulo = next(
            (s.get("title", "Conversa %s" % pendente)
             for s in (sessions or []) if s.get("id") == pendente),
            "Conversa %s" % pendente,
        )
        _dialog_confirmar(pendente, titulo)
