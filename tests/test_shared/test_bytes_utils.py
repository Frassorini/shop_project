from shop_project.shared.bytes_utils import bytes_to_str, str_to_bytes


def test_bytes_utils():
    original = b"my secret data \x00\xff"

    s = bytes_to_str(original)
    b = str_to_bytes(s)

    assert original == b
