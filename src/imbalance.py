"""Station imbalance from historical flows. This is NOT current bike inventory, and the UI must say so.

TO BUILD. Contract in tests/test_analytics_spec.py.
"""
from __future__ import annotations
import pandas as pd


def station_imbalance(trips: pd.DataFrame, stations: pd.DataFrame | None = None, min_trips: int = 50) -> pd.DataFrame:
    """Columns: station_id, name, departures, arrivals, net_flow (arrivals - departures),
    imbalance_ratio (net_flow / (departures + arrivals)), kind ("se vacía" | "se llena" | "equilibrada").
    Stations with fewer than min_trips total are excluded. Sorted by abs(net_flow), descending."""
    raise NotImplementedError


def imbalance_by_hour(trips: pd.DataFrame, station_id: int) -> pd.DataFrame:
    """Columns: hour, departures, arrivals, net_flow. All 24 hours present."""
    raise NotImplementedError


def recommendations(imbalance: pd.DataFrame, n: int = 5) -> list[dict]:
    """Deterministic, evidence-backed suggestions that work with no LLM.
    [{"station_id", "name", "action", "evidence"}] where evidence quotes the numbers used."""
    raise NotImplementedError
