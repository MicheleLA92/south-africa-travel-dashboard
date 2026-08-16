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


def test_route_order_matches_actual_trip():
    data = load_data()

    assert [stop["name"] for stop in data["route"]] == [
        "Cape Town",
        "Franschhoek",
        "Betty's Bay / Stony Point",
        "Swellendam",
        "Mossel Bay",
        "Wilderness",
        "Knysna",
        "Robberg Hiking Trail",
        "The Crags",
        "Jeffreys Bay",
        "Alexandria Dune Field Running",
        "Schotia Safaris",
        "Middle Beach Kite Spot",
        "Terry Fitzgerald Trailrunning",
        "Kidds Beach",
        "Cove View B&B",
    ]


def test_map_route_shows_only_actual_driven_route():
    data = load_data()
    route = data["map_route"]
    names = [point["name"] for point in route]
    major_stops = [
        "Cape Town",
        "Franschhoek",
        "Betty's Bay / Stony Point",
        "Swellendam",
        "Mossel Bay",
        "Wilderness",
        "Knysna",
        "Robberg Hiking Trail",
        "The Crags",
        "Jeffreys Bay",
        "Alexandria Dune Field Running",
        "Schotia Safaris",
        "Middle Beach Kite Spot",
        "Terry Fitzgerald Trailrunning",
        "Kidds Beach",
        "Cove View B&B",
    ]

    assert all(point["kind"] == "actual" for point in route)
    assert len(route) > len(major_stops)
    assert [name for name in names if name in major_stops] == major_stops
    mossel_index = names.index("Mossel Bay")
    wilderness_index = names.index("Wilderness")
    assert wilderness_index - mossel_index > 10
    assert "East London" not in names
    assert "Johannesburg" not in names
    assert "Kruger National Park" not in names
    assert "Tsitsikamma" not in names


def test_map_route_includes_morning_drive_to_sedge_links():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    wilderness_index = names.index("Wilderness")
    sedge_links_index = names.index("Sedge Links Golf Club")
    morning_segment = names[wilderness_index:sedge_links_index + 1]

    assert wilderness_index < sedge_links_index
    assert "Island Lake N2 link" in morning_segment
    assert "Swartvlei N2 link" in morning_segment
    assert "Sedgefield N2 link" in morning_segment


def test_map_route_extends_to_knysna_belle_guest_house():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    sedge_links_index = names.index("Sedge Links Golf Club")
    knysna_belle_index = names.index("The Knysna Belle Guest House")
    knysna_segment = names[sedge_links_index:knysna_belle_index + 1]

    assert sedge_links_index < knysna_belle_index
    assert "Groenvlei N2 link" in knysna_segment
    assert "Knysna west N2 link" in knysna_segment
    assert "Leisure Island causeway link" in knysna_segment


def test_map_route_extends_to_bollards_bay_canoe_stop():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    guest_house_index = names.index("The Knysna Belle Guest House")
    canoe_index = names.index("Bollards Bay Kanufahrt")
    canoe_segment = names[guest_house_index:canoe_index + 1]

    assert guest_house_index < canoe_index
    assert "Bollards Bay Beach road link" in canoe_segment


def test_map_route_extends_to_robberg_hiking_trail():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    canoe_index = names.index("Bollards Bay Kanufahrt")
    hiking_index = names.index("Robberg Hiking Trail")
    hiking_segment = names[canoe_index:hiking_index + 1]

    assert canoe_index < hiking_index
    assert "Harkerville N2 link" in hiking_segment
    assert "Plettenberg Bay Robberg Road link" in hiking_segment
    assert "Robberg Nature Reserve approach link" in hiking_segment


def test_map_route_extends_to_trogon_house():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    robberg_index = names.index("Robberg Hiking Trail")
    trogon_index = names.index("Trogon House and Forest Spa")
    trogon_segment = names[robberg_index:trogon_index + 1]

    assert robberg_index < trogon_index
    assert "Plettenberg Bay east N2 link" in trogon_segment
    assert "The Crags N2 link" in trogon_segment
    assert "Trogon House and Forest Spa forest road link" in trogon_segment


def test_map_route_extends_to_monkeyland():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    trogon_index = names.index("Trogon House and Forest Spa")
    monkeyland_index = names.index("Monkeyland")
    monkeyland_segment = names[trogon_index:monkeyland_index + 1]

    assert trogon_index < monkeyland_index
    assert "Monkeyland road link" in monkeyland_segment


