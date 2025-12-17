import importlib
import pkgutil
from pathlib import Path


def init_background_service_registry():
    # Относительный путь к папке implementations относительно текущего пакета
    # Если запускаем как "python -m src.my_script", __package__ = "src"
    package_name = f"{__package__}.implementations"  # относительное имя пакета
    implementations_path = Path(__file__).parent / "implementations"

    for finder, name, is_pkg in pkgutil.iter_modules([str(implementations_path)]):
        importlib.import_module(f"{package_name}.{name}")
