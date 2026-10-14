from app.service import process_orders


def test_process_orders_merges_duplicates_and_sorts_results():
    data = [
        {"id": 1, "name": "Иван", "phone": "+7 (999) 123-45-67", "email": "ivan@example.com", "amount": 1000, "created_at": "2026-10-01T10:00:00Z"},
        {"id": 2, "name": "Иван 2", "phone": "8 (999) 123 45 67", "email": "ivan2@example.com", "amount": 5000, "created_at": "2026-10-02T11:00:00Z"},
        {"id": 3, "name": "Другой", "phone": "+7 (916) 000 00 01", "email": "other@example.com", "amount": 200, "created_at": "2026-10-03T09:00:00Z"},
        {"id": 4, "name": "Bad", "phone": "123", "email": "bad@example.com", "amount": 999, "created_at": "2026-10-04T00:00:00Z"},
    ]

    result = process_orders(data)

    assert result["stats"]["received"] == 4
    assert result["stats"]["invalid_dropped"] == 1
    assert result["stats"]["unique"] == 2
    assert result["stats"]["duplicates_merged"] == 1
    assert [client["phone"] for client in result["clients"]] == ["+79160000001", "+79991234567"]
    assert result["clients"][0]["amount"] == 200
    assert result["clients"][1]["amount"] == 5000


def test_process_orders_handles_invalid_amount_and_date_without_crashing():
    data = [
        {"id": 1, "name": "A", "phone": "9991234567", "email": "a@example.com", "amount": "not-a-number", "created_at": "bad-date"},
        {"id": 2, "name": "B", "phone": "89991234567", "email": "b@example.com", "amount": 2500, "created_at": "2026-10-12T10:00:00Z"},
    ]

    result = process_orders(data)
    assert result["stats"]["received"] == 2
    assert result["stats"]["invalid_dropped"] == 0
    assert result["stats"]["unique"] == 1
    assert result["clients"][0]["phone"] == "+79991234567"
    assert result["clients"][0]["amount"] == 2500


def test_process_orders_idempotent_for_same_input():
    data = [
        {"id": 1, "name": "A", "phone": "8 (999) 123-45-67", "email": "a@example.com", "amount": 1000, "created_at": "2026-10-01T10:00:00Z"},
        {"id": 2, "name": "A2", "phone": "89991234567", "email": "a2@example.com", "amount": 5000, "created_at": "2026-10-02T11:00:00Z"},
        {"id": 3, "name": "B", "phone": "8 916 000 00 01", "email": "b@example.com", "amount": 200, "created_at": "2026-10-03T09:00:00Z"},
    ]

    first = process_orders(data)
    second = process_orders(data)

    assert first == second
    assert len(first["clients"]) == 2
    assert {client["phone"] for client in first["clients"]} == {"+79160000001", "+79991234567"}
