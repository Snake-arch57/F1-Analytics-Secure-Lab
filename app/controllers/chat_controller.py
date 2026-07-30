import streamlit as st
from app.services.ollama_service import OllamaService
from app.services.db_service import DBService

class ChatController:
    def __init__(self):
        self.ollama = OllamaService()

    def process_user_message(self, user_prompt):
        if "db" not in st.session_state:
            st.session_state.db = DBService()

        # Busca os dados executando uma query direta no banco de dados
        raw_data = st.session_state.db.execute_query("""
            SELECT t.team_name, l.lap_time_seconds 
            FROM f1.laps l
            JOIN f1.teams t ON l.team_id = t.id
            WHERE l.lap_time_seconds IS NOT NULL
        """)
        
        # Agrupa os tempos por equipe em Python para formar o resumo
        data_by_team = {}
        for row in raw_data:
            team = row['team_name']
            time_val = row['lap_time_seconds']
            if team not in data_by_team:
                data_by_team[team] = []
            data_by_team[team].append(time_val)

        resumo_contexto = "Médias de tempo de volta por equipe:\n"
        if data_by_team:
            for team, times in data_by_team.items():
                if times:
                    media = sum(times) / len(times)
                    resumo_contexto += f"- {team}: {media:.3f} segundos\n"
        else:
            resumo_contexto += "Nenhum dado de volta encontrado no banco de dados.\n"

        return self.ollama.generate_response_stream(
            user_prompt=user_prompt,
            context_data=resumo_contexto,
            system_prompt="Você é um analista especialista em Fórmula 1. Responda com base estritamente nos dados fornecidos."
        )
