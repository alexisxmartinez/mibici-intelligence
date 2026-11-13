"""The spec for the build. Every test here fails until the function is written.
Tell Cursor: "make tests/test_analytics_spec.py pass without changing the tests"."""
import pandas as pd, pytest
from src import analytics, imbalance


@pytest.fixture
def trips():
    # 10 trips. Station 1 sends 6 and receives 1. Station 2 sends 1 and receives 6. Station 3 is balanced.
    rows = [(1, 2, 8), (1, 2, 8), (1, 2, 8), (1, 2, 9), (1, 2, 9), (1, 3, 9), (2, 1, 18), (3, 2, 18), (3, 3, 12), (3, 3, 12)]
    df = pd.DataFrame(rows, columns=["origin_id", "dest_id", "hour"])
    df["start"] = pd.to_datetime("2026-10-05") + pd.to_timedelta(df["hour"], unit="h")
    df["minutes"] = 10.0
    df["end"] = df["start"] + pd.Timedelta(minutes=10)
    df["date"] = df["start"].dt.date
    df["weekday"] = 0
    return df


@pytest.fixture
def stations():
    return pd.DataFrame({"station_id": [1, 2, 3], "name": ["Uno", "Dos", "Tres"], "lat": [20.67] * 3, "lon": [-103.35] * 3})


def test_kpis(trips):
    k = analytics.kpis(trips)
    assert k["trips"] == 10 and k["avg_minutes"] == 10.0 and k["active_stations"] == 3
    assert k["peak_hour"] in (8, 9) and k["days"] == 1 and k["trips_per_day"] == 10.0


def test_top_stations(trips, stations):
    top = analytics.top_stations(trips, stations, n=2)
    assert list(top.columns) == ["station_id", "name", "departures", "arrivals", "total"]
    assert len(top) == 2 and top.iloc[0]["total"] >= top.iloc[1]["total"]
    row1 = top[top.station_id == 1].iloc[0]
    assert row1["departures"] == 6 and row1["arrivals"] == 1 and row1["name"] == "Uno"


def test_hourly_demand_has_all_24_hours(trips):
    h = analytics.hourly_demand(trips)
    assert list(h["hour"]) == list(range(24)) and h["trips"].sum() == 10
    assert analytics.hourly_demand(trips, station_id=1)["trips"].sum() == 6


def test_station_stats(trips):
    s = analytics.station_stats(trips, 1)
    assert s["departures"] == 6 and s["arrivals"] == 1 and s["net_flow"] == -5
    assert s["top_destinations"][0] == {"station_id": 2, "trips": 5}


def test_station_imbalance(trips, stations):
    im = imbalance.station_imbalance(trips, stations, min_trips=1)
    assert list(im["station_id"])[:2] == [1, 2] or list(im["station_id"])[:2] == [2, 1]
    s1 = im[im.station_id == 1].iloc[0]
    assert s1["net_flow"] == -5 and s1["kind"] == "se vacía" and round(s1["imbalance_ratio"], 3) == round(-5 / 7, 3)
    assert im[im.station_id == 2].iloc[0]["kind"] == "se llena"
    assert im[im.station_id == 3].iloc[0]["kind"] == "equilibrada"


def test_min_trips_filters_small_stations(trips, stations):
    assert imbalance.station_imbalance(trips, stations, min_trips=8).empty


def test_imbalance_by_hour(trips):
    h = imbalance.imbalance_by_hour(trips, 1)
    assert list(h["hour"]) == list(range(24))
    assert h.loc[h.hour == 8, "departures"].iloc[0] == 3 and h.loc[h.hour == 18, "arrivals"].iloc[0] == 1


def test_recommendations_quote_their_evidence(trips, stations):
    recs = imbalance.recommendations(imbalance.station_imbalance(trips, stations, min_trips=1), n=2)
    assert len(recs) == 2 and all({"station_id", "name", "action", "evidence"} <= set(r) for r in recs)
    r1 = next(r for r in recs if r["station_id"] == 1)
    assert "6" in r1["evidence"] and "1" in r1["evidence"]           # the real departures and arrivals appear
    assert "ahora" not in r1["action"].lower()                        # never claims current inventory
