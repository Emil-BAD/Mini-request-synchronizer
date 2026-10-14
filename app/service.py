import math
from datetime import UTC, datetime

from app.normalizer import normalize_phone


def _safe_amount(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            number = float(raw.replace(",", "."))
        except ValueError:
            return None
    else:
        return None

    if not math.isfinite(number):
        return None
    return number


def _safe_datetime(value: object) -> datetime | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _safe_id(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(text)
        except ValueError:
            return None
    return None


def _candidate_priority(record: dict, source_index: int):
    amount = _safe_amount(record.get("amount"))
    created_at = _safe_datetime(record.get("created_at"))
    record_id = _safe_id(record.get("id"))

    amount_score = amount if amount is not None else float("-inf")
    date_score = created_at if created_at is not None else datetime.min.replace(tzinfo=UTC)
    id_score = record_id if record_id is not None else -1
    return (amount_score, date_score, id_score, source_index)


def _output_amount(value: float | None) -> int | float:
    if value is None:
        return 0
    number = float(value)
    if not math.isfinite(number):
        return 0
    if number.is_integer():
        return int(number)
    return number


def process_orders(raw_orders: list[dict] | None) -> dict:
    raw_list = raw_orders if isinstance(raw_orders, list) else []
    received = len(raw_list)
    invalid_dropped = 0
    valid_by_phone: dict[str, list[tuple[int, dict]]] = {}

    for index, raw in enumerate(raw_list):
        if not isinstance(raw, dict):
            invalid_dropped += 1
            continue

        phone = normalize_phone(raw.get("phone"))
        if phone is None:
            invalid_dropped += 1
            continue

        valid_by_phone.setdefault(phone, []).append((index, raw))

    clients: list[dict] = []
    for phone, candidates in valid_by_phone.items():
        winner = None
        winner_priority = None
        for source_index, record in candidates:
            priority = _candidate_priority(record, source_index)
            if winner is None or priority > winner_priority:
                winner = record
                winner_priority = priority

        if winner is None:
            continue

        amount = _safe_amount(winner.get("amount"))
        clients.append(
            {
                "name": str(winner.get("name") or ""),
                "phone": phone,
                "email": str(winner.get("email") or ""),
                "amount": _output_amount(amount),
            }
        )

    clients.sort(key=lambda item: item["phone"])
    unique = len(clients)
    duplicates_merged = max(received - invalid_dropped - unique, 0)

    result = {
        "clients": clients,
        "stats": {
            "received": received,
            "unique": unique,
            "duplicates_merged": duplicates_merged,
            "invalid_dropped": invalid_dropped,
        },
    }

    if result["stats"]["received"] != received:
        raise ValueError("Internal invariant failed: received should equal original batch length")
    if result["stats"]["unique"] != len(result["clients"]):
        raise ValueError("Internal invariant failed: unique should equal client count")

    return result
