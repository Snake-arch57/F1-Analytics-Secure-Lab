import os
import sys
import fastf1
import pandas as pd
from app.services.db_service import save_processed_session_data

fastf1.Cache.enable_cache('/app/data/cache/fastf1')

seasons = [int(a) for a in sys.argv[1:]] or [2026]
session_types = os.getenv("SESSION_TYPES", "R").split(",")
limit = int(os.getenv("LIMIT_EVENTS", "0"))   # 0 = sem limite

print(f"Carga F1 | temporadas={seasons} | sessoes={session_types} | limite={limit or 'todos'}")

for year in seasons:
    print(f"\n=== Temporada {year} ===")
    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        print(f"[AVISO] Calendario de {year} indisponivel: {e}")
        continue

    schedule = schedule[schedule['EventFormat'] != 'testing']
    agora = pd.Timestamp.now()
    processados = 0

    for _, event in schedule.iterrows():
        event_name = event['EventName']
        data = event.get('EventDate')

        if pd.isna(data):
            continue
        ts = pd.Timestamp(data)
        if ts.tzinfo is not None:
            ts = ts.tz_localize(None)
        if ts > agora:
            print(f"[PULADO] {event_name} ainda nao aconteceu")
            continue

        for s_type in session_types:
            print(f"  -> {event_name} [{s_type}]")
            try:
                save_processed_session_data(
                    {'season': year, 'event_name': event_name, 'session_type': s_type},
                    {}
                )
            except Exception as ex:
                print(f"     [ERRO] {event_name} ({s_type}): {ex}")

        processados += 1
        if limit and processados >= limit:
            print(f"[STOP] Limite de {limit} evento(s) atingido")
            break

print("\nCarga concluida")
