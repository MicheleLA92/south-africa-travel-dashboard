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
    assert marker["icon"] in marker["label"]
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


def test_restored_quiz_answers_include_known_reconstructed_answers():
    data = load_data()
    restored_answers = data.get("restored_quiz_results", [])
    by_name = {item.get("name"): item for item in restored_answers}

    assert {"Roberto", "Steffi"}.issubset(by_name)

    steffi_answers = by_name["Steffi"]["answers"]
    assert len(steffi_answers) == 6
    assert steffi_answers[0]["answer"] == "Elefant"
    assert steffi_answers[1]["answer"] == "wir nennen es „Abenteuer“"
    assert steffi_answers[5]["answer"] == "„Wir brauchen keinen Rückflug, wir brauchen einen grösseren Koffer für den Elefanten.“"

    roberto_answers = by_name["Roberto"]["answers"]
    assert len(roberto_answers) == 6
    assert roberto_answers[1]["answer"] == "Nie"
    assert roberto_answers[4]["answer"] == "80"


def test_today_magic_place_override_points_to_existing_non_blyde_place():
    data = load_data()
    overrides = data.get("magic_place_overrides", {})
    place_names = {place["name"] for place in data["magic_places"]}

    assert overrides["2026-08-03"] in place_names
    assert overrides["2026-08-03"] != "Blyde River Canyon"


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


def test_kapstadt_photo_stop_has_preferred_mountain_photo():
    data = load_data()
    kapstadt = next((stop for stop in data.get("photo_stops", []) if stop.get("name") == "Kapstadt"), None)

    assert kapstadt is not None
    assert kapstadt["region"] == "Kapstadt"
    assert kapstadt["photos"] == [
        "assets/kapstadt-coast-fotostopp-02.jpg",
        "assets/kapstadt-camps-bay-fotostopp.jpg",
    ]
    for photo in kapstadt["photos"]:
        assert Path(photo).exists(), f"Missing Kapstadt photo: {photo}"


def test_fyn_personal_evening_photo_stop_is_published():
    data = load_data()
    fyn = next((stop for stop in data.get("photo_stops", []) if stop.get("name") == "FYN Cape Town"), None)

    assert fyn is not None
    assert "Cape Town" in fyn["location"]
    assert "wunderbarer Abend" in fyn["summary"]
    assert "Sehr zu empfehlen" in fyn["summary"]
    assert fyn["kind"] == "restaurant"
    assert fyn["region"] == "Kapstadt"
    assert fyn["lat"] < -33 and fyn["lon"] > 18
    expected = [
        "assets/fyn/fyn-cape-town-05.jpg",
        "assets/fyn/fyn-cape-town-06.jpg",
        "assets/fyn/fyn-cape-town-07.jpg",
        "assets/fyn/fyn-cape-town-08.jpg",
        "assets/fyn/fyn-cape-town-09.jpg",
        "assets/fyn/fyn-cape-town-10.jpg",
        "assets/fyn/fyn-cape-town-11.jpg",
        "assets/fyn/fyn-cape-town-12.jpg",
    ]
    assert fyn["photos"] == expected
    for photo in fyn["photos"]:
        assert Path(photo).exists(), f"Missing FYN photo: {photo}"


def test_fyn_restaurant_has_gallery_like_marloth_stay():
    data = load_data()
    restaurant = data["restaurant"]
    fyn = next(item for item in data["restaurants"] if item["name"] == "FYN Restaurant")

    expected = [
        "assets/fyn/fyn-cape-town-05.jpg",
        "assets/fyn/fyn-cape-town-06.jpg",
        "assets/fyn/fyn-cape-town-07.jpg",
        "assets/fyn/fyn-cape-town-08.jpg",
        "assets/fyn/fyn-cape-town-09.jpg",
        "assets/fyn/fyn-cape-town-10.jpg",
        "assets/fyn/fyn-cape-town-11.jpg",
        "assets/fyn/fyn-cape-town-12.jpg",
    ]
    assert restaurant["images"] == expected
    assert fyn["images"] == expected
    assert "wunderbarer" in fyn["why"]
    for photo in expected:
        assert Path(photo).exists(), f"Missing FYN restaurant photo: {photo}"


def test_paulines_greenpoint_breakfast_spot_is_recommended_with_photos():
    data = load_data()
    spot = next(item for item in data["restaurants"] if item["name"] == "Pauline's Greenpoint")

    assert "Cape Town" in spot["location"]
    assert "Super Frühstücksspot" in spot["why"]
    assert "super Essen" in spot["why"]
    assert "Avocado" not in spot["why"]
    assert spot["link"] == "https://maps.app.goo.gl/Rtho4z8KyPSoBFFz7"
    expected = [
        "assets/paulines-greenpoint/paulines-greenpoint-01.jpg",
        "assets/paulines-greenpoint/paulines-greenpoint-02.jpg",
    ]
    assert spot["images"] == expected
    for photo in expected:
        assert Path(photo).exists(), f"Missing Pauline's photo: {photo}"


