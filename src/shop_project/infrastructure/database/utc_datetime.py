import datetime

from sqlalchemy.types import DateTime, TypeDecorator


class UTCDateTime(TypeDecorator[datetime.datetime]):
    impl = DateTime
    cache_ok = True

    # при сохранении в БД
    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        # делаем datetime aware, если был naive
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.timezone.utc)

        # приводим к UTC
        value = value.astimezone(datetime.timezone.utc)

        # возвращаем naive — БД получит UTC без tzinfo
        return value.replace(tzinfo=None)

    # при загрузке из БД
    def process_result_value(self, value, dialect):
        if value is None:
            return None

        # добавляем tzinfo=UTC при чтении
        return value.replace(tzinfo=datetime.timezone.utc)
