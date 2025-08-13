from typing import Final

import pytest

from pysonio import AbsenceTypesData
from pysonio import Client


@pytest.fixture
def absence_types(client: Client) -> list[AbsenceTypesData]:
    """
    Fixture to retrieve a list of all absence types from the Personio API.
    :param client: Client instance to interact with the Personio API.
    :return: list[AbsenceTypesData] - A list of absence types.
    """
    # This code is extracted into a fixture for tests that need absence types, but
    # actually test something else. This way it's easier to see why a test fails.
    return client.get_absence_types()


def test_list_absence_types(client: Client) -> None:
    absence_types: Final = client.get_absence_types()
    assert absence_types  # No empty list.


def test_get_absence_type(client: Client, absence_types: list[AbsenceTypesData]) -> None:
    for absence_type in absence_types:
        absence_type_data: AbsenceTypesData = client.get_absence_type(absence_type.id)
        assert absence_type_data == absence_type


def test_get_absence_types_streamed(client: Client, absence_types: list[AbsenceTypesData]) -> None:
    pagination_size: Final = 2
    assert len(absence_types) > pagination_size  # We need more than one page to test streaming.
    current_offset = 0
    for page in client.get_absence_types(limit=pagination_size, streamed=True):
        expected_page_size = min(pagination_size, len(absence_types) - current_offset)
        assert len(page) == expected_page_size
        for i, absence_type in enumerate(page):
            assert absence_type == absence_types[current_offset + i]
        current_offset += expected_page_size
    assert current_offset == len(absence_types)  # We should have processed all absence types
