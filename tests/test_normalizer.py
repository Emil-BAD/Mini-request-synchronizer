from app.normalizer import normalize_phone


def test_normalize_phone_examples():
    cases = {
        "+7 (999) 123-45-67": "+79991234567",
        "8 (999) 123-45-67": "+79991234567",
        "89991234567": "+79991234567",
        "79991234567": "+79991234567",
        "9991234567": "+79991234567",
        "+7-999-123-45-67": "+79991234567",
        "12345": None,
        "abc": None,
        None: None,
    }
    for raw, expected in cases.items():
        assert normalize_phone(raw) == expected


def test_normalize_phone_edge_cases():
    invalid = [
        "",
        "   ",
        "abc123",
        "++7 999 123 45 67",
        "799912345678",
        "123",
        -123,
        -1,
        "8 999 123 45 67 99",
        "8 999 123 45",
        "999999999999999",
        "not a number",
        "8",
        "+1 999 123 45 67",
    ]
    for value in invalid:
        assert normalize_phone(value) is None, value


def test_normalize_phone_valid_russian_prefixes():
    assert normalize_phone("+79219998877") == "+79219998877"
    assert normalize_phone("89219998877") == "+79219998877"
    assert normalize_phone("9219998877") == "+79219998877"
