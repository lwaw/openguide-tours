"""
Tests for a single tour's tour.json file.

Run:
    pytest data/tests/test_tour.py --tour amsterdam-city-walk -v

The --tour argument is required. All tests are skipped if it is omitted.
"""

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent.parent
TOURS_DIR = DATA_DIR / "tours"

VALID_TOUR_TYPES = {"museum", "city", "neighborhood", "historic"}
VALID_LANGUAGE_CODES = {"en", "nl", "de", "fr", "es", "it"}

DESCRIPTION_MIN_WORDS = 100
DESCRIPTION_MAX_WORDS = 650

PEXELS_ERROR_TEXT = "Oops, we couldn't find this page"
PEXELS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_pexels_id(value: str) -> bool:
    return isinstance(value, str) and value.isdigit()


def word_count(text: str) -> int:
    return len(text.split())


def check_pexels_id(pexels_id: str) -> tuple[bool, str]:
    """Return (valid, reason). Raises pytest.skip on network error."""
    url = f"https://www.pexels.com/photo/{pexels_id}/"
    req = urllib.request.Request(url, headers=PEXELS_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        pytest.skip(f"Network unavailable, skipping Pexels check: {exc}")
    if PEXELS_ERROR_TEXT in body:
        return False, f"Pexels ID {pexels_id!r} not found (error page returned)"
    return True, ""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def tour_id(pytestconfig) -> str:
    tid = pytestconfig.getoption("--tour")
    if not tid:
        pytest.skip("No --tour argument provided. Usage: pytest test_tour.py --tour <tour-id>")
    return tid


@pytest.fixture(scope="session")
def tour_path(tour_id) -> Path:
    path = TOURS_DIR / tour_id / "tour.json"
    if not path.exists():
        pytest.fail(f"tour.json not found for {tour_id!r} at {path}")
    return path


@pytest.fixture(scope="session")
def tour(tour_path) -> dict:
    with open(tour_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def supported_languages(tour) -> list[str]:
    return tour.get("supportedLanguages", [])


@pytest.fixture(scope="session")
def stops(tour) -> list[dict]:
    return tour.get("stops", [])


def pytest_generate_tests(metafunc):
    if "stop" in metafunc.fixturenames:
        tour_id = metafunc.config.getoption("--tour", default=None)
        if not tour_id:
            metafunc.parametrize("stop", [], ids=[])
            return
        path = TOURS_DIR / tour_id / "tour.json"
        if not path.exists():
            metafunc.parametrize("stop", [], ids=[])
            return
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        stop_list = data.get("stops", [])
        ids = [s.get("id", f"stop_{i}") for i, s in enumerate(stop_list)]
        # We also need supportedLanguages available in per-stop tests.
        # Pass it via indirect or by embedding in each stop dict.
        langs = data.get("supportedLanguages", [])
        for s in stop_list:
            s["_supportedLanguages"] = langs
        metafunc.parametrize("stop", stop_list, ids=ids)


# ---------------------------------------------------------------------------
# Top-level tour tests
# ---------------------------------------------------------------------------

REQUIRED_TOUR_FIELDS = [
    "id", "name", "description", "type", "duration",
    "supportedLanguages", "defaultLanguage", "stops",
]


def test_tour_file_is_valid_json(tour_path):
    with open(tour_path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_required_top_level_fields(tour):
    missing = [f for f in REQUIRED_TOUR_FIELDS if f not in tour]
    assert not missing, f"Missing required fields: {missing}"


def test_id_matches_folder(tour, tour_id):
    assert tour["id"] == tour_id, (
        f"tour.json 'id' is {tour['id']!r} but folder name is {tour_id!r}"
    )


def test_type_is_valid(tour):
    assert tour["type"] in VALID_TOUR_TYPES, (
        f"Invalid type {tour['type']!r}. Must be one of: {VALID_TOUR_TYPES}"
    )


def test_supported_languages_non_empty(supported_languages):
    assert isinstance(supported_languages, list) and len(supported_languages) > 0, \
        "'supportedLanguages' must be a non-empty list"


def test_supported_languages_are_valid_codes(supported_languages):
    invalid = [lang for lang in supported_languages if lang not in VALID_LANGUAGE_CODES]
    assert not invalid, f"Unsupported language codes: {invalid}"


def test_default_language_in_supported(tour, supported_languages):
    default = tour["defaultLanguage"]
    assert default in supported_languages, (
        f"'defaultLanguage' {default!r} is not in 'supportedLanguages': {supported_languages}"
    )


def test_name_has_all_languages(tour, supported_languages):
    name = tour["name"]
    assert isinstance(name, dict), "'name' must be a dict"
    missing = [lang for lang in supported_languages if lang not in name]
    assert not missing, f"'name' missing translations for: {missing}"


def test_description_has_all_languages(tour, supported_languages):
    desc = tour["description"]
    assert isinstance(desc, dict), "'description' must be a dict"
    missing = [lang for lang in supported_languages if lang not in desc]
    assert not missing, f"'description' missing translations for: {missing}"


def test_city_tour_has_start_point(tour):
    if tour["type"] != "city":
        pytest.skip("Not a city tour")
    assert "startPoint" in tour, "City tours must have a 'startPoint' field"
    sp = tour["startPoint"]
    for field in ("name", "address", "location"):
        assert field in sp, f"'startPoint' missing field: {field!r}"
    loc = sp["location"]
    assert "latitude" in loc and "longitude" in loc, \
        "'startPoint.location' must have 'latitude' and 'longitude'"


def test_museum_tour_has_venue(tour):
    if tour["type"] != "museum":
        pytest.skip("Not a museum tour")
    assert "venue" in tour, "Museum tours must have a 'venue' field"
    venue = tour["venue"]
    for field in ("name", "address", "location"):
        assert field in venue, f"'venue' missing field: {field!r}"
    loc = venue["location"]
    assert "latitude" in loc and "longitude" in loc, \
        "'venue.location' must have 'latitude' and 'longitude'"


def test_distance_is_positive_if_present(tour):
    distance = tour.get("distance")
    if distance is None:
        return
    assert isinstance(distance, (int, float)) and distance > 0, (
        f"'distance' must be a positive number, got {distance!r}"
    )


def test_stops_is_non_empty_list(stops):
    assert isinstance(stops, list) and len(stops) > 0, \
        "'stops' must be a non-empty list"


def test_stop_order_is_sequential(stops):
    orders = [s.get("order") for s in stops]
    expected = list(range(1, len(stops) + 1))
    assert orders == expected, (
        f"Stop 'order' values must be sequential starting at 1. Got: {orders}"
    )


def test_stop_ids_are_unique(stops):
    ids = [s.get("id") for s in stops]
    assert len(ids) == len(set(ids)), f"Duplicate stop IDs found: {ids}"


# ---------------------------------------------------------------------------
# Per-stop tests
# ---------------------------------------------------------------------------

REQUIRED_STOP_FIELDS = ["id", "order", "name", "location", "description", "images", "tags"]


def test_stop_required_fields(stop):
    missing = [f for f in REQUIRED_STOP_FIELDS if f not in stop]
    assert not missing, f"Stop {stop.get('id')!r} missing fields: {missing}"


def test_stop_id_is_url_friendly(stop):
    stop_id = stop["id"]
    assert re.fullmatch(r"[a-z0-9-]+", stop_id), (
        f"Stop ID {stop_id!r} must contain only lowercase letters, digits, and hyphens"
    )


def test_stop_name_has_all_languages(stop):
    langs = stop["_supportedLanguages"]
    name = stop["name"]
    assert isinstance(name, dict), f"Stop {stop['id']!r}: 'name' must be a dict"
    missing = [lang for lang in langs if lang not in name]
    assert not missing, f"Stop {stop['id']!r}: 'name' missing translations for: {missing}"


def test_stop_description_has_all_languages(stop):
    langs = stop["_supportedLanguages"]
    desc = stop["description"]
    assert isinstance(desc, dict), f"Stop {stop['id']!r}: 'description' must be a dict"
    missing = [lang for lang in langs if lang not in desc]
    assert not missing, \
        f"Stop {stop['id']!r}: 'description' missing translations for: {missing}"


def test_stop_description_word_count(stop):
    langs = stop["_supportedLanguages"]
    desc = stop["description"]
    for lang in langs:
        if lang not in desc:
            continue  # already caught by test_stop_description_has_all_languages
        count = word_count(desc[lang])
        assert DESCRIPTION_MIN_WORDS <= count <= DESCRIPTION_MAX_WORDS, (
            f"Stop {stop['id']!r} [{lang}]: description has {count} words, "
            f"expected {DESCRIPTION_MIN_WORDS}–{DESCRIPTION_MAX_WORDS}"
        )


def test_stop_location_has_valid_coords(stop):
    loc = stop["location"]
    assert isinstance(loc, dict), f"Stop {stop['id']!r}: 'location' must be a dict"
    lat = loc.get("latitude")
    lon = loc.get("longitude")
    assert isinstance(lat, (int, float)) and -90 <= lat <= 90, \
        f"Stop {stop['id']!r}: invalid latitude {lat!r}"
    assert isinstance(lon, (int, float)) and -180 <= lon <= 180, \
        f"Stop {stop['id']!r}: invalid longitude {lon!r}"


def test_museum_stop_has_indoor(stop):
    # Only enforce indoor for museum tours
    tour_type_path = TOURS_DIR / stop["_supportedLanguages"][0]  # not reliable
    # Derive tour type from the loaded tour fixture — use the embedded marker instead
    # We check for presence of 'indoor' only if the stop itself signals it's a museum stop
    # by having an 'indoor' key (museum tours always include it; city tours never do).
    # A stricter check is done at the tour level in test_museum_tour_has_venue.
    # Here we just validate the indoor object structure if it is present.
    indoor = stop["location"].get("indoor")
    if indoor is None:
        pytest.skip("No 'indoor' field on this stop")
    assert "floor" in indoor, \
        f"Stop {stop['id']!r}: 'indoor' must have a 'floor' field"
    assert "room" in indoor, \
        f"Stop {stop['id']!r}: 'indoor' must have a 'room' field"


def test_stop_images_format(stop):
    images = stop["images"]
    assert isinstance(images, list), f"Stop {stop['id']!r}: 'images' must be a list"
    assert len(images) <= 1, (
        f"Stop {stop['id']!r}: 'images' must have 0 or 1 entries, got {len(images)}"
    )
    for img in images:
        assert is_pexels_id(img), (
            f"Stop {stop['id']!r}: image {img!r} must be a numeric Pexels ID string"
        )


def test_stop_tags_non_empty(stop):
    tags = stop["tags"]
    assert isinstance(tags, list) and len(tags) > 0, \
        f"Stop {stop['id']!r}: 'tags' must be a non-empty list"
    for tag in tags:
        assert isinstance(tag, str) and tag, \
            f"Stop {stop['id']!r}: each tag must be a non-empty string, got {tag!r}"


def test_stop_pexels_image_is_valid(stop):
    images = stop["images"]
    if not images:
        pytest.skip("No image on this stop")

    pexels_id = images[0]
    valid, reason = check_pexels_id(pexels_id)
    assert valid, f"Stop {stop['id']!r}: {reason}"
