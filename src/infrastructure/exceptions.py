class InfrastructureException(Exception):
    pass


class UnitOfWorkException(InfrastructureException):
    pass

class QueryPlanException(InfrastructureException):
    pass