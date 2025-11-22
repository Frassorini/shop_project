import base64
from typing import Union

BytesLike = Union[bytes, bytearray]


def bytes_to_str(data: BytesLike) -> str:
    """
    Кодирует байты в URL-safe Base64 строку без паддинга.
    Строка безопасна для JSON, URL, SQL, QR-кодов.
    """
    encoded = base64.urlsafe_b64encode(data).rstrip(b"=")
    return encoded.decode("ascii")


def str_to_bytes(data: str) -> bytes:
    """
    Декодирует URL-safe Base64 строку обратно в байты.
    Padding добавляется автоматически при декодировании.
    """
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)
