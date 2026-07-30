from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ui.theme import load_global_styles, render_hero
from app.ui.db_panel import render_database_persistence_panel

from app.services.fastf1_service import (
    F1DataUnavailableError,
    get_driver_team_dataframe,
    get_laps_dataframe,
    get_results_dataframe,
    load_f1_session,
)


st.set_page_config(
    page_title="Dashboard F1",
    page_icon="🏁",
    layout="wide"
)

load_global_styles()

render_hero(
    title="Dashboard F1",
    subtitle="Carregue uma sessão da Fórmula 1 usando FastF1 e visualize pilotos, equipes, classificação, tempos de volta e gráficos de ritmo.",
    badge="Race Session Explorer",
)

st.markdown(
    """
    Carregue uma sessão da Fórmula 1 usando FastF1 e visualize pilotos,
    equipes, classificação e tempos de volta.
    """
)


@st.cache_data(show_spinner=False)
def cached_session_data(year: int, event_input: str, session_type: str):
    """
    Cache do Streamlit para evitar recarregar os mesmos dados na interface.
    O FastF1 também possui cache local em data/cache/fastf1.
    """
    event_value = event_input.strip()

    if event_value.isdigit():
        event_value = int(event_value)

    session = load_f1_session(year, event_value, session_type)

    results_df = get_results_dataframe(session)
    laps_df = get_laps_dataframe(session)
    drivers_df = get_driver_team_dataframe(laps_df)

    event_name = session.event.get("EventName", "Evento não identificado")
    country = session.event.get("Country", "N/A")
    location = session.event.get("Location", "N/A")

    return {
        "event_name": event_name,
        "country": country,
        "location": location,
        "session_name": session.name,
        "results": results_df,
        "laps": laps_df,
        "drivers": drivers_df,
    }


if "f1_dashboard_data" not in st.session_state:
    st.session_state.f1_dashboard_data = None

if "f1_dashboard_loaded_params" not in st.session_state:
    st.session_state.f1_dashboard_loaded_params = None


with st.sidebar:
    st.header("Configuração da sessão")

    year = st.number_input(
        "Ano",
        min_value=2018,
        max_value=2026,
        value=2024,
        step=1,
    )

    event_input = st.text_input(
        "GP ou rodada",
        value="Monza",
        help="Exemplos: Monza, Brazil, Silverstone, Bahrain ou número da rodada, como 1."
    )

    session_type = st.selectbox(
        "Sessão",
        options=["R", "Q", "FP1", "FP2", "FP3", "S", "SQ"],
        index=0,
        help="R=Corrida, Q=Classificação, FP=Treinos, S=Sprint, SQ=Sprint Qualifying."
    )

    load_button = st.button("Carregar dados", type="primary")


if load_button:
    try:
        with st.spinner("Carregando dados da sessão pelo FastF1. A primeira execução pode demorar..."):
            st.session_state.f1_dashboard_data = cached_session_data(
                year,
                event_input,
                session_type,
            )
            st.session_state.f1_dashboard_loaded_params = {
                "year": year,
                "event_input": event_input,
                "session_type": session_type,
            }

    except F1DataUnavailableError as error:
        st.warning("Sessão ainda não disponível")
        st.info(str(error))
        st.stop()

    except Exception as error:
        st.error("Não foi possível carregar a sessão selecionada.")
        with st.expander("Detalhes técnicos"):
            st.exception(error)
        st.stop()


data = st.session_state.f1_dashboard_data

if data is None:
    st.warning("Selecione uma corrida no menu lateral e clique em **Carregar dados**.")
    st.stop()


loaded_params = st.session_state.f1_dashboard_loaded_params

if loaded_params:
    st.caption(
        f"Dados carregados: {loaded_params['year']} | "
        f"{loaded_params['event_input']} | {loaded_params['session_type']}"
    )


st.subheader(f"{data['event_name']} - {data['session_name']}")

col1, col2, col3 = st.columns(3)
col1.metric("Ano", loaded_params["year"] if loaded_params else year)
col2.metric("País", data["country"])
col3.metric("Local", data["location"])


drivers_df = data["drivers"]
results_df = data["results"]
laps_df = data["laps"]

render_database_persistence_panel(data, loaded_params)


st.divider()

st.subheader("Pilotos e equipes")

if drivers_df.empty:
    st.info("Não foi possível extrair pilotos e equipes desta sessão.")
else:
    st.dataframe(drivers_df, use_container_width=True)


st.subheader("Classificação da sessão")

if results_df.empty:
    st.info("Classificação não disponível para esta sessão.")
else:
    st.dataframe(results_df, use_container_width=True)


st.subheader("Tempos de volta")

if laps_df.empty:
    st.info("Tempos de volta não disponíveis para esta sessão.")
    st.stop()


available_drivers = sorted(laps_df["Driver"].dropna().unique().tolist())

default_drivers = available_drivers[:5]

selected_drivers = st.multiselect(
    "Selecione pilotos para comparar",
    options=available_drivers,
    default=default_drivers,
    key="selected_f1_drivers",
)

if not selected_drivers:
    st.warning("Selecione pelo menos um piloto para visualizar os dados.")
    st.stop()


filtered_laps = laps_df[laps_df["Driver"].isin(selected_drivers)].copy()

display_columns = [
    col for col in [
        "Driver",
        "Team",
        "LapNumber",
        "LapTimeFormatted",
        "LapTimeSeconds",
        "Stint",
        "Compound",
        "TyreLife",
        "Position",
        "IsPersonalBest",
        "IsAccurate",
    ]
    if col in filtered_laps.columns
]

st.dataframe(
    filtered_laps[display_columns].sort_values(["Driver", "LapNumber"]),
    use_container_width=True,
)


st.subheader("Gráfico: tempos de volta por piloto")

fig = px.line(
    filtered_laps.sort_values("LapNumber"),
    x="LapNumber",
    y="LapTimeSeconds",
    color="Driver",
    markers=True,
    title="Evolução dos tempos de volta",
    labels={
        "LapNumber": "Volta",
        "LapTimeSeconds": "Tempo de volta em segundos",
        "Driver": "Piloto",
    },
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Resumo de ritmo por piloto")

pace_summary = (
    filtered_laps
    .groupby("Driver", as_index=False)
    .agg(
        MelhorVoltaSegundos=("LapTimeSeconds", "min"),
        MediaVoltaSegundos=("LapTimeSeconds", "mean"),
        MedianaVoltaSegundos=("LapTimeSeconds", "median"),
        TotalVoltas=("LapTimeSeconds", "count"),
    )
    .sort_values("MediaVoltaSegundos")
)

st.dataframe(pace_summary, use_container_width=True)

fig_bar = px.bar(
    pace_summary,
    x="Driver",
    y="MediaVoltaSegundos",
    title="Média de tempo de volta por piloto selecionado",
    labels={
        "Driver": "Piloto",
        "MediaVoltaSegundos": "Média em segundos",
    },
)

st.plotly_chart(fig_bar, use_container_width=True)
