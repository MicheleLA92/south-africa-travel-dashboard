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
        "East London",
        "Johannesburg",
        "Kruger National Park",
    ]


def test_map_route_follows_coast_before_turning_inland():
    data = load_data()
    route = data["map_route"]
    names = [point["name"] for point in route]

    assert names[:7] == [
        "Cape Town",
        "Hermanus",
        "Mossel Bay",
        "Knysna",
        "Tsitsikamma",
        "Gqeberha / Port Elizabeth",
        "East London",
    ]
    assert "Durban" not in names
    assert "Coffee Bay / Wild Coast" not in names
    assert names[-2:] == ["Johannesburg", "Kruger National Park"]
    assert len(route) >= 9


def test_map_has_elephant_marker_near_port_elizabeth():
    data = load_data()
    marker = data["map_elephant_marker"]

    assert marker["icon"] == "🐘"
    assert marker["icon_url"].startswith("data:image/svg+xml")
    assert marker["name"] == "Addo Elephant National Park"
    assert "Port Elizabeth" in marker["label"] or "Gqeberha" in marker["label"]
    assert -34 <= marker["lat"] <= -32
    assert 24 <= marker["lon"] <= 27


def test_friend_quiz_questions_have_options():
    data = load_data()
    quiz = data["quiz"]
    questions = quiz["questions"]

    assert quiz["title"]
    assert quiz["description"]
    assert len(questions) == 6
    for question in questions:
        assert question["question"]
        assert len(question["options"]) >= 4
        assert "correct_index" not in question


def test_top_metrics_promote_friend_quiz_instead_of_planning():
    data = load_data()
    metrics = data["briefing"]["metrics"]
    labels = [metric["label"] for metric in metrics]
    values = [metric["value"] for metric in metrics]

    assert labels[-1] == "Freunde-Quiz"
    assert "Planung" not in labels
    assert "68%" not in values


def test_magic_places_rotate_with_unique_images():
    data = load_data()
    places = data["magic_places"]
    images = [place["image"] for place in places]
    names = [place["name"] for place in places]

    assert len(places) >= 7
    assert len(set(images)) == len(images)
    assert len(set(names)) == len(names)
    assert all("sanparks" not in place["link"].lower() for place in places)
    for place in places:
        assert place["name"]
        assert place["caption"]
        assert place["description"]
        assert place["image"].startswith("https://upload.wikimedia.org/")
        assert place["link"].startswith("https://")
