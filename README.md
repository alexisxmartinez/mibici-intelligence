# MiBici Intelligence

De los datos a decisiones de movilidad. An operations copilot over MiBici open trip data (Guadalajara): where demand concentrates, which stations drain or fill, and what to look at first, with every number traceable to a function.

Status: starter kit. The data loader, the model client and the tests are in place. The product (analytics, imbalance, copilot, UI) gets built against the spec in `tests/test_analytics_spec.py`. This is a personal portfolio project and is not affiliated with MiBici.

## Run

```
python -m venv .venv && .venv\Scripts\activate        # Windows.  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python scripts/make_sample.py                          # synthetic sample, for tests only
python scripts/preflight.py                            # must end with READY
pytest -q                                              # 5 pass today, 8 are the build spec
streamlit run app.py
```

## Data

- Trips: `datos_abiertos_YYYY_MM.csv`, stations: `nomenclatura_YYYY_MM.csv`, from https://www.mibici.net/es/datos-abiertos/
- Put real files in `data/raw/` (not committed). The app prefers them over the sample.
- `data/sample/` is synthetic and labeled as such on screen. Never present numbers from it as findings.

## Copilot backends, tried in order

| Order | Backend | Set |
|---|---|---|
| 1 | Ollama on my own 4 GB laptop at home (Koatl), over Tailscale | `OLLAMA_URL`, `OLLAMA_MODEL` |
| 2 | Gemini | `GEMINI_API_KEY`, `GEMINI_MODELS` |
| 3 | No model | Nothing. The app shows the deterministic recommendations |

## Limits, stated up front

- Flows are historical. They say nothing about how many bikes are at a station now.
- Imbalance is departures versus arrivals. Real rebalancing also depends on docks, trucks and inventory, which this data does not contain.
- Recommendations are places to investigate, not instructions.

## Layout

`src/ingestion.py` clean rows and a report of what was dropped · `src/analytics.py` KPIs and demand · `src/imbalance.py` net flow and recommendations · `src/copilot.py` tool-calling agent · `src/llm.py` model backends · `app.py` layout only
