# DataPersistence PoC

**SampleOrderSystem** 프로젝트의 데이터 영속성 처리 검증 모듈입니다.  
JSON 파일을 저장소 백엔드로 사용하는 CRUD 구조를 TDD로 구현합니다.

---

## 프로젝트 배경

가상의 반도체 회사 **S-Semi**의 시료 생산주문관리 시스템(`SampleOrderSystem`) 개발을 위한 4개의 PoC 모듈 중 하나입니다.

| 모듈 | 역할 |
|------|------|
| ConsoleMVC | 콘솔 기반 MVC 패턴 구현 |
| **DataPersistence** | **데이터 저장·불러오기 처리 (이 저장소)** |
| DataMonitor | 데이터 모니터링/조회 |
| DummyDataGenerator | 테스트용 더미 데이터 생성 |

이 PoC의 목표는 JSON 기반 데이터 영속성 구조를 검증하는 것으로, 비즈니스 로직(상태 전이, 생산 스케줄링 등)은 포함하지 않습니다.

---

## 기술 스택

- **언어**: Python 3.10+
- **테스트**: pytest, pytest-cov
- **저장 형식**: JSON 파일

---

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install pytest pytest-cov
```

### 2. 전체 테스트 실행 (커버리지 포함)

```bash
pytest
```

`pytest.ini`에 `--cov=src --cov-report=term-missing`이 기본 옵션으로 설정되어 있어, 커버리지 리포트가 자동으로 출력됩니다.

### 3. 단일 테스트 파일 실행

```bash
pytest tests/test_sample_repository.py -v
pytest tests/test_order_repository.py -v
```

### 4. 단일 테스트 함수 실행

```bash
pytest tests/test_sample_repository.py::test_save_returns_saved_sample -v
```

---

## 프로젝트 구조

```
DataPersistence-YoonChangheum-22094435/
├── src/
│   ├── repository.py          # 추상 Repository 인터페이스 (OCP 기반)
│   ├── json_repository.py     # 범용 JSON CRUD 구현체
│   └── order_repository.py    # Order 특화 저장소 (상태 검증 + 상태별 조회)
├── tests/
│   ├── test_sample_repository.py   # Sample CRUD 테스트 (14개)
│   └── test_order_repository.py    # Order CRUD 테스트 (19개)
├── agents/                    # Claude Code 서브에이전트 정의
├── PRD.md                     # 요구사항 문서 및 Phase 진행 현황
├── CLAUDE.md                  # Claude Code 작업 가이드
├── pytest.ini                 # pytest 기본 옵션
└── .gitignore
```

---

## 아키텍처

### 클래스 계층 구조

```
Repository (ABC)
│  ← 저장소 공통 인터페이스 정의 (OCP 확장 기반)
│
└── JsonRepository(Repository)
│      ← JSON 파일 기반 범용 CRUD 구현
│      ← id_key 파라미터로 엔티티 종류에 무관하게 사용 가능
│
└── OrderJsonRepository(JsonRepository)
       ← Order 특화 저장소
       ← status 유효성 검증, find_by_status 추가
```

**OCP(Open/Closed Principle) 적용:**  
새로운 저장 백엔드(예: `CsvRepository`, `InMemoryRepository`)는 `Repository` 인터페이스만 구현하면 기존 코드를 전혀 수정하지 않고 추가할 수 있습니다.  
Order 이외의 도메인 엔티티(예: `SampleRepository`)는 `JsonRepository`를 그대로 재사용합니다.

---

## 도메인 엔티티

### Sample (시료)

반도체 시료 정보를 나타내는 엔티티입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `sample_id` | str | 시료 고유 ID (식별자) |
| `name` | str | 시료 이름 |
| `avg_production_time` | int | 평균 생산 시간 (단위: 시간) |
| `yield_rate` | float | 수율 (0.0 ~ 1.0, 예: 0.9 = 90%) |

```python
sample = {
    "sample_id": "S001",
    "name": "Alpha-300",
    "avg_production_time": 48,
    "yield_rate": 0.92,
}
```

### Order (주문)

시료 생산 주문 정보를 나타내는 엔티티입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `order_id` | str | 주문 고유 ID (식별자) |
| `sample_id` | str | 주문 대상 시료 ID |
| `customer` | str | 고객명 |
| `quantity` | int | 주문 수량 |
| `status` | str | 주문 상태 (아래 참조) |

**유효한 주문 상태:**

| 상태 | 설명 |
|------|------|
| `RESERVED` | 주문 접수 |
| `REJECTED` | 주문 거절 |
| `PRODUCING` | 재고 부족으로 생산 중 |
| `CONFIRMED` | 출고 대기 중 |
| `RELEASE` | 출고 완료 |

유효하지 않은 `status` 값으로 `save` 또는 `update` 호출 시 `ValueError`가 발생합니다.

```python
order = {
    "order_id": "O001",
    "sample_id": "S001",
    "customer": "KAIST",
    "quantity": 10,
    "status": "RESERVED",
}
```

---

## API 레퍼런스

### `JsonRepository(file_path, id_key="sample_id")`

범용 JSON 파일 저장소입니다.

| 메서드 | 시그니처 | 설명 |
|--------|---------|------|
| `save` | `(entity: dict) → dict` | 엔티티 저장 후 반환 |
| `find_by_id` | `(entity_id: str) → dict \| None` | ID로 단건 조회, 없으면 `None` |
| `find_all` | `() → list` | 전체 목록 반환 |
| `update` | `(entity_id: str, updates: dict) → dict \| None` | 부분 수정 후 반환, 없으면 `None` |
| `delete` | `(entity_id: str) → bool` | 삭제 성공 여부 반환 |

```python
from src.json_repository import JsonRepository

