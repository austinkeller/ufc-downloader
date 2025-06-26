import pytest
import logging
from ufc_downloader.importer import verify_match


# Configure logging for tests to capture warnings
@pytest.fixture(autouse=True)
def caplog_fixture(caplog):
    """Fixture to capture and assert log messages."""
    caplog.set_level(logging.WARNING)
    return caplog


@pytest.mark.parametrize(
    "movie_title, event_name, expected_result, expect_warning",
    [
        # Test cases where numbers match or movie_title has no numbers
        ("UFC.on.ESPN.69", "UFC on ESPN 69", True, False),
        ("UFC.299", "UFC 299 OMalley vs Vera 2", True, False),
        (
            "UFC.Fight.Night",
            "UFC Fight Night 234",
            True,
            False,
        ),  # movie_numbers is empty
        (
            "UFC.299.Part.2",
            "UFC 299 OMalley vs Vera 2",
            True,
            False,
        ),  # movie_numbers={299, 2}, event_numbers={299, 2}
        ("UFC.No.Numbers", "Event.No.Numbers", True, False),  # Both have no numbers
        ("UFC.100", "UFC 100", True, False),
        ("UFC.1", "UFC 1", True, False),
        ("UFC.1.2.3", "UFC 1.2.3.4", True, False),  # movie_numbers is a subset
        # Test cases where numbers do not match, expecting a warning and False
        ("UFC.on.ESPN.69", "UFC on ESPN 68", False, True),  # Mismatch in numbers
        (
            "UFC.299.Part.1",
            "UFC 299 OMalley vs Vera 2",
            False,
            True,
        ),  # movie_numbers={299, 1}, event_numbers={299, 2}
        (
            "UFC.299",
            "UFC.Fight.Night",
            False,
            True,
        ),  # movie_numbers has numbers, event_numbers doesn't
        (
            "UFC.100.Part.1",
            "UFC 100 Part 2",
            False,
            True,
        ),  # Different parts, same main number, but different part numbers
        ("UFC.1.2.3.4", "UFC 1.2.3", False, True),  # movie_numbers is not a subset
    ],
)
def test_verify_match(
    movie_title, event_name, expected_result, expect_warning, caplog_fixture
):
    """
    Tests the verify_match function with various movie_title and event_name combinations.
    """
    source_path = f"/path/to/download/{movie_title}"  # Dummy source_path for logging
    result = verify_match(movie_title, event_name, source_path)
    assert (
        result == expected_result
    ), f"Expected {expected_result} but got {result} for movie_title='{movie_title}' and event_name='{event_name}'"

    if expect_warning:
        assert (
            len(caplog_fixture.records) == 1
        ), f"Expected exactly one warning for '{movie_title}' but found {len(caplog_fixture.records)}."
        assert (
            "Potential mismatch" in caplog_fixture.text
        ), f"Expected a warning for movie_title='{movie_title}' and event_name='{event_name}', but the message was incorrect."
    else:
        assert (
            len(caplog_fixture.records) == 0
        ), f"Unexpected warning for movie_title='{movie_title}' and event_name='{event_name}'"
