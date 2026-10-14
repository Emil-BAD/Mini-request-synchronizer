import re


def normalize_phone(phone: object) -> str | None:
    if not isinstance(phone, str):
        return None

    candidate = phone.strip()
    if not candidate:
        return None

    if candidate.count("+") > 1:
        return None

    if "+" in candidate and candidate.index("+") != 0:
        return None

    if any(ch.isalpha() for ch in candidate):
        return None

    cleaned = re.sub(r"[\s\-()\[\]{}./]+", "", candidate)
    if not cleaned:
        return None

    cleaned = cleaned.removeprefix("+")

    if not cleaned.isdigit():
        return None

    if len(cleaned) == 11:
        if cleaned[0] not in {"7", "8"}:
            return None
        number = cleaned[1:]
    elif len(cleaned) == 10:
        number = cleaned
    else:
        return None

    if len(number) != 10:
        return None

    if number[0] not in "3456789":
        return None

    return f"+7{number}"
