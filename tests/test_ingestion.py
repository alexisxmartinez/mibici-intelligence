"""These pass today. They protect the part of the app that everything else trusts."""
import subprocess, sys, pathlib
import pandas as pd, pytest
from src.ingestion import load_trips, load_stations, find_data, _norm

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def sample():
    if not (ROOT / "data/sample/datos_abiertos_sample.csv").exists():
        subprocess.run([sys.executable, str(ROOT / "scripts/make_sample.py")], check=True)
    return ROOT / "data/sample/datos_abiertos_sample.csv", ROOT / "data/sample/nomenclatura_sample.csv"


def test_norm_handles_accents_and_case():
    assert _norm("Año_de_nacimiento") == "ano_de_nacimiento"
    assert _norm(" Inicio del Viaje ") == "inicio_del_viaje"


def test_load_trips_cleans_and_reports(sample):
    df, rep = load_trips(sample[0])
    assert rep.rows_in == 6000
    assert rep.rows_out == len(df) < rep.rows_in          # the three planted dirty rows are gone
    assert rep.dropped["fecha inválida"] >= 1 and rep.dropped["estación inválida"] >= 1
    assert sum(rep.dropped.values()) == rep.rows_in - rep.rows_out   # every dropped row is accounted for
    assert {"start", "end", "origin_id", "dest_id", "minutes", "hour", "weekday", "date"} <= set(df.columns)
    assert df["minutes"].between(1, 24 * 60).all()
    assert df["origin_id"].dtype.kind == "i"


def test_load_stations(sample):
    st = load_stations(sample[1])
    assert {"station_id", "name", "lat", "lon"} <= set(st.columns)
    assert st["station_id"].is_unique and len(st) == 12


def test_missing_columns_fail_loudly(tmp_path):
    p = tmp_path / "bad.csv"; pd.DataFrame({"a": [1]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="Faltan columnas"):
        load_trips(p)


def test_find_data_prefers_real_over_sample(sample, tmp_path):
    (tmp_path / "raw").mkdir(); (tmp_path / "sample").mkdir()
    (tmp_path / "sample/datos_abiertos_sample.csv").write_text("x")
    assert "sample" in str(find_data(tmp_path)[0])
    (tmp_path / "raw/datos_abiertos_2026_10.csv").write_text("x")
    assert "raw" in str(find_data(tmp_path)[0])
