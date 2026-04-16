"""
Tests for data/tours.json — the tour index file.

Run:
    pytest data/tests/test_tours_index.py -v
"""

import json
import urllib.error
import urllib.request
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent.parent
TOURS_JSON = DATA_DIR / "tours.json"
TOURS_DIR = DATA_DIR / "tours"

VALID_TOUR_TYPES = {"museum", "city", "neighborhood", "historic"}

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

def load_index() -> dict:
    with open(TOURS_JSON, encoding="utf-8") as f:
        return json.load(f)


def load_tour(tour_id: str) -> dict:
    path = TOURS_DIR / tour_id / "tour.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_pexels_id(value: str) -> bool:
    return value.isdigit()


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

@pytest.fixture(scope="module")
def index() -> dict:
    return load_index()


@pytest.fixture(scope="module")
def tours(index) -> list[dict]:
    return index["tours"]


def pytest_generate_tests(metafunc):
    if "tour_summary" in metafunc.fixturenames:
        try:
            data = load_index()
            summaries = data.get("tours", [])
        except Exception:
            summaries = []
        ids = [t.get("id", f"tour_{i}") for i, t in enumerate(summaries)]
        metafunc.parametrize("tour_summary", summaries, ids=ids)


# ---------------------------------------------------------------------------
# Index-level tests
# ---------------------------------------------------------------------------

def test_index_file_exists():
    assert TOURS_JSON.exists(), f"tours.json not found at {TOURS_JSON}"


def test_index_is_valid_json():
    with open(TOURS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_index_has_tours_key(index):
    assert "tours" in index, "tours.json must have a top-level 'tours' key"


def test_tours_is_non_empty_list(tours):
    assert isinstance(tours, list), "'tours' must be a list"
    assert len(tours) > 0, "'tours' list must not be empty"


def test_tour_ids_are_unique(tours):
    ids = [t.get("id") for t in tours]
    assert len(ids) == len(set(ids)), f"Duplicate tour IDs found: {ids}"


# ---------------------------------------------------------------------------
# Per-tour-summary tests
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "id", "name", "type", "city", "country",
    "thumbnail", "duration", "stopCount", "startLocation",
]


def test_required_fields_present(tour_summary):
    missing = [f for f in REQUIRED_FIELDS if f not in tour_summary]
    assert not missing, f"Tour {tour_summary.get('id')!r} missing fields: {missing}"


def test_id_is_non_empty_string(tour_summary):
    assert isinstance(tour_summary["id"], str) and tour_summary["id"], \
        "id must be a non-empty string"


def test_type_is_valid(tour_summary):
    assert tour_summary["type"] in VALID_TOUR_TYPES, (
        f"Tour {tour_summary['id']!r} has invalid type {tour_summary['type']!r}. "
        f"Must be one of: {VALID_TOUR_TYPES}"
    )


def test_name_is_dict_with_entries(tour_summary):
    name = tour_summary["name"]
    assert isinstance(name, dict) and len(name) > 0, \
        f"Tour {tour_summary['id']!r}: 'name' must be a non-empty dict"


def test_duration_is_positive_int(tour_summary):
    duration = tour_summary["duration"]
    assert isinstance(duration, int) and duration > 0, \
        f"Tour {tour_summary['id']!r}: 'duration' must be a positive integer, got {duration!r}"


def test_stop_count_is_positive_int(tour_summary):
    stop_count = tour_summary["stopCount"]
    assert isinstance(stop_count, int) and stop_count > 0, \
        f"Tour {tour_summary['id']!r}: 'stopCount' must be a positive integer, got {stop_count!r}"


def test_stop_count_matches_tour_json(tour_summary):
    tour_id = tour_summary["id"]
    tour_path = TOURS_DIR / tour_id / "tour.json"
    assert tour_path.exists(), f"No tour.json found for {tour_id!r} at {tour_path}"

    tour = load_tour(tour_id)
    actual = len(tour.get("stops", []))
    declared = tour_summary["stopCount"]
    assert actual == declared, (
        f"Tour {tour_id!r}: stopCount is {declared} but tour.json has {actual} stops"
    )


def test_start_location_has_valid_coords(tour_summary):
    loc = tour_summary["startLocation"]
    assert isinstance(loc, dict), \
        f"Tour {tour_summary['id']!r}: 'startLocation' must be a dict"
    lat = loc.get("latitude")
    lon = loc.get("longitude")
    assert isinstance(lat, (int, float)) and -90 <= lat <= 90, \
        f"Tour {tour_summary['id']!r}: invalid latitude {lat!r}"
    assert isinstance(lon, (int, float)) and -180 <= lon <= 180, \
        f"Tour {tour_summary['id']!r}: invalid longitude {lon!r}"


def test_thumbnail_is_non_empty_string(tour_summary):
    thumb = tour_summary["thumbnail"]
    assert isinstance(thumb, str) and thumb, \
        f"Tour {tour_summary['id']!r}: 'thumbnail' must be a non-empty string"


def test_image_is_pexels_id_if_present(tour_summary):
    image = tour_summary.get("image")
    if image is None:
        return
    assert isinstance(image, str) and is_pexels_id(image), (
        f"Tour {tour_summary['id']!r}: 'image' must be a numeric Pexels ID string, got {image!r}"
    )


def test_tour_folder_and_json_exist(tour_summary):
    tour_id = tour_summary["id"]
    folder = TOURS_DIR / tour_id
    assert folder.is_dir(), f"No folder found for tour {tour_id!r} at {folder}"
    tour_json = folder / "tour.json"
    assert tour_json.exists(), f"No tour.json found for tour {tour_id!r} at {tour_json}"


def test_pexels_image_is_valid(tour_summary):
    image = tour_summary.get("image")
    if image is None or not is_pexels_id(image):
        pytest.skip("No Pexels image ID on this tour")

    valid, reason = check_pexels_id(image)
    assert valid, f"Tour {tour_summary['id']!r}: {reason}"