def test_map_route_extends_to_jeffreys_bay():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    monkeyland_index = names.index("Monkeyland")
    jeffreys_index = names.index("Jeffreys Bay")
    jeffreys_segment = names[monkeyland_index:jeffreys_index + 1]

    assert monkeyland_index < jeffreys_index
    assert "Storms River N2 link" in jeffreys_segment
    assert "Humansdorp N2 link" in jeffreys_segment
    assert "Jeffreys Bay R102 link" in jeffreys_segment


def test_map_route_extends_to_alexandria_dune_field_running():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    jeffreys_index = names.index("Jeffreys Bay")
    running_index = names.index("Alexandria Dune Field Running")
    running_segment = names[jeffreys_index:running_index + 1]

    assert jeffreys_index < running_index
    assert "Gamtoos River N2 link" in running_segment
    assert "Van Stadens N2 link" in running_segment
    assert "Gqeberha inland N2 link" in running_segment
    assert "Colchester N2 link" in running_segment
    assert "Sundays River north bank link" in running_segment
    assert "Alexandria Dune Field inland ridge link" in running_segment


def test_map_route_extends_to_schotia_safaris():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    running_index = names.index("Alexandria Dune Field Running")
    schotia_index = names.index("Schotia Safaris")
    schotia_segment = names[running_index:schotia_index + 1]

    assert running_index < schotia_index
    assert "Alexandria west R72 link" in schotia_segment
    assert "Paterson R342 link" in schotia_segment
    assert "Schotia Safaris access link" in schotia_segment


def test_map_route_extends_to_middle_beach_kite_spot():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    schotia_index = names.index("Schotia Safaris")
    kite_index = names.index("Middle Beach Kite Spot")
    kite_segment = names[schotia_index:kite_index + 1]

    assert schotia_index < kite_index
    assert "Paterson south R72 link" in kite_segment
    assert "Alexandria R72 east link" in kite_segment
    assert "Kenton-on-Sea R72 link" in kite_segment


def test_map_route_extends_to_terry_fitzgerald_trailrunning():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    kite_index = names.index("Middle Beach Kite Spot")
    trail_index = names.index("Terry Fitzgerald Trailrunning")
    trail_segment = names[kite_index:trail_index + 1]

    assert kite_index < trail_index
    assert "Port Alfred R72 link" in trail_segment
    assert "Terry Fitzgerald access link" in trail_segment


def test_map_route_extends_to_kidds_beach_stop():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    trail_index = names.index("Terry Fitzgerald Trailrunning")
    beach_index = names.index("Kidds Beach")
    beach_segment = names[trail_index:beach_index + 1]

    assert trail_index < beach_index
    assert "Port Alfred east R72 link" in beach_segment
    assert "Fish River R72 link" in beach_segment
    assert "Hamburg R72 link" in beach_segment
    assert "Kidds Beach R72 link" in beach_segment


def test_map_route_extends_to_cove_view_bnb():
    data = load_data()
    names = [point["name"] for point in data["map_route"]]

    beach_index = names.index("Kidds Beach")
    cove_index = names.index("Cove View B&B")
    cove_segment = names[beach_index:cove_index + 1]

    assert beach_index < cove_index
    assert "Cove Rock coastal link" in cove_segment


def test_route_line_connects_cape_town_coastal_photo_stops():
    data = load_data()
    main_names = [point["name"] for point in data["map_route"]]
    extensions = data.get("map_route_extensions", [])
    cape_extension = next(item for item in extensions if item["name"] == "Cape Town Küstenstopps")
    coast_names = [point["name"] for point in cape_extension["points"]]

    assert "Noordhoek Beach coast link" in coast_names
    assert "Hout Bay east road link" in coast_names
    assert "Hout Bay inland road link" in coast_names
    assert "Chapmans Peak entrance road link" in coast_names
    assert "Noordhoek inland approach link" in coast_names
    assert coast_names.index("Hout Bay east road link") < coast_names.index("Chapmans Peak entrance road link") < coast_names.index("Noordhoek Beach coast link")
    assert "Cape Town route return" not in main_names
    assert "Constantia coast link" not in main_names
    assert "Ou Kaapse Weg coast link" not in main_names


