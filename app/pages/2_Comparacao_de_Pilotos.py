from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ui.theme import load_global_styles, render_hero

from app.services.fastf1_service import (
    F1DataUnavailableError,
    get_laps_dataframe,
    load_f1_session,
)

from app.services.race_analysis_service import (
    calculate_driver_metrics,
    calculate_lap_delta_between_drivers,
    calculate_stint_summary,
    calculate_team_metrics,
    calculate_team_pace,
    compare_two_drivers,
    extract_pit_stop_laps,
    filter_racing_laps,
)


st.set_page_config(
    page_title="Comparação de Pilotos",
    page_icon="⚔️",
    layout="wide"
)

load_global_styles()

render_hero(
    title="Comparação de Pilotos",
    subtitle="Compare dois pilotos em ritmo médio, melhor volta, consistência, variação de performance, stints, pit stops e desempenho por equipe.",
    badge="Race Pace Analysis",
)

st.markdown(
    """
    Compare dois pilotos em uma corrida usando ritmo médio, melhor volta,
    consistência, variação de performance, stints, pit stops e comparação entre equipes.
    """
)


@st.cache_data(show_spinner=False)
def cached_laps_data(year: int, event_input: str, session_type: str):
    event_value = event_input.strip()

    if event_value.isdigit():
        event_value = int(event_value)

    session = load_f1_session(year, event_value, session_type)
    laps_df = get_laps_dataframe(session)

    event_name = session.event.get("EventName", "Evento não identificado")
    country = session.event.get("Country", "N/A")
    location = session.event.get("Location", "N/A")

    return {
        "event_name": event_name,
        "country": country,
        "location": location,
        "session_name": session.name,
        "laps": laps_df,
    }


if "comparison_data" not in st.session_state:
    st.session_state.comparison_data = None

if "comparison_loaded_params" not in st.session_state:
    st.session_state.comparison_loaded_params = None


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
    )

    st.divider()

    remove_first_lap = st.checkbox("Ignorar volta 1", value=True)
    remove_pit_laps = st.checkbox("Ignorar voltas de pit na análise de ritmo", value=True)
    remove_slow_outliers = st.checkbox("Remover voltas muito lentas", value=True)

    load_button = st.button("Carregar dados", type="primary")


