import pytest
from src.order_repository import OrderJsonRepository
from src.repository import Repository

VALID_STATUSES = {"RESERVED", "REJECTED", "PRODUCING", "CONFIRMED", "RELEASE"}


@pytest.fixture
def repo(tmp_path):
    return OrderJsonRepository(str(tmp_path / "orders.json"))


@pytest.fixture
def order():
    return {
        "order_id": "O001",
        "sample_id": "S001",
        "customer": "KAIST",
        "quantity": 10,
        "status": "RESERVED",
    }


# ── Create ──────────────────────────────────────────────────────────────────

def test_save_returns_saved_order(repo, order):
    result = repo.save(order)
    assert result["order_id"] == "O001"
    assert result["sample_id"] == "S001"
    assert result["customer"] == "KAIST"
    assert result["quantity"] == 10
    assert result["status"] == "RESERVED"


def test_save_multiple_orders_without_overwrite(repo, order):
    repo.save(order)
    second = {**order, "order_id": "O002", "customer": "SNU"}
    repo.save(second)
    assert len(repo.find_all()) == 2


def test_save_raises_value_error_when_status_is_invalid(repo, order):
    order["status"] = "INVALID_STATUS"
    with pytest.raises(ValueError):
        repo.save(order)


# ── Read ────────────────────────────────────────────────────────────────────

def test_find_by_id_returns_order_when_exists(repo, order):
    repo.save(order)
    result = repo.find_by_id("O001")
    assert result is not None
    assert result["order_id"] == "O001"


def test_find_by_id_returns_none_when_not_exists(repo):
    result = repo.find_by_id("NONEXISTENT")
    assert result is None


def test_find_all_returns_empty_list_when_no_data(repo):
    assert repo.find_all() == []


def test_find_all_returns_all_saved_orders(repo, order):
    repo.save(order)
    repo.save({**order, "order_id": "O002", "customer": "SNU"})
    result = repo.find_all()
    assert len(result) == 2
    ids = {o["order_id"] for o in result}
    assert ids == {"O001", "O002"}


# ── find_by_status ───────────────────────────────────────────────────────────

def test_find_by_status_returns_matching_orders(repo, order):
    repo.save(order)
    repo.save({**order, "order_id": "O002", "status": "CONFIRMED"})
    result = repo.find_by_status("RESERVED")
    assert len(result) == 1
    assert result[0]["order_id"] == "O001"


def test_find_by_status_returns_empty_when_no_match(repo, order):
    repo.save(order)
    result = repo.find_by_status("PRODUCING")
    assert result == []


def test_find_by_status_excludes_other_statuses(repo, order):
    for i, status in enumerate(["RESERVED", "CONFIRMED", "PRODUCING"]):
        repo.save({**order, "order_id": f"O00{i+1}", "status": status})
    result = repo.find_by_status("CONFIRMED")
    assert len(result) == 1
    assert result[0]["status"] == "CONFIRMED"


# ── Update ───────────────────────────────────────────────────────────────────

def test_update_modifies_order_and_returns_updated(repo, order):
    repo.save(order)
    updated = repo.update("O001", {"status": "CONFIRMED", "quantity": 20})
    assert updated is not None
    assert updated["status"] == "CONFIRMED"
    assert updated["quantity"] == 20
    assert updated["order_id"] == "O001"


def test_update_returns_none_when_order_not_exists(repo):
    result = repo.update("NONEXISTENT", {"status": "CONFIRMED"})
    assert result is None


def test_update_does_not_affect_other_orders(repo, order):
    repo.save(order)
    repo.save({**order, "order_id": "O002", "customer": "SNU"})
    repo.update("O001", {"status": "CONFIRMED"})
    other = repo.find_by_id("O002")
    assert other["status"] == "RESERVED"


def test_update_raises_value_error_when_status_is_invalid(repo, order):
    repo.save(order)
    with pytest.raises(ValueError):
        repo.update("O001", {"status": "WRONG"})


# ── Delete ───────────────────────────────────────────────────────────────────

def test_delete_removes_order_and_returns_true(repo, order):
    repo.save(order)
    assert repo.delete("O001") is True
    assert repo.find_by_id("O001") is None


def test_delete_returns_false_when_order_not_exists(repo):
    assert repo.delete("NONEXISTENT") is False


def test_delete_does_not_affect_other_orders(repo, order):
    repo.save(order)
    repo.save({**order, "order_id": "O002", "customer": "SNU"})
    repo.delete("O001")
    assert repo.find_by_id("O002") is not None
    assert len(repo.find_all()) == 1


# ── Persistence ───────────────────────────────────────────────────────────────

def test_data_persists_after_repository_recreation(tmp_path, order):
    file_path = str(tmp_path / "orders.json")
    repo1 = OrderJsonRepository(file_path)
    repo1.save(order)

    repo2 = OrderJsonRepository(file_path)
    result = repo2.find_by_id("O001")
    assert result is not None
    assert result["customer"] == "KAIST"


# ── OCP 준수 검증 ──────────────────────────────────────────────────────────────

def test_order_repository_is_a_repository(repo):
    assert isinstance(repo, Repository)