def test_moontide_riverside_lodge_replaces_rhino_post_stay():
    data = load_data()
    stays = data["stays"]
    stay_names = [stay["name"] for stay in stays]
    moontide = next(item for item in stays if item["name"] == "Moontide Riverside Lodge")

    assert "Rhino Post Safari Lodge" not in stay_names
    assert moontide["location"] == "Wilderness / Garden Route"
    assert moontide["link"] == "https://maps.app.goo.gl/wAuc6D9jhGChsRCk6"
    assert moontide["region"] == "Garden Route"
    assert moontide["kind"] == "stay"
    assert -34.5 <= moontide["lat"] <= -33.5
    assert 22 <= moontide["lon"] <= 23
    assert moontide["images"] == [
        "assets/moontide-riverside-lodge/moontide-riverside-lodge-01.jpg",
        "assets/moontide-riverside-lodge/moontide-riverside-lodge-02.jpg",
    ]
    assert "videos" not in moontide
    for photo in moontide["images"]:
        assert Path(photo).exists(), f"Missing Moontide Riverside Lodge photo: {photo}"


def test_cove_view_bnb_is_top_stay_with_photos():
    data = load_data()
    stay = next((item for item in data["stays"] if item["name"] == "Cove View B&B"), None)
    activity_names = [item["name"] for item in data.get("activities", [])]

    assert stay is not None
    assert "Cove View B&B" not in activity_names
    assert stay["location"] == "Cove Rock / East London"
    assert stay["why"] == "Ruhige Unterkunft mit schönem Meerblick, gemütlichem Zimmer und Balkon — perfekt als entspannter Küstenstopp bei East London."
    assert stay["tip"] == ""
    assert stay["link"] == "https://maps.app.goo.gl/8DVGaHocwoEVTHNf8"
    assert stay["region"] == "Eastern Cape / Addo"
    assert stay["kind"] == "stay"
    assert -34 <= stay["lat"] <= -33
    assert 27 <= stay["lon"] <= 28
    assert stay["images"] == [
        "assets/cove-view-bnb/cove-view-bnb-01.jpg",
        "assets/cove-view-bnb/cove-view-bnb-02.jpg",
        "assets/cove-view-bnb/cove-view-bnb-03.jpg",
    ]
    for photo in stay["images"]:
        assert Path(photo).exists(), f"Missing Cove View B&B photo: {photo}"


def test_knysna_belle_guest_house_has_photos():
    data = load_data()
    stays = data["stays"]
    stay = next((item for item in stays if item["name"] == "The Knysna Belle Guest House"), None)

    assert stay is not None
    assert stay["location"] == "Knysna / Leisure Island"
    assert stay["link"] == "https://maps.app.goo.gl/1eKptN5MPdNgRD6h6"
    assert stay["region"] == "Garden Route"
    assert stay["kind"] == "stay"
    assert -35 <= stay["lat"] <= -34
    assert 23 <= stay["lon"] <= 24
    assert stay["images"] == [
        "assets/knysna-belle-guest-house/knysna-belle-guest-house-01.jpg",
        "assets/knysna-belle-guest-house/knysna-belle-guest-house-02.jpg",
        "assets/knysna-belle-guest-house/knysna-belle-guest-house-03.jpg",
    ]
    for photo in stay["images"]:
        assert Path(photo).exists(), f"Missing The Knysna Belle Guest House photo: {photo}"


def test_trogon_house_is_current_stay_with_photos():
    data = load_data()
    stays = data["stays"]
    stay = next((item for item in stays if item["name"] == "Trogon House and Forest Spa"), None)

    assert data["stay"]["name"] == "Trogon House and Forest Spa"
    assert stay is not None
    assert stay["location"] == "The Crags / Plettenberg Bay"
    assert stay["link"] == "https://maps.app.goo.gl/1fj2AJuKTBAL9zUN8"
    assert stay["region"] == "Garden Route"
    assert stay["kind"] == "stay"
    assert -34.5 <= stay["lat"] <= -33.5
    assert 23 <= stay["lon"] <= 24
    assert stay["images"] == [
        "assets/trogon-house/trogon-house-01.jpg",
        "assets/trogon-house/trogon-house-02.jpg",
        "assets/trogon-house/trogon-house-03.jpg",
        "assets/trogon-house/trogon-house-04.jpg",
    ]
    for photo in stay["images"]:
        assert Path(photo).exists(), f"Missing Trogon House and Forest Spa photo: {photo}"


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


