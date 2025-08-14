import random
from typing import Final

from pysonio import PersonData
from pysonio import Pysonio


def test_get_employment(client: Pysonio, persons: list[PersonData]) -> None:
    employee: Final = random.choice(persons)
    assert employee.employments  # There must be at least one employment.
    employment: Final = client.get_employment(
        person_id=employee.id,
        employment_id=employee.employments[0].id,
    )
    assert employment.id == employee.employments[0].id
    assert employment.person.id == employee.id


def test_get_employments(client: Pysonio, persons: list[PersonData]) -> None:
    employee: Final = random.choice(persons)
    employments: Final = client.get_employments(
        person_id=employee.id,
    )
    assert len(employments) == len(employee.employments)
    for employment in employments:
        assert employment.person.id == employee.id
        assert employment.id in [e.id for e in employee.employments]
