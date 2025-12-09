from typing import Type

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject, SubjectEnum


def get_subject_enum(subject: Subject) -> SubjectEnum:
    return SubjectEnum(subject.__class__.__name__.upper())


def get_subject(subject_enum: SubjectEnum) -> Type[Subject]:
    if subject_enum == SubjectEnum.CUSTOMER:
        return Customer
    if subject_enum == SubjectEnum.EMPLOYEE:
        return Employee
    if subject_enum == SubjectEnum.MANAGER:
        return Manager
