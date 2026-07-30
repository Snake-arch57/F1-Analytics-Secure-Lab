import os
import fastf1
import pandas as pd
from services.db_service import save_processed_session_data

def carregar_tudo():
    print("🏁 Iniciando a automação de carga em lote (2024, 2025 e 2026)...")

    # Ativa o cache centralizado
    cache_dir = '/tmp/fastf1_cache'
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)

    anos = [2024, 2025, 2026]

    for ano in anos:
        print(f"\n📅 [TEMPORADA {ano}] Buscando calendário oficial...")
        try:
            calendario = fastf1.get_event_schedule(ano)
            # Filtra apenas GPs válidos (remove testes de pré-temporada)
            corridas = calendario[calendario['EventFormat'] != 'testing']

            if corridas.empty:
                print(f"⚠️ Nenhuma corrida encontrada para o ano {ano}.")
                continue

            print(f"🏎️ Encontrados {len(corridas)} GPs. Iniciando processamento...")

            for idx, row in corridas.iterrows():
                round_num = row.get('RoundNumber', idx)
                event_name = row['EventName']
                
                # Valida se a corrida já aconteceu (essencial para a temporada atual de 2026)
                if 'EventDate' in row and not pd.isna(row['EventDate']):
                    if row['EventDate'].tz_localize(None) > pd.Timestamp.now():
                        print(f"⏩ GP {event_name} (Round {round_num}) pulado pois ainda não aconteceu.")
                        continue

                print(f"🛰️ [{ano} - Etapa {round_num}] Carregando {event_name}...")
                
                try:
                    # 'R' garante a sessão principal de Corrida
                    session = fastf1.get_session(ano, event_name, 'R')
                    session.load(telemetry=False, laps=True, weather=False, messages=False)
                    
                    meta_dados = {
                        "event_name": session.event['EventName'],
                        "country": session.event['Country'],
                        "location": session.event['Location'],
                        "session_name": session.name,
                        "results": session.results,
                        "laps": session.laps
                    }

                    parametros_carga = {
                        "year": ano,
                        "session_type": 'R'
                    }

                    # Enviando com o nome de parâmetro correto esperado pelo seu db_service
                    save_processed_session_data(meta_dados, laps_data=parametros_carga)
                    
                except Exception as e_gp:
                    print(f"❌ Erro ao processar o {event_name}: {e_gp}")
                    continue

        except Exception as e_ano:
            print(f"❌ Erro crítico na temporada de {ano}: {e_ano}")

    print("\n🏆 PROCESSAMENTO CONCLUÍDO! O banco de dados está atualizado com 2024, 2025 e 2026.")

if __name__ == "__main__":
    carregar_tudo()
