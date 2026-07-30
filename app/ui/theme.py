from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STYLE_PATH = PROJECT_ROOT / "assets" / "styles.css"

_HEAD = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Titillium+Web:wght@400;600;700;900&display=swap');"
    ":root{"
    "--f1-red:#E10600;"
    "--f1-font:'Titillium Web',-apple-system,sans-serif;"
    "--f1-veil:rgba(128,128,128,0.10);"
    "--f1-veil-strong:rgba(128,128,128,0.18);"
    "--f1-line:rgba(128,128,128,0.28);"
    "}</style>"
)


def tema_ativo():
    """Melhor esforco: devolve 'light'/'dark' se a versao expuser, senao None."""
    try:
        t = st.context.theme
        return getattr(t, "type", None) or getattr(t, "base", None)
    except Exception:
        return None


def load_global_styles() -> None:
    st.markdown(_HEAD, unsafe_allow_html=True)
    if STYLE_PATH.exists():
        st.markdown(
            f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def render_hero(title: str, subtitle: str, badge: str = "F1 Analytics Secure Lab") -> None:
    st.markdown(
        f"""
        <section class="f1-hero">
            <div class="f1-badge">🏎️ {badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_card_grid(cards: list[tuple[str, str]]) -> None:
    html_cards = ""
    for title, description in cards:
        html_cards += f"""
        <div class="f1-card">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
    st.markdown(f'<div class="f1-card-grid">{html_cards}</div>',
                unsafe_allow_html=True)


def render_section_title(title: str) -> None:
    st.markdown(f'<div class="f1-section-title">{title}</div>',
                unsafe_allow_html=True)
