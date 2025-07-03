import pytest
import logging
from ufc_downloader.importer import prune_edition_from_movie_title, verify_match


# Configure logging for tests to capture warnings
@pytest.fixture(autouse=True)
def caplog_fixture(caplog):
    """Fixture to capture and assert log messages."""
    caplog.set_level(logging.WARNING)
    return caplog


@pytest.mark.parametrize(
    "movie_title, event_name, expected_result",
    [
        ##############################################################
        # Test cases where numbers match or event_name has no numbers
        ##############################################################
        ("UFC.on.ESPN.69", "UFC on ESPN 69", True),
        ("UFC.299", "UFC 299 OMalley vs Vera 2", False),
        # movie_numbers is empty
        ("UFC.Fight.Night", "UFC Fight Night 234", False),
        # movie_numbers={299, 2}, event_numbers={299, 2}
        ("UFC.299.Part.2", "UFC 299 OMalley vs Vera 2", True),
        # movie title includes a date
        ("UFC.317.Topuria.Vs.Oliveira.2025-06-28", "UFC 317 Topuria vs Oliveira", True),
        # Both have no numbers. Not ideal since this would be unexpected but we should
        # allow it unless it becomes a problem.
        ("UFC.No.Numbers", "Event.No.Numbers", True),
        ("UFC.100", "UFC 100", True),
        ("UFC.1", "UFC 1", True),
        # event_numbers is a subset
        ("UFC.1.2.3.4", "UFC 1 2 3", True),
        ##############################################################
        # Test cases where numbers do not match, expecting a warning and False
        ##############################################################
        # Mismatch in numbers
        ("UFC.on.ESPN.69", "UFC on ESPN 68", False),
        # movie_numbers={299, 1}, event_numbers={299, 2}
        ("UFC.299.Part.1", "UFC 299 OMalley vs Vera 2", False),
        # In this case we should probably fail to import but we'll let it ride since
        # this verification only should care about events with numbers
        ("UFC.299", "UFC.Fight.Night", True),
        # Different parts, same main number, but different part numbers
        ("UFC.100.Part.1", "UFC 100 Part 2", False),
        # event_numbers is not a subset
        ("UFC.1.2.3", "UFC 1 2 3 4", False),
    ],
)
def test_verify_match(movie_title, event_name, expected_result, caplog_fixture):
    """
    Tests the verify_match function with various movie_title and event_name combinations.
    """
    source_path = f"/path/to/download/{movie_title}"  # Dummy source_path for logging
    result = verify_match(movie_title, event_name, source_path)
    assert (
        result == expected_result
    ), f"Expected {expected_result} but got {result} for movie_title='{movie_title}' and event_name='{event_name}'"

    if not expected_result:
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


@pytest.mark.parametrize(
    "movie_title, expected_result",
    [
        ("UFC Fight Night 234 Prelims", "UFC Fight Night 234"),
        ("UFC Fight Night 234", "UFC Fight Night 234"),
        ("UFC Fight Night 234 Early Prelims", "UFC Fight Night 234"),
    ],
)
def test_prune_edition_from_movie_title(movie_title, expected_result):
    result = prune_edition_from_movie_title(movie_title)
    assert result == expected_result, f"Expected {expected_result} but got {result}"
