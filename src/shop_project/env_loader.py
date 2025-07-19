import os
from typing import TypeVar, Callable, Optional
from dotenv import load_dotenv

T = TypeVar("T")

class MissingEnvFileError(Exception):
    """Исключение для случая, если ENV_FILE не задан или файл не найден."""
    def __init__(self, path: Optional[str]):
        msg = f"ENV_FILE is not set" if path is None else f"ENV_FILE not found: {path}"
        super().__init__(msg)

class MissingEnvError(Exception):
    """Исключение для отсутствующих переменных окружения."""
    def __init__(self, var_name: str):
        super().__init__(f"Missing required environment variable: {var_name}")

def get_env(
    name: str,
    default: Optional[str] = None,
) -> str:
    """
    Загружает переменную окружения с возможностью кастинга и значением по умолчанию.

    :param name: Имя переменной окружения.
    :param default: Значение по умолчанию (если переменная отсутствует).
    :return: Строковое значение переменной окружения.
    """
    value = os.getenv(name)

    if value is None:
        if default is not None: 
            return default
        else:
            raise MissingEnvError(name)
    
    return value

# --- Автоматическая загрузка .env при импорте модуля ---

env_file_path = os.getenv("ENV_FILE")
if not env_file_path or not os.path.isfile(env_file_path):
    raise MissingEnvFileError(env_file_path)

load_dotenv(env_file_path)
