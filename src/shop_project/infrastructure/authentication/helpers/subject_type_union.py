from typing import TypeAlias

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager

SubjectTypeUnion: TypeAlias = Customer | Employee | Manager
