from typing import Final

import pytest

from pysonio import AbsencePeriodData
from pysonio import PersonData
from pysonio import Pysonio


@pytest.fixture
def absence_periods(client: Pysonio) -> list[AbsencePeriodData]:
    result = client.get_absence_periods()
    assert result  # We cannot work with an empty list.
    return result


def test_get_absence_periods(client: Pysonio) -> None:
    _ = client.get_absence_periods()


def test_get_absence_periods_by_person_id(client: Pysonio, persons: list[PersonData]) -> None:
    person: Final = persons[-1]
    absence_periods: Final = client.get_absence_periods(person_id=person.id)
    assert len(absence_periods) > 0
    assert all(period.person.id == person.id for period in absence_periods)


def test_get_absence_periods_streamed(client: Pysonio, absence_periods: list[AbsencePeriodData]) -> None:
    pagination_size: Final = min(100, len(absence_periods) // 4)
    current_offset = 0
    for page in client.get_absence_periods(limit=pagination_size, streamed=True):
        expected_page_size = min(pagination_size, len(absence_periods) - current_offset)
        assert len(page) == expected_page_size
        for i, absence_period in enumerate(page):
            assert absence_period == absence_periods[current_offset + i]
        current_offset += expected_page_size
    assert current_offset == len(absence_periods)
