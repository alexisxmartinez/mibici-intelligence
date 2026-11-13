#!/usr/bin/env python3
"""Run this the night before and again at the venue. It answers: can I demo right now?

  python3 scripts/preflight.py
"""
import importlib, os, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
ok = True

def line(good, text):
    global ok
    ok = ok and good
    print(("PASS  " if good else "FAIL  ") + text)

print("Python", sys.version.split()[0])
for mod in ("pandas", "streamlit", "plotly", "duckdb", "pytest"):
    try:
        m = importlib.import_module(mod); line(True, "%s %s" % (mod, getattr(m, "__version__", "")))
    except Exception as e:
        line(False, "%s missing: pip install -r requirements.txt" % mod)

from src.ingestion import find_data, load_trips, load_stations
trips_path, stations_path = find_data(root / "data")
line(trips_path is not None, "trip file: %s" % trips_path)
if trips_path:
    df, rep = load_trips(trips_path)
    line(len(df) > 0, rep.as_text())
    print("      periodo:", df["start"].min(), "a", df["start"].max(), "| real" if "raw" in str(trips_path) else "| SINTÉTICO, solo para pruebas")
if stations_path:
    st = load_stations(stations_path); line(len(st) > 0, "%d estaciones" % len(st))
else:
    line(False, "no station file (nomenclatura_*.csv)")

from src import llm
print("INFO  LLM_ORDER=%s OLLAMA_URL=%s GEMINI_API_KEY=%s" % (os.getenv("LLM_ORDER", "ollama,gemini"), os.getenv("OLLAMA_URL", "(unset)"), "set" if os.getenv("GEMINI_API_KEY") else "(unset)"))
print("INFO  copilot backend right now:", llm.status())
print("\nREADY" if ok else "\nNOT READY")
sys.exit(0 if ok else 1)
