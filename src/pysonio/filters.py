from datetime import date
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
    value: date
    operator: Operator = Operator.EQUALS


@final
class RangeFilterOperator(Enum):
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()


@final
class DateRangeFilter(NamedTuple):
    value: datetime
    operator: RangeFilterOperator
