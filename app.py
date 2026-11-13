"""MiBici Intelligence. De los datos a decisiones de movilidad.

  streamlit run app.py

Skeleton only: it loads and validates data and shows what was dropped. The four product sections
get built against tests/test_analytics_spec.py.
"""
import streamlit as st
from src.ingestion import find_data, load_trips, load_stations

st.set_page_config(page_title="MiBici Intelligence", page_icon="🚲", layout="wide")
st.title("MiBici Intelligence")
st.caption("De los datos a decisiones de movilidad. Datos abiertos de MiBici, Guadalajara.")


@st.cache_data(show_spinner="Cargando viajes…")
def _load(trips_path: str, stations_path: str | None):
    trips, report = load_trips(trips_path)
    stations = load_stations(stations_path) if stations_path else None
    return trips, stations, report


trips_path, stations_path = find_data("data")
with st.sidebar:
    st.header("Datos")
    up = st.file_uploader("Archivo de viajes (CSV de MiBici)", type="csv")
    source = up if up is not None else trips_path
    if source is None:
        st.error("No hay datos. Corre: python3 scripts/make_sample.py")
        st.stop()

trips, stations, report = _load(str(source) if up is None else up, str(stations_path) if stations_path else None)
with st.sidebar:
    st.success(report.as_text())
    st.write("Periodo:", trips["start"].min().date(), "a", trips["start"].max().date())
    if up is None and "sample" in str(trips_path):
        st.warning("Datos SINTÉTICOS de prueba. No son hallazgos reales.")

tab1, tab2, tab3 = st.tabs(["Panorama", "Desequilibrio", "Copiloto"])
with tab1:
    st.info("Por construir: KPIs, estaciones más activas, demanda por hora (src/analytics.py)")
with tab2:
    st.info("Por construir: desequilibrio por estación y recomendaciones (src/imbalance.py)")
    st.caption("Los flujos son históricos. No indican cuántas bicicletas hay ahora en una estación.")
with tab3:
    st.info("Por construir: copiloto que responde llamando a las funciones de análisis (src/copilot.py)")
