from datetime import datetime
from enum import Enum
from enum import auto
from typing import NamedTuple
from typing import final


@final
class Operator(Enum):
    EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()


@final
class DateFilter(NamedTuple):
    value: datetime
    operator: Operator = Operator.EQUALS
