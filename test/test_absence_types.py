from typing import Final

from pysonio import Client


def test_list_absence_types(client: Client) -> None:
    absence_types: Final = client.get_absence_types()
    assert absence_types  # No empty list.
