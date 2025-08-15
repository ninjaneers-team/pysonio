import random
from typing import Final

from pysonio import PersonData
from pysonio import Pysonio


def test_get_org_units(client: Pysonio, persons: list[PersonData]) -> None:
    person: Final = random.choice(persons)
    employments: Final = client.get_employments(person_id=person.id)
    assert len(employments) == 1
    employment: Final = employments[0]
    assert employment.org_units is not None
    org_units: Final = {
        org_unit.type: client.get_org_unit(
            org_unit_id=org_unit.id,
            org_unit_type=org_unit.type,
        )
        for org_unit in employment.org_units
    }
    assert "department" in org_units
