import json
from pathlib import Path


def load_data():
    return json.loads(Path("data/sample_briefing.json").read_text(encoding="utf-8"))


def test_route_stops_have_coordinates_for_map():
    data = load_data()

    for stop in data["route"]:
        assert "lat" in stop, f"{stop['name']} needs a latitude"
        assert "lon" in stop, f"{stop['name']} needs a longitude"
        assert isinstance(stop["lat"], (int, float))
        assert isinstance(stop["lon"], (int, float))
        assert -35 <= stop["lat"] <= -22
        assert 16 <= stop["lon"] <= 33


def test_route_order_matches_trip_plan():
    data = load_data()

    assert [stop["name"] for stop in data["route"]] == [
        "Cape Town",
        "Garden Route",
        "Durban",
        "Johannesburg",
        "Kruger National Park",
    ]