repo = JsonRepository("samples.json")

# 저장
repo.save({"sample_id": "S001", "name": "Alpha-300", "avg_production_time": 48, "yield_rate": 0.92})

# 조회
sample = repo.find_by_id("S001")   # → dict or None
samples = repo.find_all()           # → list

# 수정
updated = repo.update("S001", {"name": "Alpha-300-Rev2"})

# 삭제
deleted = repo.delete("S001")       # → True or False
```

### `OrderJsonRepository(file_path)`

Order 엔티티 전용 저장소입니다. `JsonRepository`의 모든 메서드를 상속하며 아래가 추가됩니다.

| 메서드 | 시그니처 | 설명 |
|--------|---------|------|
| `save` | `(entity: dict) → dict` | status 유효성 검증 후 저장 |
| `update` | `(entity_id: str, updates: dict) → dict \| None` | status 유효성 검증 후 수정 |
| `find_by_status` | `(status: str) → list` | 주어진 상태의 주문 목록 반환 |

```python
from src.order_repository import OrderJsonRepository

repo = OrderJsonRepository("orders.json")

# 저장 (status 검증 포함)
repo.save({"order_id": "O001", "sample_id": "S001", "customer": "KAIST", "quantity": 10, "status": "RESERVED"})

# 상태별 조회
reserved = repo.find_by_status("RESERVED")   # → list
confirmed = repo.find_by_status("CONFIRMED")

# 유효하지 않은 status → ValueError
repo.save({..., "status": "INVALID"})   # raises ValueError
```

---

## 테스트 현황

```
tests/test_sample_repository.py   14개 테스트
tests/test_order_repository.py    19개 테스트
─────────────────────────────────────────────
합계                               33개 테스트
커버리지                           100%
```

### 테스트 범위

- **Create**: 저장 후 반환값 검증, 복수 저장 시 격리
- **Read**: ID 조회(존재/비존재), 전체 목록, 상태별 목록
- **Update**: 부분 수정, 미존재 ID 처리, 타 엔티티 영향 없음
- **Delete**: 삭제 성공/실패, 타 엔티티 영향 없음
- **Persistence**: 저장소 객체 재생성 후 데이터 유지 확인
- **Validation**: 유효하지 않은 status 값 예외 처리
- **OCP**: `isinstance(repo, Repository)` 인터페이스 구현 확인

---

## 개발 방법론

### TDD (Test-Driven Development)

모든 기능은 **Red → Green → Refactor** 사이클로 구현되었습니다.

```
Red     : 실패하는 테스트 먼저 작성 → 사용자 승인
Green   : 테스트를 통과하는 최소 구현 → 사용자 승인
Refactor: OCP/SOLID 적용, 가독성 개선 → 사용자 승인 → Git Push
```

### Phase 진행 이력

| Phase | 내용 | 테스트 수 | 커버리지 |
|-------|------|-----------|---------|
| Phase 1 | Sample CRUD + 추상 Repository 인터페이스 도입 | 14개 | 100% |
| Phase 2 | Order CRUD + status 검증 + find_by_status | 33개 | 100% |

---

## 향후 확장 방법

새로운 저장 백엔드를 추가하려면 `Repository`를 구현하기만 하면 됩니다.  
기존 코드(`JsonRepository`, `OrderJsonRepository`)는 수정 불필요합니다.

```python
# 예시: 인메모리 저장소 (테스트용)
from src.repository import Repository

class InMemoryRepository(Repository):
    def __init__(self):
        self._store = {}

    def save(self, entity):
        ...
    # find_by_id, find_all, update, delete 구현
```