if load_button:
    try:
        with st.spinner("Carregando dados da sessão pelo FastF1..."):
            st.session_state.comparison_data = cached_laps_data(
                year,
                event_input,
                session_type,
            )
            st.session_state.comparison_loaded_params = {
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


data = st.session_state.comparison_data

if data is None:
    st.warning("Selecione uma corrida no menu lateral e clique em **Carregar dados**.")
    st.stop()


loaded_params = st.session_state.comparison_loaded_params

st.caption(
    f"Dados carregados: {loaded_params['year']} | "
    f"{loaded_params['event_input']} | {loaded_params['session_type']}"
)

st.subheader(f"{data['event_name']} - {data['session_name']}")

col1, col2, col3 = st.columns(3)
col1.metric("Ano", loaded_params["year"])
col2.metric("País", data["country"])
col3.metric("Local", data["location"])


laps_df = data["laps"]

if laps_df.empty:
    st.info("Nenhum dado de volta disponível para análise.")
    st.stop()


percentile = 0.95 if remove_slow_outliers else 1.0

analysis_laps = filter_racing_laps(
    laps_df,
    remove_first_lap=remove_first_lap,
    remove_pit_laps=remove_pit_laps,
    max_lap_time_percentile=percentile,
)

if analysis_laps.empty:
    st.warning("Após os filtros, não sobraram voltas suficientes para análise.")
    st.stop()


available_drivers = sorted(analysis_laps["Driver"].dropna().unique().tolist())

if len(available_drivers) < 2:
    st.warning("A sessão carregada não possui pilotos suficientes para comparação.")
    st.stop()


st.divider()
st.subheader("Seleção dos pilotos")

col_a, col_b = st.columns(2)

with col_a:
    driver_a = st.selectbox(
        "Piloto A",
        options=available_drivers,
        index=0,
        key="comparison_driver_a",
    )

with col_b:
    default_b_index = 1 if len(available_drivers) > 1 else 0
    driver_b = st.selectbox(
        "Piloto B",
        options=available_drivers,
        index=default_b_index,
        key="comparison_driver_b",
    )

if driver_a == driver_b:
    st.warning("Selecione dois pilotos diferentes para comparar.")
    st.stop()


comparison_laps = compare_two_drivers(analysis_laps, driver_a, driver_b)
driver_metrics = calculate_driver_metrics(comparison_laps)


st.divider()
st.subheader("Métricas principais")

if driver_metrics.empty:
    st.info("Não foi possível calcular métricas para os pilotos selecionados.")
    st.stop()


metric_a = driver_metrics[driver_metrics["Driver"] == driver_a].iloc[0]
metric_b = driver_metrics[driver_metrics["Driver"] == driver_b].iloc[0]

a1, a2, a3, a4 = st.columns(4)

a1.metric(
    f"{driver_a} - ritmo médio",
    f"{metric_a['RitmoMedioSegundos']:.3f}s",
)

a2.metric(
    f"{driver_a} - melhor volta",
    f"{metric_a['MelhorVoltaSegundos']:.3f}s",
)

a3.metric(
    f"{driver_a} - consistência",
    f"{metric_a['ConsistenciaDesvioPadrao']:.3f}s",
    help="Desvio padrão dos tempos de volta. Quanto menor, mais consistente.",
)

a4.metric(
    f"{driver_a} - variação",
    f"{metric_a['VariacaoPerformanceSegundos']:.3f}s",
)


b1, b2, b3, b4 = st.columns(4)

b1.metric(
    f"{driver_b} - ritmo médio",
    f"{metric_b['RitmoMedioSegundos']:.3f}s",
)

b2.metric(
    f"{driver_b} - melhor volta",
    f"{metric_b['MelhorVoltaSegundos']:.3f}s",
)

b3.metric(
    f"{driver_b} - consistência",
    f"{metric_b['ConsistenciaDesvioPadrao']:.3f}s",
    help="Desvio padrão dos tempos de volta. Quanto menor, mais consistente.",
)

b4.metric(
    f"{driver_b} - variação",
    f"{metric_b['VariacaoPerformanceSegundos']:.3f}s",
)


st.dataframe(driver_metrics, use_container_width=True)


st.divider()
st.subheader("Comparação volta a volta")

fig_laps = px.line(
    comparison_laps.sort_values("LapNumber"),
    x="LapNumber",
    y="LapTimeSeconds",
    color="Driver",
    markers=True,
    title=f"Tempos de volta: {driver_a} x {driver_b}",
    labels={
        "LapNumber": "Volta",
        "LapTimeSeconds": "Tempo de volta em segundos",
        "Driver": "Piloto",
    },
)

st.plotly_chart(fig_laps, use_container_width=True)


delta_df = calculate_lap_delta_between_drivers(analysis_laps, driver_a, driver_b)

if not delta_df.empty:
    st.subheader("Delta entre pilotos")

    fig_delta = px.bar(
        delta_df,
        x="LapNumber",
        y="DeltaSegundos",
        title=f"Delta por volta: {driver_a} - {driver_b}",
        labels={
            "LapNumber": "Volta",
            "DeltaSegundos": f"Delta em segundos ({driver_a} - {driver_b})",
        },
    )

    st.plotly_chart(fig_delta, use_container_width=True)

    st.caption(
        f"Delta positivo: {driver_a} foi mais lento que {driver_b}. "
        f"Delta negativo: {driver_a} foi mais rápido."
    )


st.divider()
st.subheader("Análise de consistência")

consistency_df = driver_metrics[
    [
        "Driver",
        "Equipe",
        "VoltasAnalisadas",
        "RitmoMedioSegundos",
        "ConsistenciaDesvioPadrao",
        "CoeficienteVariacaoPercentual",
    ]
].sort_values("ConsistenciaDesvioPadrao")

st.dataframe(consistency_df, use_container_width=True)

fig_consistency = px.bar(
    consistency_df,
    x="Driver",
    y="ConsistenciaDesvioPadrao",
    title="Consistência por piloto",
    labels={
        "Driver": "Piloto",
        "ConsistenciaDesvioPadrao": "Desvio padrão em segundos",
    },
)

st.plotly_chart(fig_consistency, use_container_width=True)


st.divider()
st.subheader("Stints e estratégia de pneus")

stint_summary = calculate_stint_summary(laps_df)
selected_stints = stint_summary[stint_summary["Driver"].isin([driver_a, driver_b])]

if selected_stints.empty:
    st.info("Dados de stints não disponíveis para os pilotos selecionados.")
else:
    st.dataframe(selected_stints, use_container_width=True)

    fig_stints = px.timeline(
        selected_stints,
        x_start="VoltaInicial",
        x_end="VoltaFinal",
        y="Driver",
        color="Compound",
        title="Visualização de stints por piloto",
        labels={
            "VoltaInicial": "Volta inicial",
            "VoltaFinal": "Volta final",
            "Driver": "Piloto",
            "Compound": "Composto",
        },
    )

    st.plotly_chart(fig_stints, use_container_width=True)


st.subheader("Pit stops detectados")

pit_laps = extract_pit_stop_laps(laps_df)
selected_pit_laps = pit_laps[pit_laps["Driver"].isin([driver_a, driver_b])]

if selected_pit_laps.empty:
    st.info("Nenhum pit stop detectado para os pilotos selecionados ou dados indisponíveis.")
else:
    st.dataframe(selected_pit_laps, use_container_width=True)


st.divider()
st.subheader("Comparação de ritmo entre equipes")

available_teams = sorted(analysis_laps["Team"].dropna().unique().tolist())

if len(available_teams) >= 2:
    default_team_a_index = available_teams.index("Ferrari") if "Ferrari" in available_teams else 0
    default_team_b_index = available_teams.index("Red Bull Racing") if "Red Bull Racing" in available_teams else min(1, len(available_teams) - 1)

    team_col_a, team_col_b = st.columns(2)

    with team_col_a:
        team_a = st.selectbox(
            "Equipe A",
            options=available_teams,
            index=default_team_a_index,
            key="team_a_select",
        )

    with team_col_b:
        team_b = st.selectbox(
            "Equipe B",
            options=available_teams,
            index=default_team_b_index,
            key="team_b_select",
        )

    if team_a != team_b:
        team_laps = analysis_laps[analysis_laps["Team"].isin([team_a, team_b])]
        team_pace = calculate_team_pace(team_laps)
        team_metrics = calculate_team_metrics(team_laps)

        st.dataframe(team_metrics, use_container_width=True)

        fig_team = px.line(
            team_pace,
            x="LapNumber",
            y="RitmoMedioEquipeSegundos",
            color="Team",
            markers=True,
            title=f"Ritmo médio por volta: {team_a} x {team_b}",
            labels={
                "LapNumber": "Volta",
                "RitmoMedioEquipeSegundos": "Ritmo médio da equipe em segundos",
                "Team": "Equipe",
            },
        )

        st.plotly_chart(fig_team, use_container_width=True)

    else:
        st.warning("Selecione duas equipes diferentes para comparar.")
else:
    st.info("Não há equipes suficientes para comparação.")
