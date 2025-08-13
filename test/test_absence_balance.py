from pysonio import Client
from pysonio import PersonData


def test_get_absence_balance(client: Client, persons: list[PersonData]) -> None:
    _ = client.get_absence_balance(person_id=persons[0].id)
