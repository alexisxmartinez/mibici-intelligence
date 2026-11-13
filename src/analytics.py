"""Deterministic numbers. The copilot may only quote what these functions return.

TO BUILD. The contract for each function is in tests/test_analytics_spec.py.
"""
from __future__ import annotations
import pandas as pd


def kpis(trips: pd.DataFrame) -> dict:
    """{"trips": int, "avg_minutes": float, "median_minutes": float, "active_stations": int,
        "peak_hour": int, "days": int, "trips_per_day": float}"""
    raise NotImplementedError


def top_stations(trips: pd.DataFrame, stations: pd.DataFrame | None = None, n: int = 10) -> pd.DataFrame:
    """Columns: station_id, name, departures, arrivals, total. Sorted by total, descending."""
    raise NotImplementedError


def hourly_demand(trips: pd.DataFrame, station_id: int | None = None) -> pd.DataFrame:
    """Columns: hour (0..23, all present), trips. Optionally for departures from one station."""
    raise NotImplementedError


def station_stats(trips: pd.DataFrame, station_id: int) -> dict:
    """{"station_id", "departures", "arrivals", "net_flow", "peak_departure_hour", "peak_arrival_hour",
        "top_destinations": [{"station_id", "trips"}], "avg_minutes"}"""
    raise NotImplementedError