def test_carola_anns_mossel_bay_is_recommended_with_food_photos():
    data = load_data()
    restaurant = next(item for item in data["restaurants"] if item["name"] == "Carola Ann's")

    expected = [
        "assets/carola-anns-mossel-bay/carola-anns-mossel-bay-01.jpg",
        "assets/carola-anns-mossel-bay/carola-anns-mossel-bay-02.jpg",
    ]
    assert restaurant["location"] == "Mossel Bay / 38 Marsh Street"
    assert restaurant["link"] == "https://maps.app.goo.gl/9KFzrHL45iUrntcg6?g_st=ac"
    assert restaurant["region"] == "Garden Route"
    assert -35 <= restaurant["lat"] <= -34
    assert 22 <= restaurant["lon"] <= 23
    assert restaurant["images"] == expected
    for photo in expected:
        assert Path(photo).exists(), f"Missing Carola Ann's photo: {photo}"


def test_restaurant_recommendations_do_not_use_secondary_tip_text():
    data = load_data()

    for restaurant in data["restaurants"]:
        assert restaurant.get("tip", "") == ""


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


def test_schotia_safaris_is_top_activity_with_elephant_symbol_and_photos():
    data = load_data()
    activities = data.get("activities", [])
    activity = next((item for item in activities if item["name"] == "Schotia Safaris"), None)

    assert activities[0]["name"] == "Schotia Safaris"
    assert activity is not None
    assert activity["location"] == "Schotia Safaris, Addo"
    assert activity["link"] == "https://maps.app.goo.gl/xBRNp14mRPJWq9Zz8?g_st=ac"
    assert activity["region"] == "Eastern Cape / Addo"
    assert activity["kind"] == "elephant"
    assert "tollem Guide" in activity["why"]
    assert "Nachtessen" in activity["why"]
    assert -34 <= activity["lat"] <= -33
    assert 25 <= activity["lon"] <= 26
    assert activity["images"] == [
        "assets/schotia-safaris/schotia-safaris-01.jpg",
        "assets/schotia-safaris/schotia-safaris-02.jpg",
        "assets/schotia-safaris/schotia-safaris-03.jpg",
        "assets/schotia-safaris/schotia-safaris-04.jpg",
        "assets/schotia-safaris/schotia-safaris-05.jpg",
        "assets/schotia-safaris/schotia-safaris-06.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Schotia Safaris photo: {photo}"


def test_terry_fitzgerald_trailrunning_is_photo_stop_not_top_activity():
    data = load_data()
    name = "Terry Fitzgerald Trailrunning"
    activity_names = [item["name"] for item in data.get("activities", [])]
    stop = next((item for item in data.get("photo_stops", []) if item["name"] == name), None)

    assert name not in activity_names
    assert stop is not None
    assert stop["location"] == "Terry Fitzgerald Private Nature Reserve / Port Alfred"
    assert stop["link"] == "https://maps.app.goo.gl/JNZV7nbNhgyrKhBS9"
    assert stop["region"] == "Eastern Cape / Addo"
    assert stop["kind"] == "running"
    assert stop["summary"] == "Trailrunning Ort."
    assert stop["photos"] == [
        "assets/terry-fitzgerald-trailrunning/terry-fitzgerald-trailrunning-01.jpg",
    ]
    for photo in stop["photos"]:
        assert Path(photo).exists(), f"Missing Terry Fitzgerald Trailrunning photo: {photo}"
    assert -34 <= stop["lat"] <= -33
    assert 26 <= stop["lon"] <= 27


def test_middle_beach_kite_spot_activity_has_kite_kind():
    data = load_data()
    activities = data.get("activities", [])
    activity = next((item for item in activities if item["name"] == "Middle Beach Kite Spot"), None)

    assert activity is not None
    assert activities[1]["name"] == "Middle Beach Kite Spot"
    assert activity["location"] == "Middle Beach, Kenton-on-Sea"
    assert activity["link"] == "https://maps.app.goo.gl/J7bQ5WHK5PGQH318A"
    assert activity["region"] == "Eastern Cape / Addo"
    assert activity["kind"] == "kite"
    assert "Kite fliegen" in activity["why"]
    assert "Kiten lernen" not in activity["why"]
    assert activity["images"] == [
        "assets/middle-beach-kite-spot/middle-beach-kite-spot-01.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Middle Beach Kite Spot photo: {photo}"
    assert -34 <= activity["lat"] <= -33
    assert 26 <= activity["lon"] <= 27


def test_stony_point_penguin_activity_has_photos_and_penguin_kind():
    data = load_data()
    activity = next((item for item in data.get("activities", []) if item["name"] == "Stony Point Penguin Colony"), None)

    assert activity is not None
    assert activity["location"] == "Betty's Bay / Stony Point"
    assert activity["link"] == "https://maps.app.goo.gl/TKzg4csA1hKPNXdV6"
    assert activity["region"] == "Kapstadt"
    assert activity["kind"] == "penguin"
    assert -35 <= activity["lat"] <= -34
    assert 18 <= activity["lon"] <= 19
    assert activity["images"] == [
        "assets/stony-point-penguins/stony-point-penguins-01.jpg",
        "assets/stony-point-penguins/stony-point-penguins-02.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Stony Point Penguin photo: {photo}"


def test_neevrah_art_decor_activity_has_photos_and_bitcoin_funfact():
    data = load_data()
    activity = next((item for item in data.get("activities", []) if item["name"] == "Neevrah Art + Décor"), None)

    assert activity is not None
    assert activity["location"] == "Timberlake Village / Wilderness"
    assert activity["link"] == "https://maps.app.goo.gl/BCBAeVe3rcsB3kMZ9"
    assert activity["region"] == "Garden Route"
    assert activity["kind"] == "art"
    assert "Bitcoin" in activity["why"]
    assert -35 <= activity["lat"] <= -33
    assert 22 <= activity["lon"] <= 23
    assert activity["images"] == [
        "assets/neevrah-art-decor/neevrah-art-decor-01.jpg",
        "assets/neevrah-art-decor/neevrah-art-decor-02.jpg",
        "assets/neevrah-art-decor/neevrah-art-decor-03.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Neevrah Art + Décor photo: {photo}"


def test_sedge_links_golf_activity_has_photos_and_golf_kind():
    data = load_data()
    activity = next((item for item in data.get("activities", []) if item["name"] == "Sedge Links Golf Club"), None)

    assert activity is not None
    assert activity["location"] == "Sedgefield / Garden Route"
    assert activity["link"] == "https://maps.app.goo.gl/wQeveGS45N7iqre5A?g_st=ac"
    assert activity["region"] == "Garden Route"
    assert activity["kind"] == "golf"
    assert -35 <= activity["lat"] <= -33
    assert 22 <= activity["lon"] <= 23
    assert activity["images"] == [
        "assets/sedge-links-golf-club/sedge-links-golf-club-01.jpg",
        "assets/sedge-links-golf-club/sedge-links-golf-club-02.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Sedge Links Golf Club photo: {photo}"


def test_bollards_bay_canoe_activity_has_photo_and_canoe_kind():
    data = load_data()
    activity = next((item for item in data.get("activities", []) if item["name"] == "Bollards Bay Kanufahrt"), None)

    assert activity is not None
    assert activity["location"] == "Bollards Bay Beach / Leisure Island, Knysna"
    assert activity["link"] == "https://maps.app.goo.gl/oUieEaKUJnYLrtYcA?g_st=ac"
    assert activity["region"] == "Garden Route"
    assert activity["kind"] == "canoe"
    assert -35 <= activity["lat"] <= -34
    assert 23 <= activity["lon"] <= 24
    assert activity["images"] == ["assets/bollards-bay-canoe/bollards-bay-canoe-01.jpg"]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Bollards Bay canoe photo: {photo}"


def test_robberg_hiking_activity_has_photos_and_hiking_kind():
    data = load_data()
    activity = next((item for item in data.get("activities", []) if item["name"] == "Robberg Hiking Trail"), None)

    assert activity is not None
    assert activity["location"] == "Robberg Nature Reserve / Plettenberg Bay"
    assert activity["link"] == "https://maps.app.goo.gl/cqSLHAf8n1jZwT8ZA"
    assert activity["region"] == "Garden Route"
    assert activity["kind"] == "hiking"
    assert -35 <= activity["lat"] <= -34
    assert 23 <= activity["lon"] <= 24
    assert activity["images"] == [
        "assets/robberg-hiking-trail/robberg-hiking-trail-01.jpg",
        "assets/robberg-hiking-trail/robberg-hiking-trail-02.jpg",
        "assets/robberg-hiking-trail/robberg-hiking-trail-03.jpg",
        "assets/robberg-hiking-trail/robberg-hiking-trail-04.jpg",
        "assets/robberg-hiking-trail/robberg-hiking-trail-05.jpg",
        "assets/robberg-hiking-trail/robberg-hiking-trail-06.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Robberg Hiking Trail photo: {photo}"


def test_monkeyland_activity_has_photos_and_monkey_kind():
    data = load_data()
    activity = next((item for item in data.get("activities", []) if item["name"] == "Monkeyland"), None)

    assert activity is not None
    assert activity["location"] == "The Crags / Plettenberg Bay"
    assert activity["link"] == "https://maps.app.goo.gl/TGhWGNkZ5JqciSJG8"
    assert activity["region"] == "Garden Route"
    assert activity["kind"] == "monkey"
    assert -34.5 <= activity["lat"] <= -33.5
    assert 23 <= activity["lon"] <= 24
    assert activity["images"] == [
        "assets/monkeyland/monkeyland-01.jpg",
        "assets/monkeyland/monkeyland-02.jpg",
        "assets/monkeyland/monkeyland-03.jpg",
        "assets/monkeyland/monkeyland-04.jpg",
    ]
    for photo in activity["images"]:
        assert Path(photo).exists(), f"Missing Monkeyland photo: {photo}"


def test_all_photo_stops_are_grouped_by_region():
    data = load_data()
    regions = {stop.get("region") for stop in data["photo_stops"]}

    assert None not in regions
    assert "Kapstadt" in regions
    assert "Marloth Park / Kruger" in regions


def test_jeffreys_bay_photo_stop_has_photo_and_region():
    data = load_data()
    stop = next((item for item in data["photo_stops"] if item["name"] == "Jeffreys Bay"), None)

    assert stop is not None
    assert stop["location"] == "Jeffreys Bay / Eastern Cape"
    assert stop["region"] == "Garden Route"
    assert stop["kind"] == "photo"
    assert -35 <= stop["lat"] <= -33
    assert 24 <= stop["lon"] <= 25
    assert stop["photos"] == ["assets/jeffreys-bay/jeffreys-bay-01.jpg"]
    for photo in stop["photos"]:
        assert Path(photo).exists(), f"Missing Jeffreys Bay photo: {photo}"


def test_alexandria_dune_field_running_photo_stop_has_photos_and_running_kind():
    data = load_data()
    stop = next((item for item in data["photo_stops"] if item["name"] == "Alexandria Dune Field Running"), None)

    assert stop is not None
    assert stop["location"] == "Alexandria Dune Field / Eastern Cape"
    assert stop["region"] == "Eastern Cape / Addo"
    assert stop["kind"] == "running"
    assert -34 <= stop["lat"] <= -33
    assert 26 <= stop["lon"] <= 27
    assert stop["photos"] == [
        "assets/alexandria-dune-field-running/alexandria-dune-field-running-01.jpg",
        "assets/alexandria-dune-field-running/alexandria-dune-field-running-02.jpg",
    ]
    for photo in stop["photos"]:
        assert Path(photo).exists(), f"Missing Alexandria Dune Field Running photo: {photo}"


def test_kidds_beach_is_beach_photo_stop_not_top_activity():
    data = load_data()
    name = "Kidds Beach"
    activity_names = [item["name"] for item in data.get("activities", [])]
    stop = next((item for item in data.get("photo_stops", []) if item["name"] == name), None)

    assert name not in activity_names
    assert stop is not None
    assert stop["location"] == "Kidds Beach / Eastern Cape"
    assert stop["summary"] == "Gemütlicher Zwischenstopp am Meer."
    assert stop["kind"] == "beach"
    assert stop["link"] == "https://maps.app.goo.gl/PnvH84JAtTFiqNQT6?g_st=ac"
    assert stop["photos"] == ["assets/kidds-beach-stop/kidds-beach-stop-01.jpg"]
    for photo in stop["photos"]:
        assert Path(photo).exists(), f"Missing Kidds Beach photo: {photo}"


def test_accommodation_photo_stops_use_stay_kind_for_map_symbol():
    data = load_data()
    marloth = next(stop for stop in data["photo_stops"] if stop["name"] == "Marloth Park")
    moontide = next(stay for stay in data["stays"] if stay["name"] == "Moontide Riverside Lodge")

    assert marloth["kind"] == "stay"
    assert moontide["kind"] == "stay"
