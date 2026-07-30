import psycopg2
import os
import pandas as pd
import fastf1

class DBService:
    def __init__(self):
        self.dbname = os.getenv("POSTGRES_DB", "f1_analytics")
        self.user = os.getenv("POSTGRES_USER", "f1_app")
        self.password = os.getenv("POSTGRES_PASSWORD", "f1_local_dev_password")
        self.host = os.getenv("POSTGRES_HOST", "postgres")
        
    def execute_query(self, sql, params=None):
        try:
            conn = psycopg2.connect(
                dbname=self.dbname, user=self.user, password=self.password, host=self.host, port=5432
            )
            cur = conn.cursor()
            cur.execute(sql, params)
            if cur.description:
                colnames = [desc[0] for desc in cur.description]
                results = [dict(zip(colnames, row)) for row in cur.fetchall()]
            else:
                results = []
            conn.commit()
            cur.close()
            conn.close()
            return results
        except Exception as e:
            print(f"Erro de conexao no banco: {e}")
            return []


    def apagar_chat(self, session_id):
        """Apaga a conversa inteira. O CASCADE leva as mensagens junto."""
        if not session_id:
            raise ValueError("session_id ausente - recusando DELETE sem escopo.")
        conn = psycopg2.connect(
            dbname=self.dbname, user=self.user,
            password=self.password, host=self.host, port=5432
        )
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT count(*) FROM chat_messages WHERE session_id = %s",
                    (session_id,),
                )
                n = cur.fetchone()[0]
                cur.execute("DELETE FROM chat_sessions WHERE id = %s", (session_id,))
            conn.commit()
            return n
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def save_processed_session_data(session_info, laps_data):
    db = DBService()
    try:
        if isinstance(session_info, dict):
            season = int(session_info.get('season', session_info.get('year', 2024)))
            event_name = str(session_info.get('event_name', session_info.get('race_name', 'Bahrain Grand Prix')))
            session_type = str(session_info.get('session_type', 'R'))
        elif hasattr(session_info, 'event') and session_info.event is not None:
            season = int(session_info.event.get('Season', 2024))
            event_name = str(session_info.event.get('EventName', 'Bahrain Grand Prix'))
            session_type = str(session_info.name)
        else:
            season = 2024
            event_name = "Bahrain Grand Prix"
            session_type = "R"

        # Captura do dicionário complementar
        if isinstance(laps_data, dict) and not laps_data.get('laps'):
            season = int(laps_data.get('year', season))
            session_type = str(laps_data.get('session_type', session_type))

        pass  # escape agora e feito pelo driver

        sql_session = """
            INSERT INTO f1.sessions (season, event_name, session_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (season, event_name, session_type) 
            DO UPDATE SET event_name = EXCLUDED.event_name
            RETURNING id;
        """
        res_session = db.execute_query(sql_session, (season, event_name, session_type))
        if not res_session:
            sql_get_id = """
                SELECT id FROM f1.sessions WHERE season=%s AND event_name=%s AND session_type=%s;
            """
            res_session = db.execute_query(sql_get_id, (season, event_name, session_type))
        
        session_id = res_session[0]['id']
        db.execute_query("DELETE FROM f1.laps WHERE session_id = %s;", (session_id,))

        # Carga direta das voltas via FastF1
        laps_list = []
        fastf1.Cache.enable_cache('/app/data/cache/fastf1')
        
        try:
            session = fastf1.get_session(season, event_name, session_type)
            session.load(laps=True, telemetry=False, weather=False, messages=False)
            if session.laps is not None:
                laps_list = session.laps.to_dict(orient='records')
        except Exception as e_load:
            raise RuntimeError(
                f"FastF1 nao carregou {event_name} ({season}/{session_type}): {e_load}"
            )

        inserted_count = 0
        for row in laps_list:
            if not isinstance(row, dict):
                continue
                
            team_raw = row.get('Team', row.get('team_name', row.get('team', 'Unknown Team')))
            driver_raw = row.get('Driver', row.get('driver_id', row.get('driver', 'UNK')))
            lap_num_raw = row.get('LapNumber', row.get('lap_number', row.get('lap', 1)))
            
            # Tratamento de tempo flexível (LapTimeSeconds numérico vs LapTime Timedelta object)
            lap_time_seconds = None
            lap_time_raw = row.get('LapTimeSeconds', row.get('LapTime', None))
            
            if lap_time_raw is not None and str(lap_time_raw) != 'nan' and not pd.isna(lap_time_raw):
                if hasattr(lap_time_raw, 'total_seconds'):
                    lap_time_seconds = lap_time_raw.total_seconds()
                else:
                    try:
                        lap_time_seconds = float(lap_time_raw)
                    except ValueError:
                        continue

            if lap_time_seconds is None:
                continue

            team_name = str(team_raw)
            driver_name = str(driver_raw)

            sql_team = """
                INSERT INTO f1.teams (team_name) VALUES (%s) ON CONFLICT (team_name) DO UPDATE SET team_name = EXCLUDED.team_name RETURNING id;
            """
            res_team = db.execute_query(sql_team, (team_name,))
            team_id = res_team[0]['id']

            sql_driver = """
                INSERT INTO f1.drivers (abbreviation, full_name, current_team) VALUES (%s, %s, %s) ON CONFLICT (abbreviation) DO UPDATE SET current_team = EXCLUDED.current_team RETURNING id;
            """
            res_driver = db.execute_query(sql_driver, (driver_name, driver_name, team_name))
            driver_id = res_driver[0]['id']

            sql_lap = """
                INSERT INTO f1.laps (session_id, driver_id, team_id, lap_number, lap_time_seconds)
                VALUES (%s, %s, %s, %s, %s);
            """
            db.execute_query(sql_lap, (session_id, driver_id, team_id, int(lap_num_raw), float(lap_time_seconds)))
            inserted_count += 1
            
        print(f"✅ Sessão {event_name} salva com sucesso! ({inserted_count} voltas processadas)")
        
        return {
            "status": "success", 
            "session_id": session_id, 
            "laps": laps_list[:1],
            "pit_stops": [], 
            "results": [],
            "drivers": [],
            "teams": []
        }
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados da sessão: {e}")
        return {"status": "error", "message": str(e), "laps": [], "pit_stops": [], "results": [], "teams": []}
