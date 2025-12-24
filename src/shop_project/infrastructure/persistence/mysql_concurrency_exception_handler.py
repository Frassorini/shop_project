from contextlib import asynccontextmanager

from sqlalchemy.exc import OperationalError

from shop_project.application.interfaces.interface_unit_of_work import (
    DeadlockDetectedException,
    LockTimeoutException,
    NoWaitException,
)

MYSQL_LOCK_ERRORS = {
    3572: NoWaitException,
    1205: LockTimeoutException,
    1213: DeadlockDetectedException,
}


@asynccontextmanager
async def translate_mysql_concurrency_errors():
    try:
        yield
    except OperationalError as e:
        orig = e.orig

        if not orig:
            raise

        if hasattr(orig, "args") and orig.args:
            mysql_code = orig.args[0]
            exc_type = MYSQL_LOCK_ERRORS.get(mysql_code)

            if exc_type is not None:
                raise exc_type() from e

        raise
