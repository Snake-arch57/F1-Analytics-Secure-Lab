import streamlit as st


def render_footer():

    st.markdown("---")

    st.caption(
        "Todas as respostas serão baseadas exclusivamente nos dados locais armazenados no PostgreSQL."
    )

