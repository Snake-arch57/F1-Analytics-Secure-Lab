import os
import sys
from pathlib import Path
import streamlit as st

# 1. Ajuste Dinâmico do Path para evitar ModuleNotFoundError no Docker
# Garante que a raiz do código (/app/app) e a raiz do projeto (/app) estejam no path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(1, str(PROJECT_ROOT))

# 2. Configuração de página OBRIGATORIAMENTE em primeiro lugar
st.set_page_config(
    page_title="AGAPORNIS AI CORE",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. Imports internos (Devem vir DEPOIS do ajuste do sys.path e set_page_config)
from ui.theme import load_global_styles
from ui.sidebar import render_sidebar
from ui.ai_home import render_ai_home

# 4. Injetar o arquivo CSS customizado da Sprint 1.5 & Sprint 2
css_path = os.path.join(PROJECT_ROOT, "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Remove margens exageradas do Streamlit para colar o chat na parte inferior
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    </style>
""", unsafe_allow_html=True)

# 5. Execução dos Componentes Visuais
load_global_styles()  # Carrega seus estilos globais base, se existirem
render_sidebar()      # Invoca a barra lateral com histórico e status (Sprint 2)
render_ai_home()      # Renderiza o chat central minimalista (Sprint 1)