def test_chefs_warehouse_tintswalo_has_uploaded_food_gallery():
    data = load_data()
    restaurant = next(item for item in data["restaurants"] if item["name"] == "Chefs Warehouse at Tintswalo Atlantic")

    expected = [
        "assets/chefs-warehouse-tintswalo/chefs-warehouse-tintswalo-01.jpg",
        "assets/chefs-warehouse-tintswalo/chefs-warehouse-tintswalo-02.jpg",
        "assets/chefs-warehouse-tintswalo/chefs-warehouse-tintswalo-03.jpg",
        "assets/chefs-warehouse-tintswalo/chefs-warehouse-tintswalo-04.jpg",
        "assets/chefs-warehouse-tintswalo/chefs-warehouse-tintswalo-05.jpg",
        "assets/chefs-warehouse-tintswalo/chefs-warehouse-tintswalo-06.jpg",
    ]
    assert restaurant["location"] == "Cape Town / Hout Bay"
    assert restaurant["link"] == "https://maps.app.goo.gl/xSp3384MMfwmqRwd8"
    assert restaurant["region"] == "Kapstadt"
    assert -35 <= restaurant["lat"] <= -34
    assert 18 <= restaurant["lon"] <= 19
    assert restaurant["images"] == expected
    for photo in expected:
        assert Path(photo).exists(), f"Missing Chefs Warehouse Tintswalo photo: {photo}"


def test_paulines_greenpoint_is_on_photo_map():
    data = load_data()
    spot = next((item for item in data["photo_stops"] if item["name"] == "Pauline's Greenpoint"), None)

    assert spot is not None
    assert "Green Point" in spot["location"]
    assert spot["lat"] < -33 and spot["lon"] > 18
    assert "Super Frühstücksspot" in spot["summary"]
    assert "super Essen" in spot["summary"]
    assert spot["kind"] == "restaurant"
    assert spot["region"] == "Kapstadt"
    assert "Avocado" not in spot["summary"]
    assert spot["photos"] == [
        "assets/paulines-greenpoint/paulines-greenpoint-01.jpg",
        "assets/paulines-greenpoint/paulines-greenpoint-02.jpg",
    ]
    for photo in spot["photos"]:
        assert Path(photo).exists(), f"Missing Pauline's photo stop photo: {photo}"


def test_noordhoek_beach_is_on_photo_map_with_sunset_photos():
    data = load_data()
    spot = next((item for item in data["photo_stops"] if item["name"] == "Noordhoek Beach"), None)

    assert spot is not None
    assert spot["location"] == "Cape Town / Noordhoek Beach"
    assert spot["region"] == "Kapstadt"
    assert -35 <= spot["lat"] <= -34
    assert 18 <= spot["lon"] <= 19
    assert spot["summary"] == "Weitläufiger Strandmoment bei Noordhoek Beach mit Sonnenuntergang, Meer und Bergen"
    assert spot["photos"] == [
        "assets/noordhoek-beach/noordhoek-beach-01.jpg",
        "assets/noordhoek-beach/noordhoek-beach-02.jpg",
        "assets/noordhoek-beach/noordhoek-beach-03.jpg",
    ]
    for photo in spot["photos"]:
        assert Path(photo).exists(), f"Missing Noordhoek Beach photo: {photo}"


def test_franschhoek_wine_tram_activity_has_photo_and_map_coordinates():
    data = load_data()
    activity = next((item for item in data.get("activities", []) if item["name"] == "Franschhoek Wine Tram"), None)

    assert activity is not None
    assert activity["location"] == "Franschhoek"
    assert activity["link"] == "https://maps.app.goo.gl/PWEVXGeEe1G4KaHj6"
    assert activity["region"] == "Kapstadt"
    assert -34 <= activity["lat"] <= -33
    assert 19 <= activity["lon"] <= 20
    assert activity["images"] == [
        "assets/franschhoek-wine-tram/franschhoek-wine-tram-01.jpg",
        "assets/franschhoek-wine-tram/franschhoek-wine-tram-02.jpg",
        "assets/franschhoek-wine-tram/franschhoek-wine-tram-03.jpg",
        "assets/franschhoek-wine-tram/franschhoek-wine-tram-04.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Franschhoek Wine Tram photo: {photo}"


def test_all_photo_stops_are_grouped_by_region():
    data = load_data()
    regions = {stop.get("region") for stop in data["photo_stops"]}

    assert None not in regions
    assert "Kapstadt" in regions
    assert "Marloth Park / Kruger" in regions
