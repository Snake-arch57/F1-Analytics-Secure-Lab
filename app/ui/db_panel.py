import streamlit as st

from app.services.db_service import (
    get_database_status,
    get_saved_sessions,
    save_processed_session_data,
)


def render_database_persistence_panel(data: dict, loaded_params: dict) -> None:
    """
    Renderiza o painel de persistência PostgreSQL dentro do dashboard.
    """
    st.divider()
    st.subheader("🗄️ Persistência PostgreSQL")

    with st.expander("Salvar e consultar dados processados no banco", expanded=False):
        status = get_database_status()

        if not status["ok"]:
            st.warning("PostgreSQL indisponível para o app neste momento.")
            st.caption(status["message"])
            return

        st.success("PostgreSQL conectado com sucesso.")
        st.caption("Conexão com banco validada sem exposição de versão.")

        if st.button("Salvar sessão carregada no PostgreSQL", type="primary"):
            try:
                result = save_processed_session_data(data, loaded_params)

                st.success(
                    "Sessão salva com sucesso no PostgreSQL: "
                    f"{result['laps']} voltas, "
                    f"{result['pit_stops']} pit stops, "
                    f"{result['drivers']} pilotos e "
                    f"{result['teams']} equipes."
                )

            except Exception as error:
                st.error("Falha ao salvar dados no PostgreSQL.")
                with st.expander("Detalhes técnicos"):
                    st.exception(error)

        try:
            saved_sessions = get_saved_sessions()

            if saved_sessions.empty:
                st.info("Nenhuma sessão salva no banco ainda.")
            else:
                st.markdown("**Sessões salvas no banco:**")
                st.dataframe(saved_sessions, use_container_width=True)

        except Exception as error:
            st.error("Falha ao consultar sessões salvas.")
            with st.expander("Detalhes técnicos"):
                st.exception(error)
