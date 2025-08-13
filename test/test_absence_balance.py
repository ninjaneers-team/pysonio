from pysonio import PersonData
from pysonio import Pysonio


def test_get_absence_balance(client: Pysonio, persons: list[PersonData]) -> None:
    _ = client.get_absence_balance(person_id=persons[0].id)
