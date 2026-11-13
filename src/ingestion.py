"""Load and clean MiBici open data. No analytics here, only trustworthy rows.

Trip files:    datos_abiertos_YYYY_MM.csv   (https://www.mibici.net/es/datos-abiertos/)
Station file:  nomenclatura_YYYY_MM.csv

Column names have changed spelling over the years (accents, case, spaces), so every
column is matched by a normalized name instead of an exact string.
"""
from __future__ import annotations
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd

TRIP_ALIASES = {
    "trip_id": ["viaje_id", "viajeid", "id_viaje"],
    "user_id": ["usuario_id", "usuarioid", "id_usuario"],
    "gender": ["genero", "sexo"],
    "birth_year": ["ano_de_nacimiento", "anio_de_nacimiento", "a_o_de_nacimiento", "ano_nacimiento"],
    "start": ["inicio_del_viaje", "inicio_viaje", "inicio"],
    "end": ["fin_del_viaje", "fin_viaje", "fin"],
    "origin_id": ["origen_id", "origenid", "origen"],
    "dest_id": ["destino_id", "destinoid", "destino"],
}
STATION_ALIASES = {
    "station_id": ["id", "station_id"],
    "name": ["name", "nombre"],
    "code": ["obcn", "codigo"],
    "location": ["location", "ubicacion"],
    "lat": ["latitude", "latitud", "lat"],
    "lon": ["longitude", "longitud", "lon", "lng"],
    "status": ["status", "estatus", "estado"],
}
MIN_MINUTES, MAX_MINUTES = 1, 24 * 60


def _norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "_".join(s.strip().lower().replace("-", " ").split())


def _read_csv(path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except UnicodeDecodeError as e:
            last = e
    raise last


def _rename(df: pd.DataFrame, aliases: dict, required: list[str]) -> pd.DataFrame:
    normalized = {_norm(c): c for c in df.columns}
    mapping = {}
    for canonical, options in aliases.items():
        for opt in options:
            if opt in normalized:
                mapping[normalized[opt]] = canonical
                break
    out = df.rename(columns=mapping)
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError("Faltan columnas %s. Columnas encontradas: %s" % (missing, list(df.columns)))
    return out


@dataclass
class CleanReport:
    """What was removed and why. Show this in the app: never drop rows silently."""
    rows_in: int = 0
    rows_out: int = 0
    dropped: dict = field(default_factory=dict)

    def as_text(self) -> str:
        parts = ["%s: %d" % (k, v) for k, v in self.dropped.items() if v]
        return "%d de %d viajes válidos. Descartados: %s" % (self.rows_out, self.rows_in, ", ".join(parts) or "ninguno")


def load_trips(path) -> tuple[pd.DataFrame, CleanReport]:
    """Return (clean trips, report). Columns: trip_id, user_id, gender, birth_year, start, end,
    origin_id, dest_id, minutes, hour, weekday, date."""
    raw = _rename(_read_csv(path), TRIP_ALIASES, ["start", "end", "origin_id", "dest_id"])
    rep = CleanReport(rows_in=len(raw))
    df = raw.copy()
    for c in ("start", "end"):
        df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ("origin_id", "dest_id"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    bad_dates = df["start"].isna() | df["end"].isna()
    bad_station = df["origin_id"].isna() | df["dest_id"].isna()
    df["minutes"] = (df["end"] - df["start"]).dt.total_seconds() / 60
    too_short = df["minutes"] < MIN_MINUTES
    too_long = df["minutes"] > MAX_MINUTES
    rep.dropped = {
        "fecha inválida": int(bad_dates.sum()),
        "estación inválida": int((bad_station & ~bad_dates).sum()),
        "menos de %d min" % MIN_MINUTES: int((too_short & ~bad_dates & ~bad_station).sum()),
        "más de 24 h": int((too_long & ~bad_dates & ~bad_station).sum()),
    }
    df = df[~(bad_dates | bad_station | too_short | too_long)].copy()
    df["origin_id"] = df["origin_id"].astype(int)
    df["dest_id"] = df["dest_id"].astype(int)
    df["hour"] = df["start"].dt.hour
    df["weekday"] = df["start"].dt.dayofweek          # 0 = lunes
    df["date"] = df["start"].dt.date
    rep.rows_out = len(df)
    return df.reset_index(drop=True), rep


def load_stations(path) -> pd.DataFrame:
    """Return stations with columns station_id, name, lat, lon (plus code, location, status when present)."""
    df = _rename(_read_csv(path), STATION_ALIASES, ["station_id", "name"])
    df["station_id"] = pd.to_numeric(df["station_id"], errors="coerce")
    df = df.dropna(subset=["station_id"]).copy()
    df["station_id"] = df["station_id"].astype(int)
    for c in ("lat", "lon"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.drop_duplicates("station_id").reset_index(drop=True)


def find_data(folder="data") -> tuple[Path | None, Path | None]:
    """Newest real trip file and station file under data/raw, else the sample."""
    root = Path(folder)
    for sub in ("raw", "sample"):
        trips = sorted((root / sub).glob("datos_abiertos_*.csv"))
        stations = sorted((root / sub).glob("nomenclatura_*.csv"))
        if trips:
            return trips[-1], (stations[-1] if stations else None)
    return None, None
