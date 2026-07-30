import sys
# Adiciona a raiz do código ao Python Path
sys.path.append('/app/app')

from services.db_service import DBService

class F1AIContextService:
    def __init__(self):
        self.db = DBService()

    def retrieve_context(self, user_query: str) -> str:
        # Query adaptada ao schema f1 e nome de colunas que criamos no init.sql
        sql = "SELECT t.team_name, AVG(l.lap_time_seconds) as media FROM f1.laps l JOIN f1.teams t ON l.team_id = t.id GROUP BY t.team_name LIMIT 5;"
        results = self.db.execute_query(sql)
        return str(results)
