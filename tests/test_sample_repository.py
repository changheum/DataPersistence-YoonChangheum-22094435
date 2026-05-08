import os
import pytest
from src.json_repository import JsonRepository
from src.repository import Repository


@pytest.fixture
def repo(tmp_path):
    """각 테스트마다 독립된 임시 JSON 파일을 사용하는 저장소."""
    file_path = tmp_path / "samples.json"
    return JsonRepository(str(file_path))


@pytest.fixture
def sample():
    return {
        "sample_id": "S001",
        "name": "Alpha-300",
        "avg_production_time": 48,
        "yield_rate": 0.92,
    }


# ── Create ──────────────────────────────────────────────────────────────────

def test_save_returns_saved_sample(repo, sample):
    result = repo.save(sample)
    assert result["sample_id"] == "S001"
    assert result["name"] == "Alpha-300"
    assert result["avg_production_time"] == 48
    assert result["yield_rate"] == 0.92


def test_save_multiple_samples_without_overwrite(repo, sample):
    repo.save(sample)
    second = {**sample, "sample_id": "S002", "name": "Beta-500"}
    repo.save(second)
    assert len(repo.find_all()) == 2


# ── Read ────────────────────────────────────────────────────────────────────

def test_find_by_id_returns_sample_when_exists(repo, sample):
    repo.save(sample)
    result = repo.find_by_id("S001")
    assert result is not None
    assert result["sample_id"] == "S001"


def test_find_by_id_returns_none_when_not_exists(repo):
    result = repo.find_by_id("NONEXISTENT")
    assert result is None


def test_find_all_returns_empty_list_when_no_data(repo):
    result = repo.find_all()
    assert result == []


def test_find_all_returns_all_saved_samples(repo, sample):
    repo.save(sample)
    repo.save({**sample, "sample_id": "S002", "name": "Beta-500"})
    result = repo.find_all()
    assert len(result) == 2
    ids = {s["sample_id"] for s in result}
    assert ids == {"S001", "S002"}


# ── Update ───────────────────────────────────────────────────────────────────

def test_update_modifies_sample_and_returns_updated(repo, sample):
    repo.save(sample)
    updated = repo.update("S001", {"name": "Alpha-300-Rev2", "yield_rate": 0.95})
    assert updated is not None
    assert updated["name"] == "Alpha-300-Rev2"
    assert updated["yield_rate"] == 0.95
    assert updated["sample_id"] == "S001"


def test_update_returns_none_when_sample_not_exists(repo):
    result = repo.update("NONEXISTENT", {"name": "Ghost"})
    assert result is None


def test_update_does_not_affect_other_samples(repo, sample):
    repo.save(sample)
    repo.save({**sample, "sample_id": "S002", "name": "Beta-500"})
    repo.update("S001", {"name": "Alpha-300-Rev2"})
    other = repo.find_by_id("S002")
    assert other["name"] == "Beta-500"


# ── Delete ───────────────────────────────────────────────────────────────────

def test_delete_removes_sample_and_returns_true(repo, sample):
    repo.save(sample)
    result = repo.delete("S001")
    assert result is True
    assert repo.find_by_id("S001") is None


def test_delete_returns_false_when_sample_not_exists(repo):
    result = repo.delete("NONEXISTENT")
    assert result is False


def test_delete_does_not_affect_other_samples(repo, sample):
    repo.save(sample)
    repo.save({**sample, "sample_id": "S002", "name": "Beta-500"})
    repo.delete("S001")
    assert repo.find_by_id("S002") is not None
    assert len(repo.find_all()) == 1


# ── Persistence ───────────────────────────────────────────────────────────────

def test_data_persists_after_repository_recreation(tmp_path, sample):
    """저장 후 저장소 객체를 새로 만들어도 데이터가 유지되어야 함."""
    file_path = str(tmp_path / "samples.json")
    repo1 = JsonRepository(file_path)
    repo1.save(sample)

    repo2 = JsonRepository(file_path)
    result = repo2.find_by_id("S001")
    assert result is not None
    assert result["name"] == "Alpha-300"


# ── OCP 준수 검증 ──────────────────────────────────────────────────────────────

def test_json_repository_is_a_repository(repo):
    """JsonRepository는 Repository 인터페이스를 구현해야 한다 (OCP)."""
    assert isinstance(repo, Repository)
