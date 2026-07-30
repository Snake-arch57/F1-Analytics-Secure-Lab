import streamlit as st

def render_cards():
    # Criando um grid 2x2 de sugestões rápidas de IA focadas em F1
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Análise de Ritmo 🏎️", value="Comparar Verstappen vs Hamilton em Mônaco 2024", delta="Telemetria")
        st.metric(label="Estratégia de Paradas ⏱️", value="Qual a janela ideal de Pit Stop para Monza?", delta="Estratégia")
        
    with col2:
        st.metric(label="Clima e Pneus 🌧️", value="Analisar impacto de pista molhada no GP atual", delta="Previsão")
        st.metric(label="Histórico de Desempenho 📊", value="Resumo da evolução da McLaren na temporada", delta="Histórico")
