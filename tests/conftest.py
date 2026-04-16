def pytest_addoption(parser):
    parser.addoption(
        "--tour",
        action="store",
        default=None,
        help="Tour ID to test, e.g. amsterdam-city-walk",
    )
