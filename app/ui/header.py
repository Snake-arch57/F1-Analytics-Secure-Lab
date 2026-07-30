from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOGO_PATH = PROJECT_ROOT / "assets" / "agapornis_logo.png"


def render_header():

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:

        if LOGO_PATH.exists():

            st.image(
                str(LOGO_PATH),
                width=180
            )

        st.markdown(
            """
            <h1 style="
                text-align:center;
                font-size:3rem;
                margin-bottom:0;
                color:white;
            ">
            AGAPORNIS AI CORE
            </h1>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <p style="
                text-align:center;
                color:#9CA3AF;
                font-size:1.15rem;
                margin-top:0.4rem;
            ">
            IA Local especializada em análises de Fórmula 1
            </p>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.badge("Ollama")

        with c2:
            st.badge("PostgreSQL")

        with c3:
            st.badge("FastF1")

        with c4:
            st.badge("Local AI")

    st.markdown("<br>", unsafe_allow_html=True)
