import random
from collections import defaultdict
from datetime import date
from typing import Final

from pysonio import DateFilter
from pysonio import PersonData
from pysonio import Pysonio
from pysonio.filters import Operator


def test_get_all_persons(client: Pysonio) -> None:
    # This will use pagination due to the default limit of 10.
    persons: Final = client.get_persons()
    assert persons  # No empty list.


def test_get_person_by_first_name(client: Pysonio, persons: list[PersonData]) -> None:
    persons_by_first_name: defaultdict[str, list[PersonData]] = defaultdict(list)
    for person in persons:
        persons_by_first_name[person.first_name].append(person)

    assert persons_by_first_name

    # We only perform the test with one random first name to speed up the tests.
    first_name, person_list = random.choice(list(persons_by_first_name.items()))

    persons_with_this_first_name = client.get_persons(first_name=first_name)
    assert persons_with_this_first_name
    assert len(persons_with_this_first_name) == len(person_list)
    for person in persons_with_this_first_name:
        assert person.first_name == first_name


def test_get_persons_by_updated_at(client: Pysonio, persons: list[PersonData]) -> None:
    new_employees: Final = client.get_persons(
        updated_at_filters=[
            DateFilter(
                value=date(year=2025, month=1, day=1),
                operator=Operator.GREATER_THAN,
            ),
        ]
    )
    expected_employees: Final = [person for person in persons if person.updated_at.year >= 2025]
    for employee in new_employees:
        assert employee in expected_employees


def test_all_person_ids_are_numeric(client: Pysonio, persons: list[PersonData]) -> None:
    # We test this because we use the retrieved employee IDs for querying absence balances.
    # For that we have to use a V1 endpoint that requires numeric IDs. However, the V2
    # endpoint to retrieve persons returns string IDs.
    assert all(person.id.isdigit() for person in persons)


def test_get_persons_streamed(client: Pysonio, persons: list[PersonData]) -> None:
    pagination_size: Final = 20
    current_offset = 0
    for page in client.get_persons(limit=pagination_size, streamed=True):
        expected_page_size = min(pagination_size, len(persons) - current_offset)
        assert len(page) == expected_page_size
        for i, person in enumerate(page):
            assert person == persons[current_offset + i]
        current_offset += expected_page_size
