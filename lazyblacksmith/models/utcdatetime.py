import pytz

from sqlalchemy.types import DateTime
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """
    Thanks MySQL not to be able to manage timezone times...
    So we extend DateTime to always store as UTC and
    """
    impl = DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(pytz.utc).replace(tzinfo=None)

    def process_result_value(self, value, engine):
        if value is not None:
            return value.replace(tzinfo=pytz.utc)
